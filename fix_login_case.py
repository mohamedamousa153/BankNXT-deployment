with open("backend/main.py", "r") as f:
    content = f.read()

old_sync = """        user = db.query(models.User).filter(models.User.employee_no == auth_result["employee_no"]).first()
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
            user.user_dn = auth_result.get('user_dn')"""

new_sync = """        from sqlalchemy import func
        user = None
        if auth_result.get('user_dn'):
            user = db.query(models.User).filter(models.User.user_dn == auth_result['user_dn']).first()
        if not user:
            user = db.query(models.User).filter(func.lower(models.User.employee_no) == func.lower(auth_result["employee_no"])).first()
            
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
            # Important: sync the auth_result to use the existing DB case so session tokens match!
            auth_result["employee_no"] = user.employee_no"""

content = content.replace(old_sync, new_sync)

with open("backend/main.py", "w") as f:
    f.write(content)
