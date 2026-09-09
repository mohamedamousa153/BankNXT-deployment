import re
with open("backend/main.py", "r") as f:
    content = f.read()

old_logic = """        import secrets
        user.session_token = secrets.token_hex(32)
        db.commit()
        db.refresh(user)
        return user"""

new_logic = """        import secrets
        user.session_token = secrets.token_hex(32)
        db.commit()
        db.refresh(user)
        user.has_direct_reports = has_direct_reports
        return user"""

content = content.replace(old_logic, new_logic)
with open("backend/main.py", "w") as f:
    f.write(content)
