import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError

def test_ldap_connection(server_url: str, port: int, timeout: int = 5, bind_dn: str = None, bind_password: str = None, use_tls: bool = False) -> dict:
    if not server_url:
        return {"success": False, "message": "LDAP server URL is required."}
        
    try:
        host = server_url
        if "://" in host:
            host = host.split("://")[1]
            
        server = Server(host, port=port, use_ssl=use_tls, get_info=ALL, connect_timeout=timeout)
        conn = Connection(server, user=bind_dn, password=bind_password, auto_bind=True, receive_timeout=timeout)
        conn.unbind()
        return {"success": True, "message": f"Successfully connected and bound to {host}:{port}"}
    except LDAPBindError as e:
        return {"success": False, "message": f"LDAP Bind Failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}

def get_attr_case_insensitive(attrs: dict, attr_name: str):
    if not attr_name:
        return []
    attr_name_lower = attr_name.lower()
    for k, v in attrs.items():
        if k.lower() == attr_name_lower:
            return v if isinstance(v, list) else [v]
    return []

def authenticate_user(username: str, password: str, config) -> dict:
    try:
        host = config.server_url
        if "://" in host:
            host = host.split("://")[1]
            
        server = Server(host, port=config.port, use_ssl=config.use_tls, get_info=ALL, connect_timeout=config.timeout)
        admin_conn = Connection(server, user=config.bind_username, password=config.bind_password, auto_bind=True, receive_timeout=config.timeout)
        
        # 1. Search for user
        search_base = config.user_search_base if config.user_search_base else config.base_dn
        
        # Process filter safely
        filter_str = config.user_search_filter if config.user_search_filter else f"({config.attr_username}={username})"
        if "{username}" in filter_str:
            filter_str = filter_str.replace("{username}", username)
            
        # We explicitly request memberOf in case it's not included in '*' by default on some servers
        admin_conn.search(search_base, filter_str, SUBTREE, attributes=['*', 'memberOf', config.group_membership_attr])
        
        if not admin_conn.entries:
            admin_conn.unbind()
            return {"success": False, "message": f"User '{username}' not found in LDAP."}
            
        user_entry = admin_conn.entries[0]
        user_dn = user_entry.entry_dn
        
        # Get raw dict attributes
        attrs = user_entry.entry_attributes_as_dict
        
        # Safe extraction
        emp_list = get_attr_case_insensitive(attrs, config.attr_employee_no)
        employee_no = emp_list[0] if emp_list and str(emp_list[0]).strip() else username
        
        disp_list = get_attr_case_insensitive(attrs, config.attr_display_name)
        display_name = disp_list[0] if disp_list and str(disp_list[0]).strip() else username
        
        mgr_list = get_attr_case_insensitive(attrs, config.attr_manager)
        manager_dn = mgr_list[0] if mgr_list else None
        
        # Groups and role mapping via LDAP has been removed as AD manager relation is the sole source of truth.
        group_dns = []
        
        # 2.5 Resolve manager
        
        manager_name = None
        if manager_dn:
            admin_conn.search(config.base_dn, f"(distinguishedName={manager_dn})", SUBTREE, attributes=['*'])
            if admin_conn.entries:
                mgr_entry = admin_conn.entries[0]
                mgr_attrs = mgr_entry.entry_attributes_as_dict
                mgr_disp_list = get_attr_case_insensitive(mgr_attrs, config.attr_display_name)
                manager_name = mgr_disp_list[0] if mgr_disp_list else manager_dn
                
        admin_conn.unbind()
        
        # 3. Verify password
        try:
            user_conn = Connection(server, user=user_dn, password=password, auto_bind=True, receive_timeout=config.timeout)
            user_conn.unbind()
        except LDAPBindError:
            return {"success": False, "message": "Invalid credentials."}
            
        return {
            "success": True,
            "employee_no": str(employee_no),
            "name": str(display_name),
            "user_dn": user_dn,
            "groups": group_dns,
            "manager_dn": manager_dn,
            "manager_name": manager_name
        }
    except Exception as e:
        return {"success": False, "message": f"LDAP Authentication Error: {str(e)}"}

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
            
            
            if current_dn == manager_dn:
                print(f"DEBUG: DIRECT REPORTS FOUND: {len(admin_conn.entries)}")
                
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
