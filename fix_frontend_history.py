with open("frontend/app.jsx", "r") as f:
    content = f.read()

old_td_wfh = """                  <td className="p-3 text-xs text-slate-600">
                      {r.approved_by ? <><span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : '-'}
                  </td>"""

new_td_wfh = """                  <td className="p-3 text-xs text-slate-600">
                      <div className="mb-1"><span className="text-slate-400">Approver:</span> <span className="font-bold">{r.approver_name || "Not Assigned"}</span></div>
                      {r.approved_by ? <><span className="text-slate-400">Action by:</span> <span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : ''}
                  </td>"""

old_td_ot = """                <td className="p-3 text-xs text-slate-600">
                    {r.approved_by ? <><span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : '-'}
                </td>"""

new_td_ot = """                <td className="p-3 text-xs text-slate-600">
                    <div className="mb-1"><span className="text-slate-400">Approver:</span> <span className="font-bold">{r.approver_name || "Not Assigned"}</span></div>
                    {r.approved_by ? <><span className="text-slate-400">Action by:</span> <span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : ''}
                </td>"""

content = content.replace(old_td_wfh, new_td_wfh)
content = content.replace(old_td_ot, new_td_ot)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
