import re

with open("backend/ldap_service.py", "r") as f:
    content = f.read()

# Add get_ad_subordinates_recursive at the end
new_code = """
def get_ad_subordinates_recursive(manager_dn: str, config, db_session) -> list:
    if not manager_dn or not config or not config.enabled:
        return []
        
    try:
        from ldap3.utils.conv import escape_filter_chars
        from models import User
        
        host = config.server_url
        if "://" in host:
            host = host.split("://")[1]
            
        server = Server(host, port=config.port, use_ssl=config.use_tls, get_info=ALL, connect_timeout=config.timeout)
        admin_conn = Connection(server, user=config.bind_username, password=config.bind_password, auto_bind=True, receive_timeout=config.timeout)
        
        visited = set()
        queue = [manager_dn]
        allowed_employees = []
        
        while queue:
            current_dn = queue.pop(0)
            if current_dn in visited:
                continue
            visited.add(current_dn)
            
            escaped_dn = escape_filter_chars(current_dn)
            search_filter = f"(&(objectCategory=person)(manager={escaped_dn}))"
            
            admin_conn.search(
                search_base=config.base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['*', 'manager']
            )
            
            for entry in admin_conn.entries:
                attrs = entry.entry_attributes_as_dict
                
                emp_list = get_attr_case_insensitive(attrs, config.attr_employee_no)
                emp_no = emp_list[0] if emp_list and str(emp_list[0]).strip() else None
                if not emp_no:
                    usr_list = get_attr_case_insensitive(attrs, config.attr_username)
                    emp_no = usr_list[0] if usr_list and str(usr_list[0]).strip() else None
                if not emp_no:
                    continue
                    
                emp_no = str(emp_no)
                
                disp_list = get_attr_case_insensitive(attrs, config.attr_display_name)
                name = disp_list[0] if disp_list and str(disp_list[0]).strip() else emp_no
                
                mgr_list = get_attr_case_insensitive(attrs, 'manager')
                mgr_dn = mgr_list[0] if mgr_list else None
                user_dn = entry.entry_dn
                
                # Try to resolve manager name inside the loop or keep it simple
                # To save LDAP roundtrips, we might not resolve manager_name for everyone right away
                # or we just rely on AD DN. We'll set manager_name = None for now, as UI mostly needs manager DN.
                
                # Sync to SQLite safely
                user_record = db_session.query(User).filter(User.employee_no == emp_no).first()
                if not user_record:
                    user_record = User(
                        employee_no=emp_no,
                        name=str(name),
                        password="ldap_managed",
                        role="employee",
                        team_id=None,
                        user_dn=str(user_dn),
                        manager_dn=str(mgr_dn) if mgr_dn else None,
                    )
                    db_session.add(user_record)
                else:
                    user_record.name = str(name)
                    user_record.user_dn = str(user_dn)
                    user_record.manager_dn = str(mgr_dn) if mgr_dn else None
                    
                if emp_no not in allowed_employees:
                    allowed_employees.append(emp_no)
                    
                if user_dn and user_dn not in visited:
                    queue.append(str(user_dn))
                    
        db_session.commit()
        admin_conn.unbind()
        return allowed_employees
    except Exception as e:
        print(f"LDAP Subordinate Resolution Error: {e}")
        return []
"""

if "def get_ad_subordinates_recursive" not in content:
    with open("backend/ldap_service.py", "a") as f:
        f.write(new_code)
