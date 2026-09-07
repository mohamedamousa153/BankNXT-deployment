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
            
        admin_conn.search(search_base, filter_str, SUBTREE, attributes=['*'])
        
        if not admin_conn.entries:
            admin_conn.unbind()
            return {"success": False, "message": f"User '{username}' not found in LDAP."}
            
        user_entry = admin_conn.entries[0]
        user_dn = user_entry.entry_dn
        
        attrs = user_entry.entry_attributes_as_dict
        employee_no = attrs.get(config.attr_employee_no, [username])[0]
        display_name = attrs.get(config.attr_display_name, [username])[0]
        manager_dn = attrs.get(config.attr_manager, [None])[0]
        
        # 2. Search for groups
        group_dns = []
        if config.group_search_base and config.group_membership_attr:
            group_filter = f"({config.group_membership_attr}={user_dn})"
            admin_conn.search(config.group_search_base, group_filter, SUBTREE, attributes=['*'])
            for entry in admin_conn.entries:
                group_dns.append(entry.entry_dn)
                
        # 2.5 Resolve manager
        manager_name = None
        if manager_dn:
            admin_conn.search(config.base_dn, f"(distinguishedName={manager_dn})", SUBTREE, attributes=['*'])
            if admin_conn.entries:
                mgr_entry = admin_conn.entries[0]
                mgr_attrs = mgr_entry.entry_attributes_as_dict
                manager_name = mgr_attrs.get(config.attr_display_name, [manager_dn])[0]
                
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
