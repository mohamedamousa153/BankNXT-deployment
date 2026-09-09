with open("frontend/app.jsx", "r") as f:
    content = f.read()

old_ot_submit = '<div className="col-span-2 flex justify-end"><button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button></div>'
new_ot_submit = '''<div className="col-span-2 flex justify-between items-center">
            <div className="text-sm text-slate-500">Manager / Approver: <span className="font-bold text-slate-700">{user.manager_name || "Not Assigned"}</span></div>
            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button>
          </div>'''

old_wfh_submit = '<div className="mt-6 flex justify-end"><button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button></div>'
new_wfh_submit = '''<div className="mt-6 flex justify-between items-center">
            <div className="text-sm text-slate-500">Manager / Approver: <span className="font-bold text-slate-700">{user.manager_name || "Not Assigned"}</span></div>
            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button>
          </div>'''

content = content.replace(old_ot_submit, new_ot_submit)
content = content.replace(old_wfh_submit, new_wfh_submit)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
