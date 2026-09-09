with open("backend/main.py", "r") as f:
    content = f.read()

content = content.replace(
    'subs = ldap_service.get_ad_subordinates_recursive(db, auth_result.get("user_dn"), config)',
    'subs = ldap_service.get_ad_subordinates_recursive(auth_result.get("user_dn"), config, db)'
)

with open("backend/main.py", "w") as f:
    f.write(content)
