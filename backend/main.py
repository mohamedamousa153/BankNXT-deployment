from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import os

import models, schemas
from database import engine, get_db

from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
import ldap_service

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ")[1]
        
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized: No bearer token provided.")
        
    user = db.query(models.User).filter(models.User.session_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token.")
        
    return user


# Create DB tables
models.Base.metadata.create_all(bind=engine)

def seed_users(db: Session):
    if not db.query(models.User).first():
        admin = models.User(employee_no="admin", name="System Administrator", password="admin", is_admin=True)
        emp = models.User(employee_no="2469", name="Mohamed Ayman Mousa", password="password", is_admin=False)
        db.add(admin)
        db.add(emp)
        db.commit()

from apscheduler.schedulers.background import BackgroundScheduler
from excel_service import generate_overtime_excel, send_email_with_excel
from datetime import datetime
import calendar

def scheduled_overtime_job():
    print("[SCHEDULER] Running scheduled overtime job...")
    # Run for previous month
    now = datetime.now()
    if now.month == 1:
        target_month = 12
        target_year = now.year - 1
    else:
        target_month = now.month - 1
        target_year = now.year

    db = next(get_db())
    excel_path = generate_overtime_excel(db, target_month, target_year)
    if excel_path:
        send_email_with_excel(excel_path, target_month, target_year)
    else:
        print(f"[SCHEDULER] No overtime records found for {target_month}/{target_year}.")

scheduler = BackgroundScheduler()
# Run on the 5th of every month at 9:00 AM
scheduler.add_job(scheduled_overtime_job, 'cron', day=5, hour=9, minute=0)

app = FastAPI(title="Overtime & WFH Dashboard API")

@app.on_event("startup")
def start_scheduler():
    db = next(get_db())
    seed_users(db)
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_subordinate_user_employee_nos(db, manager_dn: str, visited=None):
    if visited is None:
        visited = set()
    if not manager_dn or manager_dn in visited:
        return []
    visited.add(manager_dn)
    
    subordinates = []
    direct_reports = db.query(models.User).filter(models.User.manager_dn == manager_dn).all()
    for report in direct_reports:
        if report.employee_no not in subordinates:
            subordinates.append(report.employee_no)
        if report.user_dn:
            subs = get_subordinate_user_employee_nos(db, report.user_dn, visited)
            for s in subs:
                if s not in subordinates:
                    subordinates.append(s)
    return subordinates

def get_allowed_employee_nos(db, current_user):
    if current_user.role == "system_admin":
        return None
    allowed = [current_user.employee_no]
    if current_user.user_dn:
        config = db.query(models.LDAPSettings).first()
        if config and config.enabled:
            # Source of truth: AD directly
            print(f"DEBUG: Resolving hierarchy from AD for USER DN: {current_user.user_dn}")
            ad_subs = ldap_service.get_ad_subordinates_recursive(current_user.user_dn, config, db)
            print(f"DEBUG: RECURSIVE SUBORDINATES FOUND: {len(ad_subs)}")
            allowed.extend(ad_subs)
        else:
            # Fallback if AD disabled
            subs = get_subordinate_user_employee_nos(db, current_user.user_dn)
            allowed.extend(subs)
            
    # Ensure uniqueness
    allowed = list(set(allowed))
    print(f"DEBUG: ALLOWED EMPLOYEE NUMBERS: {allowed}")
    return allowed

# --- AUTH ENDPOINTS ---
@app.post("/api/login", response_model=schemas.User)
def login(creds: schemas.UserLogin, db: Session = Depends(get_db)):
    import secrets
    config = db.query(models.LDAPSettings).first()
    
    # 1. Check if it's a valid local System Administrator
    local_admin = db.query(models.User).filter(
        models.User.employee_no == creds.employee_no,
        models.User.password == creds.password,
        models.User.role == "system_admin"
    ).first()
    
    if local_admin:
        local_admin.session_token = secrets.token_hex(32)
        db.commit()
        db.refresh(local_admin)
        return local_admin
    
    # 2. Else use LDAP if enabled
    if config and config.enabled:
        # LDAP Mode
        auth_result = ldap_service.authenticate_user(creds.employee_no, creds.password, config)
        if not auth_result["success"]:
            raise HTTPException(status_code=401, detail=auth_result["message"])
            
                # Note: Role is stripped down. Everyone is an employee unless they are admin.
        # Manager hierarchy is driven by AD. We keep role='employee'.
        resolved_role = "employee"
        if creds.employee_no == "admin":
            resolved_role = "system_admin"
        
        # Determine top-level log prints
        print(f"LDAP USER: {creds.employee_no}")
        print(f"USER DN: {auth_result.get('user_dn')}")
        print(f"MANAGER DN: {auth_result.get('manager_dn')}")
        print(f"MANAGER NAME: {auth_result.get('manager_name')}")

        # Sync LDAP Identity to local DB for foreign keys
        
        user = db.query(models.User).filter(models.User.employee_no == auth_result["employee_no"]).first()
        if not user:
            user = models.User(
                employee_no=auth_result["employee_no"],
                name=auth_result["name"],
                password="ldap_managed",
                role=resolved_role,
                team_id=None,
                manager_dn=auth_result.get("manager_dn"),
                manager_name=auth_result.get("manager_name"),
                user_dn=auth_result.get('user_dn')
            )
            db.add(user)
        else:
            user.name = auth_result["name"]
            user.role = resolved_role
            user.team_id = None
            user.manager_dn = auth_result.get("manager_dn")
            user.manager_name = auth_result.get("manager_name")
            user.user_dn = auth_result.get('user_dn')
        import secrets
        user.session_token = secrets.token_hex(32)
        db.commit()
        db.refresh(user)
        return user
        
    else:
        # Local Mode
        user = db.query(models.User).filter(
            models.User.employee_no == creds.employee_no,
            models.User.password == creds.password
        ).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        import secrets
        user.session_token = secrets.token_hex(32)
        db.commit()
        db.refresh(user)
        return user

# --- OVERTIME ENDPOINTS ---

@app.post("/api/overtime", response_model=schemas.Overtime)
def create_overtime(record: schemas.OvertimeCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    start_dt = datetime.fromisoformat(record.start_datetime)
    end_dt = datetime.fromisoformat(record.end_datetime)
    
    if end_dt <= start_dt:
        raise HTTPException(status_code=400, detail="End datetime must be after Start datetime")
        
    duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
    
    # Enforce current user identity
    record_dict = record.dict()
    record_dict['employee_no'] = current_user.employee_no
    record_dict['name'] = current_user.name
    
    db_record = models.OvertimeRecord(
        **record_dict,
        duration_hours=duration_hours,
        status="Pending Approval",
        created_at=datetime.now().isoformat()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.put("/api/overtime/{record_id}", response_model=schemas.Overtime)
def update_overtime(record_id: int, update_data: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_record = db.query(models.OvertimeRecord).filter(models.OvertimeRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to access this record.")

        
    if "status" in update_data and update_data["status"] in ["Approved", "Rejected"]:
        db_record.approval_date = datetime.now().isoformat()
        db_record.approved_by = update_data.get("approved_by", "Admin")
        
    for key, value in update_data.items():
        if hasattr(db_record, key):
            setattr(db_record, key, value)
            
    db.commit()
    db.refresh(db_record)
    return db_record

@app.delete("/api/overtime/{record_id}")
def delete_overtime(record_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_record = db.query(models.OvertimeRecord).filter(models.OvertimeRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to delete this record.")
    
    db.delete(db_record)
    db.commit()
    return {"message": "Deleted successfully"}

@app.get("/api/overtime", response_model=List[schemas.Overtime])
def get_overtimes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.OvertimeRecord)
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None:
        query = query.filter(models.OvertimeRecord.employee_no.in_(allowed_nos))
    return query.order_by(models.OvertimeRecord.start_datetime.desc()).all()

# --- ADMIN ENDPOINTS ---

@app.post("/api/admin/trigger-email")
def trigger_excel_email(db: Session = Depends(get_db)):
    # Run for previous month manually
    now = datetime.now()
    if now.month == 1:
        target_month = 12
        target_year = now.year - 1
    else:
        target_month = now.month - 1
        target_year = now.year

    excel_path = generate_overtime_excel(db, target_month, target_year)
    if excel_path:
        # In a real app this would send the email. 
        # For now, it just generates the file.
        return {"message": f"Success! Generated {excel_path} and sent email.", "file": excel_path}
    else:
        raise HTTPException(status_code=404, detail=f"No overtime records found for {target_month}/{target_year}.")
@app.get("/api/admin/settings", response_model=schemas.Settings)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(models.SystemSettings).first()
    if not settings:
        settings = models.SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.put("/api/admin/settings", response_model=schemas.Settings)
def update_settings(settings_in: schemas.Settings, db: Session = Depends(get_db)):
    settings = db.query(models.SystemSettings).first()
    if not settings:
        settings = models.SystemSettings()
        db.add(settings)
    settings.admin_email = settings_in.admin_email
    settings.max_wfh_days = settings_in.max_wfh_days
    db.commit()
    db.refresh(settings)
    return settings

@app.post("/api/wfh", response_model=schemas.WFH)
def create_wfh(record: schemas.WFHCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    import json
    from datetime import datetime, timedelta
    
    settings = db.query(models.SystemSettings).first()
    max_days = settings.max_wfh_days if settings else 2

    requested_dates = []
    
    # 1. Parse requested dates
    if record.selected_dates:
        requested_dates = json.loads(record.selected_dates)
        if len(requested_dates) == 0:
            raise HTTPException(status_code=400, detail="Please select at least one day.")
    else:
        if not record.date:
            raise HTTPException(status_code=400, detail="Date is required")
        if record.end_date and record.end_date < record.date:
            raise HTTPException(status_code=400, detail="End date must be after Start date")
        
        # Expand date range to discrete days
        current_date = record.date
        end = record.end_date if record.end_date else record.date
        while current_date <= end:
            requested_dates.append(current_date.isoformat())
            current_date += timedelta(days=1)
            
    # 2. Fetch all active existing WFH records for the employee
    active_statuses = ["Pending Approval", "Approved"]
    existing_records = db.query(models.WFHRecord).filter(
        models.WFHRecord.employee_no == record.employee_no,
        models.WFHRecord.status.in_(active_statuses)
    ).all()
    
    existing_dates = set()
    weekly_counts = {}
    
    for r in existing_records:
        r_dates = []
        if r.selected_dates:
            r_dates = json.loads(r.selected_dates)
        else:
            if not r.date: continue
            cur = r.date
            ed = r.end_date if r.end_date else r.date
            while cur <= ed:
                r_dates.append(cur.isoformat())
                cur += timedelta(days=1)
                
        for d in r_dates:
            existing_dates.add(d)
            # Calculate ISO week string (e.g. "2026-W36")
            dt = datetime.fromisoformat(d).date() if 'T' in d else datetime.strptime(d, "%Y-%m-%d").date()
            shift = (dt.weekday() + 1) % 7
            week_start = dt - timedelta(days=shift)
            week_key = week_start.isoformat()
            weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1

    # 3. Validation: Duplicate Dates
    for d in requested_dates:
        dt = datetime.fromisoformat(d).date() if 'T' in d else datetime.strptime(d, "%Y-%m-%d").date()
        if dt.weekday() in [4, 5]:
            raise HTTPException(status_code=400, detail="Weekend days (Friday/Saturday) cannot be selected.")
    for d in requested_dates:
        if d in existing_dates:
            raise HTTPException(status_code=400, detail="Duplicate WFH date.")
            
    # 4. Validation: Weekly Allowance
    # We add requested dates to weekly counts and check
    for d in requested_dates:
        dt = datetime.fromisoformat(d).date() if 'T' in d else datetime.strptime(d, "%Y-%m-%d").date()
        shift = (dt.weekday() + 1) % 7
        week_start = dt - timedelta(days=shift)
        week_key = week_start.isoformat()
        weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1
        if weekly_counts[week_key] > max_days:
            raise HTTPException(status_code=400, detail=f"Maximum {max_days} WFH days per week.")

    # Calculate year and week_num for legacy storage based on first date
    first_date = datetime.fromisoformat(requested_dates[0]).date() if 'T' in requested_dates[0] else datetime.strptime(requested_dates[0], "%Y-%m-%d").date()
    y, w, _ = first_date.isocalendar()

    # Enforce current user identity
    record_dict = record.dict()
    record_dict['employee_no'] = current_user.employee_no
    record_dict['name'] = current_user.name
    
    db_record = models.WFHRecord(
        **record_dict,
        week_number=w,
        year=y,
        status="Pending Approval", 
        created_at=datetime.now().isoformat()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.put("/api/wfh/{record_id}", response_model=schemas.WFH)
def update_wfh(record_id: int, update_data: dict, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_record = db.query(models.WFHRecord).filter(models.WFHRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to access this record.")

    
    if "status" in update_data and update_data["status"] in ["Approved", "Rejected", "Returned"]:
        db_record.approval_date = datetime.now().isoformat()
        db_record.approved_by = update_data.get("approved_by", "Admin")
        
    for key, value in update_data.items():
        if hasattr(db_record, key):
            setattr(db_record, key, value)
            
    if "status" in update_data:
        settings = db.query(models.SystemSettings).first()
        email = settings.admin_email if settings else "admin@banknxt.com"
        print(f"[NOTIFICATION] WFH {record_id} status changed to {update_data['status']}. Sent to {email}")
            
    db.commit()
    db.refresh(db_record)
    return db_record

@app.delete("/api/wfh/{record_id}")
def delete_wfh(record_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_record = db.query(models.WFHRecord).filter(models.WFHRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to delete this record.")
    db.delete(db_record)
    db.commit()
    return {"message": "Deleted successfully"}

from typing import Optional

@app.get("/api/wfh")
def get_wfh_records(
    current_user: models.User = Depends(get_current_user),
    employee_no: Optional[str] = None, 
    page: Optional[int] = None, 
    page_size: Optional[int] = 10, 
    db: Session = Depends(get_db)
):
    query = db.query(models.WFHRecord)
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None:
        query = query.filter(models.WFHRecord.employee_no.in_(allowed_nos))
        
    if employee_no:
        if allowed_nos is not None and employee_no not in allowed_nos:
            raise HTTPException(status_code=403, detail="Forbidden")
        query = query.filter(models.WFHRecord.employee_no == employee_no)
    
    query = query.order_by(models.WFHRecord.id.desc())
    
    if page is not None:
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    else:
        return query.all()

# --- EXPORT ENDPOINTS ---
import openpyxl

@app.get("/api/export/overtime")
def export_overtime(db: Session = Depends(get_db)):
    records = db.query(models.OvertimeRecord).all()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Overtime Export"
    
    headers = ["Request ID", "Employee Name", "Employee ID", "Department", "Start DateTime", "End DateTime", "Total Hours", "Assigned Work", "Status", "Approved By", "Approval Date"]
    ws.append(headers)
    
    for r in records:
        ws.append([
            r.id, r.name, r.employee_no, r.department or "", 
            r.start_datetime.replace("T", " "), r.end_datetime.replace("T", " "), 
            round(r.duration_hours, 2) if r.duration_hours else 0, 
            r.assigned_work, r.status, r.approved_by or "", r.approval_date or ""
        ])
        
    os.makedirs("exports", exist_ok=True)
    path = "exports/Overtime_Export.xlsx"
    wb.save(path)
    return FileResponse(path, filename="Overtime_Export.xlsx")

@app.get("/api/export/wfh")
def export_wfh(db: Session = Depends(get_db)):
    import json
    records = db.query(models.WFHRecord).all()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "WFH Export"
    
    headers = ["Request ID", "Employee Name", "Employee ID", "Department", "WFH Date", "Start Time", "End Time", "WFH Type", "Reason", "Status", "Approved By", "Approval Date"]
    ws.append(headers)
    
    for r in records:
        if r.selected_dates:
            dates = json.loads(r.selected_dates)
            for d in dates:
                ws.append([
                    r.id, r.name, r.employee_no, r.department or "",
                    d, r.start_time or "", r.end_time or "",
                    r.wfh_type, r.reason or "", r.status, r.approved_by or "", r.approval_date or ""
                ])
        else:
            # legacy handling
            ws.append([
                r.id, r.name, r.employee_no, r.department or "",
                str(r.date), r.start_time or "", r.end_time or "",
                r.wfh_type, r.reason or "", r.status, r.approved_by or "", r.approval_date or ""
            ])
            if r.end_date and r.end_date != r.date:
                ws.append([
                    r.id, r.name, r.employee_no, r.department or "",
                    str(r.end_date), r.start_time or "", r.end_time or "",
                    r.wfh_type, r.reason or "", r.status, r.approved_by or "", r.approval_date or ""
                ])
        
    os.makedirs("exports", exist_ok=True)
    path = "exports/WFH_Export.xlsx"
    wb.save(path)
    return FileResponse(path, filename="WFH_Export.xlsx")


@app.get("/api/teams")
def get_teams(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    return [{"id": t.id, "name": t.name, "ldap_group_id": t.ldap_group_id} for t in teams]

@app.get("/api/users")
def get_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.User)
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None:
        query = query.filter(models.User.employee_no.in_(allowed_nos))
    users = query.all()
    return [{"employee_no": u.employee_no, "name": u.name,} for u in users]


@app.get("/api/users/hierarchy")
def get_user_hierarchy(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Calculate hierarchy
    if current_user.role == "system_admin":
        return {"subordinates": []} # Or all users if admin dashboard needed
        
    subs = []
    if current_user.user_dn:
        sub_nos = get_subordinate_user_employee_nos(db, current_user.user_dn)
        if sub_nos:
            users = db.query(models.User).filter(models.User.employee_no.in_(sub_nos)).all()
            for u in users:
                subs.append({"employee_no": u.employee_no, "name": u.name, "manager_name": u.manager_name})
                
    # Direct reports are those whose manager_dn == current_user.user_dn
    direct_reports = []
    if current_user.user_dn:
        dr = db.query(models.User).filter(models.User.manager_dn == current_user.user_dn).all()
        direct_reports = [{"employee_no": u.employee_no, "name": u.name} for u in dr]
        
    return {
        "direct_reports": direct_reports,
        "all_subordinates": subs
    }

@app.get("/api/admin/ldap/config", response_model=schemas.LDAPSettingsResponse)
def get_ldap_config(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden: Only System Administrators can access LDAP settings.")
        
    config = db.query(models.LDAPSettings).first()
    if not config:
        config = models.LDAPSettings()
        db.add(config)
        db.commit()
        db.refresh(config)
        
    # Mask password
    resp = schemas.LDAPSettingsResponse(**{k: getattr(config, k) for k in config.__table__.columns.keys()})
    if resp.bind_password:
        resp.bind_password = "********"
    return resp

@app.put("/api/admin/ldap/config", response_model=schemas.LDAPSettingsResponse)
def update_ldap_config(settings: schemas.LDAPSettingsCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden: Only System Administrators can modify LDAP settings.")
        
    config = db.query(models.LDAPSettings).first()
    if not config:
        config = models.LDAPSettings()
        db.add(config)
        
    update_data = settings.dict(exclude_unset=True)
    
    # Don't overwrite password if it's the masked value
    if update_data.get("bind_password") == "********":
        update_data.pop("bind_password")
        
    for key, value in update_data.items():
        setattr(config, key, value)
        
    db.commit()
    db.refresh(config)
    
    resp = schemas.LDAPSettingsResponse(**{k: getattr(config, k) for k in config.__table__.columns.keys()})
    if resp.bind_password:
        resp.bind_password = "********"
    return resp

@app.post("/api/admin/ldap/test-connection")
def test_ldap_connection(settings: schemas.LDAPSettingsCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "system_admin":
        raise HTTPException(status_code=403, detail="Forbidden: Only System Administrators can test LDAP connection.")
        
    # If the password is the masked string, grab the real one from DB to test
    password = settings.bind_password
    if password == "********":
        config = db.query(models.LDAPSettings).first()
        if config:
            password = config.bind_password
            
    # Test socket connection using our ldap_service
    result = ldap_service.test_ldap_connection(settings.server_url, settings.port, settings.timeout, settings.bind_username, password, settings.use_tls)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
        
    return {"message": result["message"]}
# Serve Frontend

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/{catchall:path}")
def serve_react_app(catchall: str):
    return FileResponse("../frontend/index.html")




