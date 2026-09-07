import re

with open("backend/main.py", "r") as f:
    content = f.read()

# For update_overtime, delete_overtime, update_wfh, delete_wfh:
# Let's replace the whole role checking block
pattern = r"    req_user = current_user\n    if req_user.role == \"employee\":\n        if db_record.employee_no != req_user.employee_no:\n            raise HTTPException\(status_code=403, detail=\"Forbidden:[^\"]+\"\)\n            \n    elif req_user.role == \"manager\":\n        if db_record.team_id != req_user.team_id:\n            raise HTTPException\(status_code=403, detail=\"Forbidden:[^\"]+\"\)"

replacement = """    allowed_nos = get_allowed_employee_nos(db, current_user)
    if allowed_nos is not None and db_record.employee_no not in allowed_nos:
        raise HTTPException(status_code=403, detail="Forbidden: Not authorized to access this record.")"""

content = re.sub(pattern, replacement, content)

with open("backend/main.py", "w") as f:
    f.write(content)
