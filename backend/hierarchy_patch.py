import sys

with open("backend/ldap_service.py", "r") as f:
    content = f.read()

new_func = """
def get_ad_hierarchy(manager_dn: str, config, db_session) -> dict:
    result = {
        "has_direct_reports": False,
        "direct_reports": [],
        "all_subordinates": []
    }
    if not manager_dn or not config or not config.enabled:
        return result
        
    try:
        from ldap3 import Server, Connection, SUBTREE, ALL
        from ldap3.utils.conv import escape_filter_chars
        from models import User
        from sqlalchemy import func
        
        host = config.server_url
        if "://" in host:
            host = host.split("://")[1]
            
        server = Server(host, port=config.port, use_ssl=config.use_tls, get_info=ALL, connect_timeout=config.timeout)
        admin_conn = Connection(server, user=config.bind_username, password=config.bind_password, auto_bind=True, receive_timeout=config.timeout)
        
        visited = set()
        queue = [(manager_dn, True)] # (dn, is_direct)
        
        while queue:
            current_dn, is_direct = queue.pop(0)
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
                name = str(disp_list[0]) if disp_list and str(disp_list[0]).strip() else emp_no
                
                user_dn = entry.entry_dn
                mgr_list = get_attr_case_insensitive(attrs, config.attr_manager)
                mgr_dn = str(mgr_list[0]) if mgr_list else None
                
                sub_data = {
                    "employee_no": emp_no,
                    "name": name,
                    "user_dn": user_dn,
                    "manager_dn": mgr_dn
                }
                
                # Check uniqueness before adding to lists
                if not any(x["employee_no"] == emp_no for x in result["all_subordinates"]):
                    result["all_subordinates"].append(sub_data)
                    
                    if is_direct:
                        result["direct_reports"].append(sub_data)
                        result["has_direct_reports"] = True
                        
                    # Sync to shadow DB
                    if db_session and user_dn:
                        user_record = db_session.query(User).filter(User.user_dn == str(user_dn)).first()
                        if not user_record:
                            user_record = db_session.query(User).filter(func.lower(User.employee_no) == func.lower(emp_no)).first()
                        
                        if not user_record:
                            user_record = User(
                                employee_no=emp_no,
                                name=name,
                                user_dn=user_dn,
                                manager_dn=mgr_dn,
                                role="employee"
                            )
                            db_session.add(user_record)
                        else:
                            user_record.name = name
                            user_record.user_dn = user_dn
                            user_record.manager_dn = mgr_dn
                        db_session.commit()
                
                if user_dn and user_dn not in visited:
                    queue.append((user_dn, False))
                    
    except Exception as e:
        print(f"ERROR resolving AD hierarchy: {e}")
        
    return result

"""

content = content + new_func

with open("backend/ldap_service.py", "w") as f:
    f.write(content)
