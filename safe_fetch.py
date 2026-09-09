with open("frontend/app.jsx", "r") as f:
    content = f.read()

old_fetch = """      setWfh(await wfhRes.json());
      setOvertime(await otRes.json());
      setHierarchy(await teamRes.json());
      setUsers(await userRes.json());"""

new_fetch = """      const wData = await wfhRes.json();
      const oData = await otRes.json();
      const hData = await teamRes.json();
      const uData = await userRes.json();
      
      setWfh(Array.isArray(wData) ? wData : (wData.items ? wData.items : []));
      setOvertime(Array.isArray(oData) ? oData : (oData.items ? oData.items : []));
      setHierarchy(hData && hData.direct_reports ? hData : {direct_reports: [], all_subordinates: []});
      setUsers(Array.isArray(uData) ? uData : []);"""

content = content.replace(old_fetch, new_fetch)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
