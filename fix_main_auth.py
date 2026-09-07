import re

with open("backend/main.py", "r") as f:
    content = f.read()

# 1. Fix get_overtimes
old_get_overtimes = """@app.get("/api/overtime", response_model=List[schemas.Overtime])
def get_overtimes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.OvertimeRecord)
    if current_user.role == "manager":
        query = query.filter(models.OvertimeRecord.team_id == current_user.team_id)
    elif current_user.role != "system_admin":
        query = query.filter(models.OvertimeRecord.employee_no == current_user.employee_no)
    return query.order_by(models.OvertimeRecord.start_datetime.desc()).all()"""

new_get_overtimes = """@app.get("/api/overtime", response_model=List[schemas.Overtime])
def get_overtimes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.OvertimeRecord)
    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None:
        query = query.filter(models.OvertimeRecord.employee_no.in_(allowed_nos))
    return query.order_by(models.OvertimeRecord.start_datetime.desc()).all()"""

content = content.replace(old_get_overtimes, new_get_overtimes)

# 2. Fix update_overtime authorization
old_up_ot = """    req_user = current_user
    if req_user.role == "employee":
        if db_record.employee_no != req_user.employee_no:
            raise HTTPException(status_code=403, detail="Forbidden: You can only edit your own requests.")
            
    elif req_user.role == "manager":
        if db_record.team_id != req_user.team_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only edit requests for your assigned team.")"""

new_up_ot = """    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to access this record.")"""

content = content.replace(old_up_ot, new_up_ot)

# 3. Fix delete_overtime authorization
old_del_ot = """    req_user = current_user
    if req_user.role == "employee":
        if db_record.employee_no != req_user.employee_no:
            raise HTTPException(status_code=403, detail="Forbidden: You can only delete your own requests.")
            
    elif req_user.role == "manager":
        if db_record.team_id != req_user.team_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only delete requests for your assigned team.")"""

new_del_ot = """    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to delete this record.")"""
        
content = content.replace(old_del_ot, new_del_ot)

# 4. Fix update_wfh
old_up_wfh = """    req_user = current_user
    if req_user.role == "employee":
        if db_record.employee_no != req_user.employee_no:
            raise HTTPException(status_code=403, detail="Forbidden: You can only edit your own requests.")
            
    elif req_user.role == "manager":
        if db_record.team_id != req_user.team_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only edit requests for your assigned team.")"""

content = content.replace(old_up_wfh, new_up_ot) # They are identical

# 5. Fix delete_wfh
old_del_wfh = """    req_user = current_user
    if req_user.role == "employee":
        if db_record.employee_no != req_user.employee_no:
            raise HTTPException(status_code=403, detail="Forbidden: You can only delete your own requests.")
            
    elif req_user.role == "manager":
        if db_record.team_id != req_user.team_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only delete requests for your assigned team.")"""

content = content.replace(old_del_wfh, new_del_ot)

# Ensure users endpoint has hierarchy route
if "/api/users/hierarchy" not in content:
    hierarchy_endpoint = """
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
"""
    content = content.replace("@app.get(\"/api/admin/ldap/config\"", hierarchy_endpoint + "\n@app.get(\"/api/admin/ldap/config\"")

with open("backend/main.py", "w") as f:
    f.write(content)
