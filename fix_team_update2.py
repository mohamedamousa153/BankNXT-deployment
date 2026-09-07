with open("backend/main.py", "r") as f:
    lines = f.readlines()

out = []
skip = False
for line in lines:
    if "req_user = current_user" in line:
        skip = True
        out.append("    allowed_nos = get_allowed_employee_nos(db, current_user)\n")
        out.append("    if allowed_nos is not None and db_record.employee_no not in allowed_nos:\n")
        out.append("        raise HTTPException(status_code=403, detail=\"Forbidden: Not authorized to access this record.\")\n")
        continue
    
    if skip:
        if line.strip() == "" or line.startswith("    db_record.status") or "db.delete" in line or line.startswith("    for key"):
            skip = False
        else:
            continue
            
    out.append(line)

with open("backend/main.py", "w") as f:
    f.writelines(out)
