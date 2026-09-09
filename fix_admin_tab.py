with open("frontend/app.jsx", "r") as f:
    content = f.read()

content = content.replace("user.role === 'manager' ? 'hierarchy' : 'global'", "user.role === 'system_admin' ? 'global' : 'hierarchy'")

with open("frontend/app.jsx", "w") as f:
    f.write(content)
