with open("backend/ldap_service.py", "r") as f:
    content = f.read()

old_sync = """                # Sync to SQLite safely
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
                    user_record.manager_dn = str(mgr_dn) if mgr_dn else None"""

new_sync = """                # Sync to SQLite safely
                # Search by user_dn first since employee_no could have different casing
                from sqlalchemy import func
                user_record = db_session.query(User).filter(User.user_dn == str(user_dn)).first()
                if not user_record:
                    user_record = db_session.query(User).filter(func.lower(User.employee_no) == func.lower(emp_no)).first()
                
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
                    # We do not override employee_no to avoid breaking existing relations
                    emp_no = user_record.employee_no  # use the DB's casing"""

content = content.replace(old_sync, new_sync)

with open("backend/ldap_service.py", "w") as f:
    f.write(content)
