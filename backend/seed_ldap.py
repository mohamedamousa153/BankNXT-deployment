import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "/app/backend/data/dashboard.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("""
INSERT INTO ldap_settings (
    id, enabled, server_url, port, protocol, use_tls, base_dn, bind_username, bind_password, timeout,
    user_search_base, user_search_filter, attr_username, attr_employee_no, attr_display_name, attr_email, attr_manager, attr_department,
    group_search_base, group_membership_attr, group_sysadmin, group_manager, group_employee
) VALUES (
    1, 1, '10.177.100.10', 389, 'LDAP', 0, 'DC=AIBEgypt,DC=local', 'CN=cp4prod,OU=Service Accounts,DC=AIBEgypt,DC=local', 'SECURE_PASSWORD', 10,
    'DC=AIBEgypt,DC=local', '(&(objectCategory=person)(sAMAccountName={username}))', 'sAMAccountName', 'employeeNumber', 'displayName', 'mail', 'manager', 'department',
    'DC=AIBEgypt,DC=local', 'memberOf', 'CN=HRPortal-SystemAdmins,OU=Groups,DC=AIBEgypt,DC=local', 'CN=HRPortal-Managers,OU=Groups,DC=AIBEgypt,DC=local', 'CN=HRPortal-Employees,OU=Groups,DC=AIBEgypt,DC=local'
)
""")

c.execute("INSERT INTO teams (id, name, ldap_group_id) VALUES (3, 'DevOps', 'CN=DevOps & SRE,CN=Users,DC=AIBEgypt,DC=local')")
c.execute("UPDATE users SET role='system_admin' WHERE employee_no='admin'")

conn.commit()
conn.close()
print("LDAP Settings Seeded")
