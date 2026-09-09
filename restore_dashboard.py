with open("/tmp/app.jsx.old", "r") as f:
    old_lines = f.readlines()

ldap_start = -1
admin_dash_start = -1
admin_settings_start = -1

for i, line in enumerate(old_lines):
    if line.startswith("function LDAPSettingsPage"):
        ldap_start = i
    if line.startswith("function AdminDashboard"):
        admin_dash_start = i
    if line.startswith("function AdminSettings"):
        admin_settings_start = i

ldap_and_dashboard_code = "".join(old_lines[ldap_start:admin_settings_start])

# Now inject it into the current app.jsx right before AdminSettings
with open("frontend/app.jsx", "r") as f:
    current_content = f.read()

current_content = current_content.replace("function AdminSettings() {", ldap_and_dashboard_code + "\nfunction AdminSettings() {")

# Then, we need to apply the UI refactor to AdminDashboard (change TeamOverview to HierarchyOverview)
current_content = current_content.replace("const [teams, setTeams] = useState([]);", "const [hierarchy, setHierarchy] = useState({direct_reports: [], all_subordinates: []});\n  const [viewFilter, setViewFilter] = useState('direct');")
current_content = current_content.replace("const [selectedTeam, setSelectedTeam] = useState(user.team_id || 1);", "")
current_content = current_content.replace("fetch(`/api/teams?requester=${user.employee_no}`),", "fetch(`/api/users/hierarchy`),")
current_content = current_content.replace("setTeams(await teamRes.json());", "setHierarchy(await teamRes.json());")
current_content = current_content.replace("teams={teams}", "hierarchy={hierarchy}")
current_content = current_content.replace("selectedTeam={selectedTeam}", "viewFilter={viewFilter}")
current_content = current_content.replace("setSelectedTeam={setSelectedTeam}", "setViewFilter={setViewFilter}")
current_content = current_content.replace("adminTab === 'team'", "adminTab === 'hierarchy'")
current_content = current_content.replace("setAdminTab('team')", "setAdminTab('hierarchy')")
current_content = current_content.replace("user.role === 'manager' ? 'team' : 'global'", "user.role === 'manager' ? 'hierarchy' : 'global'")
current_content = current_content.replace("user.role === 'manager' ? \"Team Dashboard\" : \"Global Dashboard\"", "user.role === 'manager' ? \"My Reports\" : \"Global Dashboard\"")
current_content = current_content.replace("My Team Dashboard", "My Reports Dashboard")
current_content = current_content.replace("My Team Overview", "My Reports Overview")
current_content = current_content.replace("<TeamOverview ", "<HierarchyOverview ")

with open("frontend/app.jsx", "w") as f:
    f.write(current_content)
