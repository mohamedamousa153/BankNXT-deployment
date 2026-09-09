import re
with open("backend/main.py", "r") as f:
    content = f.read()

old_logic = """        # Manager hierarchy is driven by AD. We check if they have reports.
        resolved_role = "employee"
        if creds.employee_no == "admin" or creds.employee_no == "sysadmin":
            resolved_role = "system_admin"
        elif auth_result.get("user_dn"):
            # Check if this user has any subordinates in AD
            subs = ldap_service.get_ad_subordinates_recursive(auth_result.get("user_dn"), config, db)
            if subs and len(subs) > 0:
                resolved_role = "manager"
        
        # Determine top-level log prints"""

new_logic = """        # Manager hierarchy is driven by AD. Role is only for sysadmin.
        resolved_role = "employee"
        if creds.employee_no == "admin" or creds.employee_no == "sysadmin":
            resolved_role = "system_admin"
            
        has_direct_reports = False
        if auth_result.get("user_dn") and resolved_role != "system_admin":
            # Check AD quickly just for direct reports
            hi = ldap_service.get_ad_hierarchy(auth_result.get("user_dn"), config, None)
            has_direct_reports = hi.get("has_direct_reports", False)
        
        # Determine top-level log prints"""

content = content.replace(old_logic, new_logic)

# In the login response, we currently return: return {"token": token, "user": ...}
# We should add has_direct_reports to the response.
# wait, the response model might be constrained. Let's look at it.
