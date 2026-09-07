import re

with open("frontend/app.jsx", "r") as f:
    content = f.read()

# Replace TeamOverview component with HierarchyOverview
old_team = r"function TeamOverview\(\{ wfh, overtime, teams, users, selectedTeam, setSelectedTeam, dateFilter, formatDateOnly, getWFHDaysCount, user, handleAction \}\) \{.*?\n\s+return \(\n.*?\n\s+\);\n\}"

new_hierarchy = """function HierarchyOverview({ wfh, overtime, hierarchy, users, viewFilter, setViewFilter, dateFilter, formatDateOnly, getWFHDaysCount, user, handleAction }) {
    // viewFilter: 'direct' or 'all'
    const displayUsers = viewFilter === 'direct' ? hierarchy.direct_reports : hierarchy.all_subordinates;
    const memberNos = new Set(displayUsers.map(u => String(u.employee_no)));
    
    const teamWfh = wfh.filter(r => memberNos.has(String(r.employee_no)));
    const teamOt = overtime.filter(r => memberNos.has(String(r.employee_no)));
    
    const totalWfhDays = teamWfh.reduce((acc, r) => acc + getWFHDaysCount(r), 0);
    const pendingWfh = teamWfh.filter(r => r.status === 'Pending Approval').length;
    const totalOtHours = teamOt.reduce((acc, r) => acc + (r.duration_hours || 0), 0);
    const pendingOt = teamOt.filter(r => r.status === 'Pending Approval').length;

    const wfhToday = teamWfh.filter(r => {
        if (!r.selected_dates) return false;
        try {
            return JSON.parse(r.selected_dates).includes(formatDateOnly(new Date()));
        } catch { return false; }
    });

    const empSummary = displayUsers.map(emp => {
        const empWfh = teamWfh.filter(r => String(r.employee_no) === String(emp.employee_no));
        const empOt = teamOt.filter(r => String(r.employee_no) === String(emp.employee_no));
        return {
            ...emp,
            wfh_count: empWfh.reduce((acc, r) => acc + getWFHDaysCount(r), 0),
            wfh_pending: empWfh.filter(r => r.status === 'Pending Approval').length,
            ot_hours: empOt.reduce((acc, r) => acc + (r.duration_hours || 0), 0),
            ot_pending: empOt.filter(r => r.status === 'Pending Approval').length
        };
    }).sort((a,b) => b.wfh_count - a.wfh_count);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                <h3 className="text-xl font-bold text-slate-800">My Reports Dashboard</h3>
                <div className="flex gap-4 items-center">
                    <select className="border rounded-lg p-2 font-medium text-slate-700" value={viewFilter} onChange={e => setViewFilter(e.target.value)}>
                        <option value="direct">Direct Reports ({hierarchy.direct_reports.length})</option>
                        <option value="all">All Subordinates ({hierarchy.all_subordinates.length})</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Total Employees</div>
                    <p className="text-2xl font-black text-slate-700">{displayUsers.length}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Pending WFH</div>
                    <p className="text-2xl font-black text-blue-600">{pendingWfh}</p>
                    <p className="text-xs text-slate-400 mt-1">{totalWfhDays} total WFH days</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Pending Overtime</div>
                    <p className="text-2xl font-black text-amber-600">{pendingOt}</p>
                    <p className="text-xs text-slate-400 mt-1">{totalOtHours} total hours</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">WFH Today</div>
                    <p className="text-2xl font-black text-emerald-600">{wfhToday.length}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="font-bold text-slate-700 mb-4">Pending WFH Approvals</h3>
                    <div className="space-y-3">
                        {teamWfh.filter(r => r.status === 'Pending Approval').length > 0 ? (
                            teamWfh.filter(r => r.status === 'Pending Approval').map(r => (
                                <div key={r.id} className="border p-3 rounded-lg flex justify-between items-center">
                                    <div>
                                        <p className="font-bold">{r.name} ({r.employee_no})</p>
                                        <p className="text-sm text-slate-500">{getWFHDaysCount(r)} Days: {r.selected_dates ? JSON.parse(r.selected_dates).join(', ') : r.date}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={() => handleAction('wfh', r.id, 'Approved')} className="bg-emerald-500 text-white px-3 py-1 rounded text-sm hover:bg-emerald-600 font-bold">Approve</button>
                                        <button onClick={() => handleAction('wfh', r.id, 'Rejected')} className="bg-rose-500 text-white px-3 py-1 rounded text-sm hover:bg-rose-600 font-bold">Reject</button>
                                    </div>
                                </div>
                            ))
                        ) : <p className="text-slate-400 text-sm">No pending requests.</p>}
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="font-bold text-slate-700 mb-4">Pending Overtime Approvals</h3>
                    <div className="space-y-3">
                        {teamOt.filter(r => r.status === 'Pending Approval').length > 0 ? (
                            teamOt.filter(r => r.status === 'Pending Approval').map(r => (
                                <div key={r.id} className="border p-3 rounded-lg flex justify-between items-center">
                                    <div>
                                        <p className="font-bold">{r.name} ({r.employee_no})</p>
                                        <p className="text-sm text-slate-500">{r.start_datetime.split('T')[0]} - {r.duration_hours} hrs</p>
                                        <p className="text-xs text-slate-400 truncate w-48">{r.assigned_work}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={() => handleAction('overtime', r.id, 'Approved')} className="bg-emerald-500 text-white px-3 py-1 rounded text-sm hover:bg-emerald-600 font-bold">Approve</button>
                                        <button onClick={() => handleAction('overtime', r.id, 'Rejected')} className="bg-rose-500 text-white px-3 py-1 rounded text-sm hover:bg-rose-600 font-bold">Reject</button>
                                    </div>
                                </div>
                            ))
                        ) : <p className="text-slate-400 text-sm">No pending requests.</p>}
                    </div>
                </div>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <h3 className="font-bold text-slate-700 mb-4">Employee Overview ({displayUsers.length})</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-600">
                            <tr>
                                <th className="p-3 rounded-tl-lg">Employee</th>
                                <th className="p-3">Manager</th>
                                <th className="p-3 text-center">WFH Days (Total)</th>
                                <th className="p-3 text-center">WFH Pending</th>
                                <th className="p-3 text-center">OT Hours (Total)</th>
                                <th className="p-3 text-center rounded-tr-lg">OT Pending</th>
                            </tr>
                        </thead>
                        <tbody>
                            {empSummary.map(emp => (
                                <tr key={emp.employee_no} className="border-b last:border-0 hover:bg-slate-50">
                                    <td className="p-3 font-medium">{emp.name} ({emp.employee_no})</td>
                                    <td className="p-3">{emp.manager_name || 'N/A'}</td>
                                    <td className="p-3 text-center">{emp.wfh_count}</td>
                                    <td className="p-3 text-center text-blue-600 font-bold">{emp.wfh_pending > 0 ? emp.wfh_pending : '-'}</td>
                                    <td className="p-3 text-center">{emp.ot_hours}</td>
                                    <td className="p-3 text-center text-amber-600 font-bold">{emp.ot_pending > 0 ? emp.ot_pending : '-'}</td>
                                </tr>
                            ))}
                            {empSummary.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="p-4 text-center text-slate-500">No employees found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
"""

content = re.sub(r"function TeamOverview\(\{.*?\}\s*\{.*?\n\}\n", new_hierarchy, content, flags=re.DOTALL)


content = content.replace("const [teams, setTeams] = useState([]);", "const [hierarchy, setHierarchy] = useState({direct_reports: [], all_subordinates: []});\n  const [viewFilter, setViewFilter] = useState('direct');")
content = content.replace("const [selectedTeam, setSelectedTeam] = useState(user.team_id || 1);", "")

# Fix API calls
content = content.replace("fetch(`/api/teams?requester=${user.employee_no}`),", "fetch(`/api/users/hierarchy`),")
content = content.replace("setTeams(await teamRes.json());", "setHierarchy(await teamRes.json());")
content = content.replace("teams={teams}", "hierarchy={hierarchy}")
content = content.replace("selectedTeam={selectedTeam}", "viewFilter={viewFilter}")
content = content.replace("setSelectedTeam={setSelectedTeam}", "setViewFilter={setViewFilter}")
content = content.replace("adminTab === 'team'", "adminTab === 'hierarchy'")
content = content.replace("setAdminTab('team')", "setAdminTab('hierarchy')")
content = content.replace("user.role === 'manager' ? 'team' : 'global'", "user.role === 'manager' ? 'hierarchy' : 'global'")
content = content.replace("user.role === 'manager' ? \"Team Dashboard\" : \"Global Dashboard\"", "user.role === 'manager' ? \"My Reports\" : \"Global Dashboard\"")
content = content.replace("My Team Dashboard", "My Reports Dashboard")
content = content.replace("My Team Overview", "My Reports Overview")

with open("frontend/app.jsx", "w") as f:
    f.write(content)
