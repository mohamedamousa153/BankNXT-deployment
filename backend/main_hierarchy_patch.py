with open("backend/main.py", "r") as f:
    content = f.read()

import re

old_hierarchy = re.search(r'@app\.get\("/api/users/hierarchy"\).*?return {\s*"direct_reports": direct_reports,\s*"all_subordinates": subs\s*}', content, re.DOTALL).group(0)

new_hierarchy = """@app.get("/api/users/hierarchy")
def get_user_hierarchy(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    config = db.query(models.LDAPSettings).first()
    
    if current_user.role == "system_admin":
        # Admin can view all users, but we'll return empty hierarchy to avoid loading thousands
        return {"has_direct_reports": False, "direct_reports": [], "all_subordinates": []}
        
    if config and config.enabled and current_user.user_dn:
        return ldap_service.get_ad_hierarchy(current_user.user_dn, config, db)
        
    # Fallback to local DB if LDAP is disabled
    subs = []
    direct_reports = []
    has_direct_reports = False
    
    if current_user.user_dn:
        sub_nos = get_subordinate_user_employee_nos(db, current_user.user_dn)
        if sub_nos:
            users = db.query(models.User).filter(models.User.employee_no.in_(sub_nos)).all()
            subs = [{"employee_no": u.employee_no, "name": u.name, "user_dn": u.user_dn, "manager_dn": u.manager_dn} for u in users]
            
        dr = db.query(models.User).filter(models.User.manager_dn == current_user.user_dn).all()
        direct_reports = [{"employee_no": u.employee_no, "name": u.name, "user_dn": u.user_dn, "manager_dn": u.manager_dn} for u in dr]
        has_direct_reports = len(direct_reports) > 0
        
    return {
        "has_direct_reports": has_direct_reports,
        "direct_reports": direct_reports,
        "all_subordinates": subs
    }"""

content = content.replace(old_hierarchy, new_hierarchy)

with open("backend/main.py", "w") as f:
    f.write(content)
