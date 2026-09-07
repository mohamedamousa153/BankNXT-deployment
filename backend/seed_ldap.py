import sqlite3

conn = sqlite3.connect('backend/dashboard.db')
c = conn.cursor()

# Insert the provided LDAP configuration
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

# Insert a sample team mapped to DevOps & SRE
c.execute("""
INSERT INTO teams (id, name, ldap_group_id) VALUES (3, 'DevOps', 'CN=DevOps & SRE,CN=Users,DC=AIBEgypt,DC=local')
""")

conn.commit()
conn.close()
print("LDAP Settings Seeded")
