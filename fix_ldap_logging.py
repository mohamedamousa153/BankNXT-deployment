with open("backend/ldap_service.py", "r") as f:
    content = f.read()

old_code = "for entry in admin_conn.entries:"
new_code = """
            if current_dn == manager_dn:
                print(f"DEBUG: DIRECT REPORTS FOUND: {len(admin_conn.entries)}")
                
            for entry in admin_conn.entries:"""

content = content.replace(old_code, new_code)
with open("backend/ldap_service.py", "w") as f:
    f.write(content)
