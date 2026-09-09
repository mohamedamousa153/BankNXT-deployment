with open("frontend/app.jsx", "r") as f:
    content = f.read()

# Replace any h2 title based on user role
old_h2 = '        <h2 className="text-2xl font-bold text-slate-800">{user.role === \'manager\' ? "My Reports Dashboard" : "HR Analytics Dashboard"}</h2>'
new_h2 = '        <h2 className="text-2xl font-bold text-slate-800">{user.role === \'system_admin\' ? "HR Analytics Dashboard" : "My Reports Dashboard"}</h2>'
content = content.replace(old_h2, new_h2)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
