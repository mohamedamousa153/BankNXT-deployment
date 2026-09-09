with open("frontend/app.jsx", "r") as f:
    content = f.read()

old_sidebar = """          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-3 flex flex-col gap-1">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-3 pt-2">Menu</div>
            {!user.is_admin ? (
              <>
                <NavButton active={activeTab === 'overtime'} onClick={() => setActiveTab('overtime')} icon="🕒">Log Overtime</NavButton>
                <NavButton active={activeTab === 'wfh'} onClick={() => setActiveTab('wfh')} icon="🏠">Schedule WFH</NavButton>
              </>
            ) : (
              <>
                <NavButton active={activeTab === 'admin-dashboard'} onClick={() => setActiveTab('admin-dashboard')} icon={user.role === 'manager' ? "👥" : "📊"}>{user.role === 'manager' ? "My Reports" : "Global Dashboard"}</NavButton>
                {user.role === 'system_admin' && <NavButton active={activeTab === 'admin-settings'} onClick={() => setActiveTab('admin-settings')} icon="⚙️">Settings</NavButton>}
              </>
            )}
          </div>
        </aside>

        <main className="flex-1 bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden overflow-y-auto min-h-[80vh]">
          {!user.is_admin && activeTab === 'overtime' && <Overtime user={user} />}
          {!user.is_admin && activeTab === 'wfh' && <WFH user={user} />}
          {user.is_admin && activeTab === 'admin-dashboard' && <AdminDashboard user={user} />}
          {user.is_admin && activeTab === 'admin-settings' && <AdminSettings />}
        </main>"""

new_sidebar = """          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-3 flex flex-col gap-1">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-3 pt-2">Menu</div>
            <NavButton active={activeTab === 'overtime'} onClick={() => setActiveTab('overtime')} icon="🕒">Log Overtime</NavButton>
            <NavButton active={activeTab === 'wfh'} onClick={() => setActiveTab('wfh')} icon="🏠">Schedule WFH</NavButton>
            
            {(user.has_direct_reports || user.role === 'system_admin') && (
                <>
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-3 pt-4 border-t mt-2">Management</div>
                <NavButton active={activeTab === 'admin-dashboard'} onClick={() => setActiveTab('admin-dashboard')} icon={user.role === 'system_admin' ? "📊" : "👥"}>{user.role === 'system_admin' ? "Global Dashboard" : "My Reports"}</NavButton>
                </>
            )}
            {user.role === 'system_admin' && <NavButton active={activeTab === 'admin-settings'} onClick={() => setActiveTab('admin-settings')} icon="⚙️">Settings</NavButton>}
          </div>
        </aside>

        <main className="flex-1 bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden overflow-y-auto min-h-[80vh]">
          {activeTab === 'overtime' && <Overtime user={user} />}
          {activeTab === 'wfh' && <WFH user={user} />}
          {(user.has_direct_reports || user.role === 'system_admin') && activeTab === 'admin-dashboard' && <AdminDashboard user={user} />}
          {user.role === 'system_admin' && activeTab === 'admin-settings' && <AdminSettings />}
        </main>"""

content = content.replace(old_sidebar, new_sidebar)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
