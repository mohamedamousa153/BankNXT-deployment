with open("frontend/app.jsx", "r") as f:
    content = f.read()

old_wfh = "const pendingWfh = filteredWfh.filter(r => r.status === 'Pending Approval');"
new_wfh = "const pendingWfh = filteredWfh.filter(r => r.status === 'Pending Approval' && (user.role === 'system_admin' || !r.approver_dn || r.approver_dn === user.user_dn));"

old_ot = "const pendingOt = filteredOt.filter(r => r.status === 'Pending Approval');"
new_ot = "const pendingOt = filteredOt.filter(r => r.status === 'Pending Approval' && (user.role === 'system_admin' || !r.approver_dn || r.approver_dn === user.user_dn));"

content = content.replace(old_wfh, new_wfh)
content = content.replace(old_ot, new_ot)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
