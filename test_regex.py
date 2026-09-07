with open("frontend/app.jsx", "r") as f:
    content = f.read()

content = content.replace("<TeamOverview ", "<HierarchyOverview ")
with open("frontend/app.jsx", "w") as f:
    f.write(content)
