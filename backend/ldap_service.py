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
        
        # 2. Search for groups
        group_dns = []
        # Try to read directly from user attributes (Active Directory memberOf style)
        direct_groups = get_attr_case_insensitive(attrs, config.group_membership_attr)
        if direct_groups:
            group_dns.extend([str(g) for g in direct_groups])
            
        # If the configuration provided a group search base, also do a traditional group search
        if config.group_search_base and config.group_membership_attr:
            group_filter = f"({config.group_membership_attr}={user_dn})"
            admin_conn.search(config.group_search_base, group_filter, SUBTREE, attributes=['*'])
            for entry in admin_conn.entries:
                if entry.entry_dn not in group_dns:
                    group_dns.append(entry.entry_dn)
                
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
