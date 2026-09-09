import re
with open("frontend/app.jsx", "r") as f:
    text = f.read()

print("wfh:", "Submit Request" in text)
print("approver:", "approver_name" in text)
