with open("backend/main.py", "r") as f:
    content = f.read()

old_ot_create = """    db_record = models.OvertimeRecord(
        **record_dict,
        duration_hours=duration_hours,
        status="Pending Approval",
        created_at=datetime.now().isoformat()
    )"""

new_ot_create = """    db_record = models.OvertimeRecord(
        **record_dict,
        duration_hours=duration_hours,
        status="Pending Approval",
        approver_dn=current_user.manager_dn,
        approver_name=current_user.manager_name,
        created_at=datetime.now().isoformat()
    )"""

content = content.replace(old_ot_create, new_ot_create)

old_wfh_create = """    db_record = models.WFHRecord(
        **record_dict,
        week_number=w,
        year=y,
        status="Pending Approval", 
        created_at=datetime.now().isoformat()
    )"""

new_wfh_create = """    db_record = models.WFHRecord(
        **record_dict,
        approver_dn=current_user.manager_dn,
        approver_name=current_user.manager_name,
        week_number=w,
        year=y,
        status="Pending Approval", 
        created_at=datetime.now().isoformat()
    )"""

content = content.replace(old_wfh_create, new_wfh_create)

with open("backend/main.py", "w") as f:
    f.write(content)
