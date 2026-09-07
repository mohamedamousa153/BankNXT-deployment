import re

with open("backend/main.py", "r") as f:
    content = f.read()

# 1. Add hierarchy functions
hierarchy_funcs = """
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
        subs = get_subordinate_user_employee_nos(db, current_user.user_dn)
        allowed.extend(subs)
    return allowed
"""

content = content.replace("# --- AUTH ENDPOINTS ---", hierarchy_funcs + "\n# --- AUTH ENDPOINTS ---")

# 2. Refactor get_wfh_records
old_wfh = """    req_user = current_user
    if req_user.role == "manager":
        query = query.filter(models.WFHRecord.team_id == req_user.team_id)
    elif req_user.role != "system_admin":
        query = query.filter(models.WFHRecord.employee_no == req_user.employee_no)
            
    if employee_no:
        query = query.filter(models.WFHRecord.employee_no == employee_no)"""
new_wfh = """    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None:
        query = query.filter(models.WFHRecord.employee_no.in_(allowed_nos))
        
    if employee_no:
        if allowed_nos is not None and employee_no not in allowed_nos:
            raise HTTPException(status_code=403, detail="Forbidden")
        query = query.filter(models.WFHRecord.employee_no == employee_no)"""
content = content.replace(old_wfh, new_wfh)

# 3. Refactor get_overtime_records
old_ot = """    req_user = current_user
    if req_user.role == "manager":
        query = query.filter(models.OvertimeRecord.team_id == req_user.team_id)
    elif req_user.role != "system_admin":
        query = query.filter(models.OvertimeRecord.employee_no == req_user.employee_no)
            
    if employee_no:
        query = query.filter(models.OvertimeRecord.employee_no == employee_no)"""
new_ot = """    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None:
        query = query.filter(models.OvertimeRecord.employee_no.in_(allowed_nos))
        
    if employee_no:
        if allowed_nos is not None and employee_no not in allowed_nos:
            raise HTTPException(status_code=403, detail="Forbidden")
        query = query.filter(models.OvertimeRecord.employee_no == employee_no)"""
content = content.replace(old_ot, new_ot)

# 4. Refactor get_users
old_users = """    req_user = current_user
    if req_user.role == "manager":
        query = query.filter(models.User.team_id == req_user.team_id)
    elif req_user.role != "system_admin":
        query = query.filter(models.User.employee_no == req_user.employee_no)"""
new_users = """    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None:
        query = query.filter(models.User.employee_no.in_(allowed_nos))"""
content = content.replace(old_users, new_users)

# 5. Modify login function to completely skip LDAP groups/teams logic
login_pattern = r"(# Resolve Role.*?)(# Sync LDAP Identity to local DB for foreign keys)"
login_replacement = r"""
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

        \2"""
content = re.sub(login_pattern, login_replacement.strip("\n") + "\n        ", content, flags=re.DOTALL)

# Sync user_dn
sync_pattern = r"(employee_no=auth_result\[\"employee_no\"\],.*?manager_name=auth_result\.get\(\"manager_name\"\))"
sync_replacement = r"\1,\n                user_dn=auth_result.get('user_dn')"
content = re.sub(sync_pattern, sync_replacement, content, flags=re.DOTALL)

sync_pattern2 = r"(user\.manager_name = auth_result\.get\(\"manager_name\"\))"
sync_replacement2 = r"\1\n            user.user_dn = auth_result.get('user_dn')"
content = re.sub(sync_pattern2, sync_replacement2, content, flags=re.DOTALL)

# Write back
with open("backend/main.py", "w") as f:
    f.write(content)
