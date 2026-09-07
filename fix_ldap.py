import re

with open("backend/ldap_service.py", "r") as f:
    content = f.read()

pattern = r"(        # 2\. Search for groups.*?)        # 2\.5 Resolve manager"
replacement = r"""
        # Groups and role mapping via LDAP has been removed as AD manager relation is the sole source of truth.
        group_dns = []
        
        # 2.5 Resolve manager
"""
content = re.sub(pattern, replacement.strip("\n") + "\n        ", content, flags=re.DOTALL)

with open("backend/ldap_service.py", "w") as f:
    f.write(content)
