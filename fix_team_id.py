with open("backend/main.py", "r") as f:
    content = f.read()

content = content.replace("team_id=resolved_team_id", "team_id=None")
content = content.replace("user.team_id = resolved_team_id", "user.team_id = None")

with open("backend/main.py", "w") as f:
    f.write(content)
