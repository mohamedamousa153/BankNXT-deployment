import re

with open("backend/main.py", "r") as f:
    content = f.read()

pattern = r"def get_allowed_employee_nos\(db, current_user\):.*?return allowed"

replacement = """def get_allowed_employee_nos(db, current_user):
    if current_user.role == "system_admin":
        return None
    allowed = [current_user.employee_no]
    if current_user.user_dn:
        config = db.query(models.LDAPSettings).first()
        if config and config.enabled:
            # Source of truth: AD directly
            ad_subs = ldap_service.get_ad_subordinates_recursive(current_user.user_dn, config, db)
            print(f"DEBUG: Found {len(ad_subs)} subordinates from AD for {current_user.employee_no}")
            allowed.extend(ad_subs)
        else:
            # Fallback if AD disabled
            subs = get_subordinate_user_employee_nos(db, current_user.user_dn)
            allowed.extend(subs)
            
    # Ensure uniqueness
    allowed = list(set(allowed))
    return allowed"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open("backend/main.py", "w") as f:
    f.write(content)
