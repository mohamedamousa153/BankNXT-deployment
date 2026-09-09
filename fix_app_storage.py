with open("frontend/app.jsx", "r") as f:
    content = f.read()

old_use_effect = """  useEffect(() => {
    const savedUser = localStorage.getItem("banknxt_user");
    if (savedUser) {
      const u = JSON.parse(savedUser);
      setUser(u);
      setActiveTab(u.is_admin ? "admin-dashboard" : "overtime");
    }
  }, []);"""

new_use_effect = """  useEffect(() => {
    try {
        const savedUser = localStorage.getItem("banknxt_user");
        if (savedUser && savedUser !== "undefined" && savedUser !== "null") {
          const u = JSON.parse(savedUser);
          if (u && typeof u === 'object') {
              setUser(u);
              setActiveTab(u.is_admin ? "admin-dashboard" : "overtime");
          }
        }
    } catch(e) {
        localStorage.removeItem("banknxt_user");
    }
  }, []);"""

content = content.replace(old_use_effect, new_use_effect)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
