with open("backend/main.py", "r") as f:
    content = f.read()

old_auth = """    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to access this record.")"""

new_auth = """    # Strict Direct-Manager Authorization for Updates
    if current_user.role != "system_admin":
        if getattr(db_record, "approver_dn", None):
            if db_record.approver_dn != current_user.user_dn:
                raise HTTPException(status_code=403, detail="Forbidden: You are not the direct manager assigned to approve this request.")
        else:
            # Legacy fallback
            allowed_nos = get_allowed_employee_nos(db, current_user)
            if allowed_nos is not None and db_record.employee_no not in allowed_nos:
                raise HTTPException(status_code=403, detail="Forbidden: Not authorized to access this record.")"""

content = content.replace(old_auth, new_auth)

with open("backend/main.py", "w") as f:
    f.write(content)
