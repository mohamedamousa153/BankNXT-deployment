with open("backend/main.py", "r") as f:
    content = f.read()

old_logic = """        # Manager hierarchy is driven by AD. We keep role='employee'.
        resolved_role = "employee"
        if creds.employee_no == "admin":
            resolved_role = "system_admin"
        
        # Determine top-level log prints"""

new_logic = """        # Manager hierarchy is driven by AD. We check if they have reports.
        resolved_role = "employee"
        if creds.employee_no == "admin" or creds.employee_no == "sysadmin":
            resolved_role = "system_admin"
        elif auth_result.get("user_dn"):
            # Check if this user has any subordinates in AD
            subs = ldap_service.get_ad_subordinates_recursive(db, auth_result.get("user_dn"), config)
            if subs and len(subs) > 0:
                resolved_role = "manager"
        
        # Determine top-level log prints"""

content = content.replace(old_logic, new_logic)

with open("backend/main.py", "w") as f:
    f.write(content)
