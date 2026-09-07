import re

with open("backend/main.py", "r") as f:
    content = f.read()

# Completely remove all references to team_id logic in updates
pattern = r"            \n    elif req_user\.role == \"manager\":\n        if db_record\.team_id != req_user\.team_id:\n            raise HTTPException\(status_code=403, detail=\"Forbidden:[^\"]+\"\)\n"

content = re.sub(pattern, "", content)

# Remove team_id assignments during creation
content = re.sub(r"    record_dict\['team_id'\] = current_user\.team_id\n", "", content)

# Remove team_id from users API response
content = content.replace(' "team_id": u.team_id', '')

with open("backend/main.py", "w") as f:
    f.write(content)
