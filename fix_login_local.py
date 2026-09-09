import re
with open("backend/main.py", "r") as f:
    content = f.read()

content = content.replace("    if config and config.enabled:\n        # LDAP Mode", "    has_direct_reports = False\n    if config and config.enabled:\n        # LDAP Mode")

with open("backend/main.py", "w") as f:
    f.write(content)
