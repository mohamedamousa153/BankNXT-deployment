
// Intercept fetch to automatically attach Authorization header
const originalFetch = window.fetch;
window.fetch = async (...args) => {
    let [resource, config] = args;
    const currentUser = JSON.parse(localStorage.getItem('banknxt_user') || 'null');
    
    if (currentUser && currentUser.employee_no && typeof resource === 'string' && resource.startsWith('/api/')) {
        config = config || {};
        config.headers = config.headers || {};
        if (!config.headers['Authorization']) {
            config.headers['Authorization'] = `Bearer ${currentUser.session_token || currentUser.employee_no}`;
        }
    }
    const response = await originalFetch(resource, config);
    if (response.status === 401 && resource !== '/api/login') {
        localStorage.removeItem('banknxt_user');
        window.location.reload();
    }
    return response;
};

const { useState, useEffect, useRef, useMemo } = React;

function formatDateTime(isoString) {
    if (!isoString) return "";
    const date = new Date(isoString);
    if (isNaN(date)) return isoString;
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) + " " + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatDateOnly(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    if (isNaN(date)) return dateString;
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function FlatpickrInput({ type, value, onChange, placeholder, required }) {
    const inputRef = useRef(null);
    const fpRef = useRef(null);
    useEffect(() => {
        const isTime = type === 'time';
        fpRef.current = flatpickr(inputRef.current, {
            enableTime: isTime,
            noCalendar: isTime,
            altInput: true,
            altFormat: isTime ? "h:i K" : "d M Y",
            dateFormat: isTime ? "H:i" : "Y-m-d",
            defaultDate: value,
            onChange: (selectedDates, dateStr) => onChange(dateStr)
        });
        return () => fpRef.current && fpRef.current.destroy();
    }, [type]);
    useEffect(() => {
        if (fpRef.current && !value) fpRef.current.clear();
    }, [value]);
    return <input ref={inputRef} required={required} className="w-full border p-2 rounded cursor-pointer" placeholder={placeholder} />;
}

// --- WFH Grid Logic ---
function getSunday(d) {
  d = new Date(d);
  var day = d.getDay();
  return new Date(d.setDate(d.getDate() - day));
}
function addDays(date, days) {
  var result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function getLocalYMD(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}


function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("overtime");
  
  useEffect(() => {
    const savedUser = localStorage.getItem("banknxt_user");
    if (savedUser) {
      const u = JSON.parse(savedUser);
      setUser(u);
      setActiveTab(u.is_admin ? "admin-dashboard" : "overtime");
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("banknxt_user");
    setUser(null);
  };

  if (!user) return <Login onLogin={u => { setUser(u); localStorage.setItem("banknxt_user", JSON.stringify(u)); setActiveTab(u.is_admin ? "admin-dashboard" : "overtime"); }} />;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2 rounded-lg font-bold text-xl tracking-tight leading-none">BankNXT</div>
          <h1 className="text-xl font-semibold text-slate-700 hidden sm:block">HR Portal</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">{user.is_admin ? "Administrator" : "Employee"}</span>
          <div className="flex items-center gap-2 border-l pl-4 border-slate-200">
            <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">{user.name.charAt(0)}</div>
            <div className="text-sm hidden sm:block">
              <p className="font-semibold leading-none">{user.name}</p>
              <p className="text-slate-500 text-xs">ID: {user.employee_no}</p>
            </div>
          </div>
          <button onClick={handleLogout} className="ml-2 text-sm text-red-600 hover:text-red-800 font-semibold">Logout</button>
        </div>
      </header>
      
      <div className="flex flex-1 max-w-[1400px] mx-auto w-full p-4 gap-6">
        <aside className="w-64 flex-shrink-0 flex flex-col gap-2">
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-3 flex flex-col gap-1">
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
        </main>
      </div>
    </div>
  );
}

function Login({ onLogin }) {
  const [empNo, setEmpNo] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault(); setError("");
    try {
      const res = await fetch("/api/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ employee_no: empNo, password }) });
      const data = await res.json();
      if (res.ok) onLogin(data); else setError(data.detail);
    } catch(err) { setError("Network error."); }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-sm w-full">
        <div className="text-center mb-8"><div className="inline-block bg-blue-600 text-white p-3 rounded-xl font-bold text-3xl mb-2">BankNXT</div><h2 className="text-xl font-semibold text-slate-700">HR Portal Login</h2></div>
        {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div><label className="block text-sm font-semibold mb-1">Employee ID</label><input type="text" required className="w-full border p-2.5 rounded-lg" value={empNo} onChange={e=>setEmpNo(e.target.value)} /></div>
          <div><label className="block text-sm font-semibold mb-1">Password</label><input type="password" required className="w-full border p-2.5 rounded-lg" value={password} onChange={e=>setPassword(e.target.value)} /></div>
          <button type="submit" className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg">Login</button>
        </form>
      </div>
    </div>
  );
}

function NavButton({ active, onClick, icon, children }) {
  return <button className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center gap-3 ${active ? 'bg-blue-50 text-blue-700 border border-blue-100' : 'hover:bg-slate-50 text-slate-600 hover:text-slate-900'}`} onClick={onClick}><span className="text-lg">{icon}</span>{children}</button>;
}

function StatusBadge({ status }) {
    const colors = {
        "Approved": "bg-green-100 text-green-800 border-green-200",
        "Pending Approval": "bg-yellow-100 text-yellow-800 border-yellow-200",
        "Submitted": "bg-blue-100 text-blue-800 border-blue-200",
        "Draft": "bg-gray-100 text-gray-800 border-gray-200",
        "Rejected": "bg-red-100 text-red-800 border-red-200",
        "Returned": "bg-orange-100 text-orange-800 border-orange-200"
    };
    return <span className={`${colors[status] || 'bg-slate-100'} border py-1 px-2 rounded-full text-xs font-bold whitespace-nowrap`}>{status}</span>;
}

// ============================
// EMPLOYEE OVERTIME
// ============================
function Overtime({ user }) {
  const [records, setRecords] = useState([]);
  const [formData, setFormData] = useState({ start_date: "", start_time: "", end_date: "", end_time: "", assigned_work: "", notes: "" });
  const [error, setError] = useState("");

  const fetchRecords = async () => {
    const res = await fetch(`/api/overtime?requester=${user.employee_no}`);
    const data = await res.json();
    setRecords(data.filter(r => r.employee_no === user.employee_no));
  };
  useEffect(() => { fetchRecords(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.start_date || !formData.start_time || !formData.end_date || !formData.end_time) {
        setError("Please complete all date and time fields."); return;
    }
    const stTime = formData.start_time.length === 5 ? `${formData.start_time}:00` : formData.start_time;
    const edTime = formData.end_time.length === 5 ? `${formData.end_time}:00` : formData.end_time;
    
    const res = await fetch("/api/overtime", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ 
        start_datetime: `${formData.start_date}T${stTime}`, 
        end_datetime: `${formData.end_date}T${edTime}`, 
        assigned_work: formData.assigned_work, notes: formData.notes, employee_no: user.employee_no, name: user.name, team_id: user.team_id 
    })});
    
    if(res.ok) { 
        setFormData({ start_date: "", start_time: "", end_date: "", end_time: "", assigned_work: "", notes: "" }); 
        setError(""); fetchRecords(); 
    } else { const err = await res.json(); setError(err.detail); }
  };
  
  const handleDelete = async (id) => { if(confirm("Cancel this request?")) { await fetch(`/api/overtime/${id}?requester=${user.employee_no}`, { method: "DELETE" }); fetchRecords(); } };

  return (
    <div>
      <div className="p-6 border-b bg-slate-50 flex justify-between"><h2 className="text-2xl font-bold">Log Overtime</h2></div>
      <div className="p-6">
        {error && <div className="bg-red-50 text-red-700 p-3 rounded mb-4 font-bold border border-red-200">{error}</div>}
        <form onSubmit={handleSubmit} className="bg-white border rounded-xl p-5 mb-8 shadow-sm grid grid-cols-2 gap-4">
          <div className="col-span-2 border-b pb-4"><h3 className="font-semibold mb-3">Time Entry (Supports AM/PM & Overnight)</h3>
            <div className="grid grid-cols-4 gap-4">
              <div><label className="block text-xs font-bold mb-1">Start Date</label><FlatpickrInput type="date" required={true} value={formData.start_date} onChange={v=>setFormData(prev=>({...prev, start_date:v}))} placeholder="Select Date"/></div>
              <div><label className="block text-xs font-bold mb-1">Start Time</label><FlatpickrInput type="time" required={true} value={formData.start_time} onChange={v=>setFormData(prev=>({...prev, start_time:v}))} placeholder="Select Time"/></div>
              <div><label className="block text-xs font-bold mb-1">End Date</label><FlatpickrInput type="date" required={true} value={formData.end_date} onChange={v=>setFormData(prev=>({...prev, end_date:v}))} placeholder="Select Date"/></div>
              <div><label className="block text-xs font-bold mb-1">End Time</label><FlatpickrInput type="time" required={true} value={formData.end_time} onChange={v=>setFormData(prev=>({...prev, end_time:v}))} placeholder="Select Time"/></div>
            </div>
          </div>
          <div><label className="block text-xs font-bold mb-1">Assigned Work</label><input type="text" required className="w-full border p-2 rounded" value={formData.assigned_work} onChange={e=>setFormData({...formData, assigned_work:e.target.value})}/></div>
          <div><label className="block text-xs font-bold mb-1">Notes</label><input type="text" className="w-full border p-2 rounded" value={formData.notes} onChange={e=>setFormData({...formData, notes:e.target.value})}/></div>
          <div className="col-span-2 flex justify-end"><button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button></div>
        </form>
        
        <h3 className="font-bold text-lg mb-4">My Past Records</h3>
        <div className="overflow-x-auto"><table className="w-full text-left text-sm border rounded-xl overflow-hidden"><thead className="bg-slate-50 border-b"><tr><th className="p-3">Start</th><th className="p-3">End</th><th className="p-3">Duration</th><th className="p-3">Status</th><th className="p-3">Approver Details</th><th className="p-3">Action</th></tr></thead>
          <tbody className="divide-y">{records.map(r => (
            <tr key={r.id}>
                <td className="p-3">{formatDateTime(r.start_datetime)}</td>
                <td className="p-3">{formatDateTime(r.end_datetime)}</td>
                <td className="p-3 font-bold text-blue-700">{r.duration_hours.toFixed(2)}h</td>
                <td className="p-3"><StatusBadge status={r.status}/></td>
                <td className="p-3 text-xs text-slate-600">
                    {r.approved_by ? <><span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : '-'}
                </td>
                <td className="p-3">{r.status === 'Pending Approval' && <button onClick={()=>handleDelete(r.id)} className="text-red-500 font-bold hover:underline">Cancel</button>}</td>
            </tr>
          ))}</tbody>
        </table></div>
      </div>
    </div>
  );
}

// ============================
// EMPLOYEE WFH
// ============================
function WFH({ user }) {
  const [records, setRecords] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  const existingWfhDates = useMemo(() => {
      const dates = new Set();
      records.forEach(r => {
          if (r.status === 'Rejected' || r.status === 'Cancelled' || r.status === 'Returned') return;
          if (r.selected_dates) {
              try { JSON.parse(r.selected_dates).forEach(d => dates.add(d)); } catch(e){}
          } else if (r.date) {
              let cur = new Date(r.date);
              let end = r.end_date ? new Date(r.end_date) : cur;
              while (cur <= end) {
                  dates.add(cur.toISOString().split('T')[0]);
                  cur.setDate(cur.getDate() + 1);
              }
          }
      });
      return dates;
  }, [records]);
  const [maxDays, setMaxDays] = useState(2);
  const [currentWeekSunday, setCurrentWeekMonday] = useState(getSunday(new Date()));
  const [selectedDates, setSelectedDates] = useState([]);
  const [formData, setFormData] = useState({ wfh_type: "Full Day", reason: "", start_time: "", end_time: "" });
  const [error, setError] = useState("");

  const fetchData = async (currentPage = page) => {
    const [wfhRes, setRes] = await Promise.all([
        fetch(`/api/wfh?employee_no=${user.employee_no}&page=${currentPage}&page_size=10`),
        fetch("/api/admin/settings")
    ]);
    const wfhData = await wfhRes.json();
    const setData = await setRes.json();
    setRecords(wfhData.items || []);
    setTotalPages(wfhData.total_pages || 1);
    setTotalRecords(wfhData.total || 0);
    setMaxDays(setData.max_wfh_days || 2);
  };
  useEffect(() => { fetchData(page); }, [page]);

  const handleDayClick = (dateStr) => {
      if (existingWfhDates.has(dateStr)) return;
      setError("");
      if (selectedDates.includes(dateStr)) {
          setSelectedDates(selectedDates.filter(d => d !== dateStr));
      } else {
          const getSundayStr = (dStr) => { const d = new Date(dStr); return getLocalYMD(new Date(d.setDate(d.getDate() - d.getDay()))); };
          const weekSunday = getSundayStr(dateStr);
          const selectedInWeek = selectedDates.filter(d => getSundayStr(d) === weekSunday).length;
          
          if (selectedInWeek >= maxDays) {
              setError(`Maximum ${maxDays} WFH days per week are allowed.`);
              return;
          }
          setSelectedDates([...selectedDates, dateStr].sort());
      }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedDates.length === 0) { setError("Please select at least one day from the calendar."); return; }
    setError("");
    const res = await fetch("/api/wfh", { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ 
            ...formData, 
            selected_dates: JSON.stringify(selectedDates),
            employee_no: user.employee_no, 
            name: user.name,
            team_id: user.team_id 
        }) 
    });
    if (res.ok) { 
        setFormData({ wfh_type: "Full Day", reason: "", start_time: "", end_time: "" }); 
        setSelectedDates([]);
        fetchData(); 
    }
    else { const err = await res.json(); setError(err.detail); }
  };
  
  const handleDelete = async (id) => { if(confirm("Cancel this request?")) { await fetch(`/api/wfh/${id}?requester=${user.employee_no}`, { method: "DELETE" }); fetchData(page); } };

  // Generate Week Days (Mon - Fri)
  const weekDays = [];
  for (let i = 0; i < 5; i++) {
      const d = addDays(currentWeekSunday, i);
      const dateStr = getLocalYMD(d); // YYYY-MM-DD
      const dayName = d.toLocaleDateString('en-US', { weekday: 'long' });
      const shortDate = d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
      weekDays.push({ dateStr, dayName, shortDate });
  }

  return (
    <div>
      <div className="p-6 border-b bg-slate-50 flex justify-between"><h2 className="text-2xl font-bold">Schedule WFH</h2></div>
      <div className="p-6">
        {error && <div className="bg-red-50 text-red-700 p-3 rounded mb-4 font-bold border border-red-200">{error}</div>}
        <form onSubmit={handleSubmit} className="bg-white border rounded-xl p-5 mb-8 shadow-sm">
          <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-lg">Select WFH Days</h3>
              <div className="flex gap-2 items-center bg-slate-100 rounded-lg p-1">
                  <button type="button" onClick={()=>setCurrentWeekMonday(addDays(currentWeekSunday, -7))} className="px-3 py-1 bg-white shadow-sm rounded text-sm font-medium hover:bg-slate-50">&lt; Previous Week</button>
                  <button type="button" onClick={()=>setCurrentWeekMonday(getSunday(new Date()))} className="px-3 py-1 text-sm font-medium hover:text-blue-600">Current Week</button>
                  <button type="button" onClick={()=>setCurrentWeekMonday(addDays(currentWeekSunday, 7))} className="px-3 py-1 bg-white shadow-sm rounded text-sm font-medium hover:bg-slate-50">Next Week &gt;</button>
              </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
              {weekDays.map(day => {
                  const isSelected = selectedDates.includes(day.dateStr);
                  const isExisting = existingWfhDates.has(day.dateStr);
                  return (
                      <div 
                          key={day.dateStr} 
                          onClick={() => handleDayClick(day.dateStr)}
                          className={`border rounded-xl p-4 transition-all ${isExisting ? 'bg-slate-100 opacity-60 cursor-not-allowed border-slate-200' : isSelected ? 'bg-blue-50 border-blue-500 shadow-[0_0_0_2px_rgba(59,130,246,0.3)] cursor-pointer' : 'bg-white hover:border-blue-300 hover:bg-slate-50 cursor-pointer'}`}
                      >
                          <div className={`font-bold mb-1 flex justify-between items-center ${isExisting ? 'text-slate-400' : isSelected ? 'text-blue-700' : 'text-slate-700'}`}>
                              {day.dayName} {isSelected && <span>✓</span>} {isExisting && <span className="text-[10px] uppercase bg-slate-200 px-2 py-0.5 rounded text-slate-500">Booked</span>}
                          </div>
                          <div className={`text-sm ${isExisting ? 'text-slate-400' : isSelected ? 'text-blue-600' : 'text-slate-500'}`}>{day.shortDate}</div>
                      </div>
                  )
              })}
          </div>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
              <div><label className="block text-xs font-bold mb-1">WFH Type</label><select className="w-full border p-2 rounded" value={formData.wfh_type} onChange={e=>setFormData({...formData, wfh_type: e.target.value})}><option>Full Day</option><option>Half Day</option><option>Partial Hour</option></select></div>
              <div><label className="block text-xs font-bold mb-1">Reason</label><input type="text" className="w-full border p-2 rounded" value={formData.reason} onChange={e=>setFormData({...formData, reason: e.target.value})}/></div>
              {formData.wfh_type === 'Partial Hour' && (<>
                  <div><label className="block text-xs font-bold mb-1">Start Time</label><FlatpickrInput type="time" value={formData.start_time} onChange={v=>setFormData(prev=>({...prev, start_time: v}))} placeholder="AM/PM Time"/></div>
                  <div><label className="block text-xs font-bold mb-1">End Time</label><FlatpickrInput type="time" value={formData.end_time} onChange={v=>setFormData(prev=>({...prev, end_time: v}))} placeholder="AM/PM Time"/></div>
              </>)}
          </div>
          <div className="mt-6 flex justify-end"><button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button></div>
        </form>

        <h3 className="font-bold text-lg mb-4">My WFH History</h3>
        <div className="overflow-x-auto"><table className="w-full text-left text-sm border rounded-xl overflow-hidden"><thead className="bg-slate-50 border-b"><tr><th className="p-3">Req ID</th><th className="p-3">Selected Dates</th><th className="p-3">Type</th><th className="p-3">Reason</th><th className="p-3">Submitted</th><th className="p-3">Status</th><th className="p-3">Approver Details</th><th className="p-3">Action</th></tr></thead>
          <tbody className="divide-y">{records.map(r => {
              // Handle discrete selected dates natively
              let datesDisplay = "-";
              if (r.selected_dates) {
                  try {
                      datesDisplay = JSON.parse(r.selected_dates).map(d => formatDateOnly(d)).join(<br/>);
                  } catch(e){}
              } else {
                  datesDisplay = formatDateOnly(r.date) + (r.end_date && r.end_date !== r.date ? ` ➡️ ${formatDateOnly(r.end_date)}` : '');
              }

              return (
              <tr key={r.id}>
                  <td className="p-3 font-semibold text-slate-500">#{r.id}</td>
                  <td className="p-3 font-bold text-blue-700 bg-blue-50/50">
                      {r.selected_dates ? (
                         <div className="flex flex-col gap-1">
                             {JSON.parse(r.selected_dates).map(d => <span key={d}>{formatDateOnly(d)}</span>)}
                         </div>
                      ) : (
                          <>{formatDateOnly(r.date)} {r.end_date && r.end_date !== r.date ? ` ➡️ ${formatDateOnly(r.end_date)}` : ''}</>
                      )}
                  </td>
                  <td className="p-3">{r.wfh_type}</td>
                  <td className="p-3">{r.reason}</td>
                  <td className="p-3 text-xs">{formatDateOnly(r.created_at)}</td>
                  <td className="p-3"><StatusBadge status={r.status}/></td>
                  <td className="p-3 text-xs text-slate-600">
                      {r.approved_by ? <><span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : '-'}
                  </td>
                  <td className="p-3">{r.status === 'Pending Approval' && <button onClick={()=>handleDelete(r.id)} className="text-red-500 font-bold hover:underline">Cancel</button>}</td>
              </tr>
            )
          })}</tbody>
        </table></div>
      </div>
    </div>
  );
}

// ============================
// ADMIN DASHBOARD (ANALYTICS)
// ============================

function HierarchyOverview({ wfh, overtime, hierarchy, users, viewFilter, setViewFilter, dateFilter, formatDateOnly, getWFHDaysCount, user, handleAction }) {
    // viewFilter: 'direct' or 'all'
    const displayUsers = viewFilter === 'direct' ? hierarchy.direct_reports : hierarchy.all_subordinates;
    const memberNos = new Set(displayUsers.map(u => String(u.employee_no)));
    
    const teamWfh = wfh.filter(r => memberNos.has(String(r.employee_no)));
    const teamOt = overtime.filter(r => memberNos.has(String(r.employee_no)));
    
    const totalWfhDays = teamWfh.reduce((acc, r) => acc + getWFHDaysCount(r), 0);
    const pendingWfh = teamWfh.filter(r => r.status === 'Pending Approval').length;
    const totalOtHours = teamOt.reduce((acc, r) => acc + (r.duration_hours || 0), 0);
    const pendingOt = teamOt.filter(r => r.status === 'Pending Approval').length;

    const wfhToday = teamWfh.filter(r => {
        if (!r.selected_dates) return false;
        try {
            return JSON.parse(r.selected_dates).includes(formatDateOnly(new Date()));
        } catch { return false; }
    });

    const empSummary = displayUsers.map(emp => {
        const empWfh = teamWfh.filter(r => String(r.employee_no) === String(emp.employee_no));
        const empOt = teamOt.filter(r => String(r.employee_no) === String(emp.employee_no));
        return {
            ...emp,
            wfh_count: empWfh.reduce((acc, r) => acc + getWFHDaysCount(r), 0),
            wfh_pending: empWfh.filter(r => r.status === 'Pending Approval').length,
            ot_hours: empOt.reduce((acc, r) => acc + (r.duration_hours || 0), 0),
            ot_pending: empOt.filter(r => r.status === 'Pending Approval').length
        };
    }).sort((a,b) => b.wfh_count - a.wfh_count);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                <h3 className="text-xl font-bold text-slate-800">My Reports Dashboard</h3>
                <div className="flex gap-4 items-center">
                    <select className="border rounded-lg p-2 font-medium text-slate-700" value={viewFilter} onChange={e => setViewFilter(e.target.value)}>
                        <option value="direct">Direct Reports ({hierarchy.direct_reports.length})</option>
                        <option value="all">All Subordinates ({hierarchy.all_subordinates.length})</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Total Employees</div>
                    <p className="text-2xl font-black text-slate-700">{displayUsers.length}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Pending WFH</div>
                    <p className="text-2xl font-black text-blue-600">{pendingWfh}</p>
                    <p className="text-xs text-slate-400 mt-1">{totalWfhDays} total WFH days</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Pending Overtime</div>
                    <p className="text-2xl font-black text-amber-600">{pendingOt}</p>
                    <p className="text-xs text-slate-400 mt-1">{totalOtHours} total hours</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <div className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">WFH Today</div>
                    <p className="text-2xl font-black text-emerald-600">{wfhToday.length}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="font-bold text-slate-700 mb-4">Pending WFH Approvals</h3>
                    <div className="space-y-3">
                        {teamWfh.filter(r => r.status === 'Pending Approval').length > 0 ? (
                            teamWfh.filter(r => r.status === 'Pending Approval').map(r => (
                                <div key={r.id} className="border p-3 rounded-lg flex justify-between items-center">
                                    <div>
                                        <p className="font-bold">{r.name} ({r.employee_no})</p>
                                        <p className="text-sm text-slate-500">{getWFHDaysCount(r)} Days: {r.selected_dates ? JSON.parse(r.selected_dates).join(', ') : r.date}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={() => handleAction('wfh', r.id, 'Approved')} className="bg-emerald-500 text-white px-3 py-1 rounded text-sm hover:bg-emerald-600 font-bold">Approve</button>
                                        <button onClick={() => handleAction('wfh', r.id, 'Rejected')} className="bg-rose-500 text-white px-3 py-1 rounded text-sm hover:bg-rose-600 font-bold">Reject</button>
                                    </div>
                                </div>
                            ))
                        ) : <p className="text-slate-400 text-sm">No pending requests.</p>}
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="font-bold text-slate-700 mb-4">Pending Overtime Approvals</h3>
                    <div className="space-y-3">
                        {teamOt.filter(r => r.status === 'Pending Approval').length > 0 ? (
                            teamOt.filter(r => r.status === 'Pending Approval').map(r => (
                                <div key={r.id} className="border p-3 rounded-lg flex justify-between items-center">
                                    <div>
                                        <p className="font-bold">{r.name} ({r.employee_no})</p>
                                        <p className="text-sm text-slate-500">{r.start_datetime.split('T')[0]} - {r.duration_hours} hrs</p>
                                        <p className="text-xs text-slate-400 truncate w-48">{r.assigned_work}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={() => handleAction('overtime', r.id, 'Approved')} className="bg-emerald-500 text-white px-3 py-1 rounded text-sm hover:bg-emerald-600 font-bold">Approve</button>
                                        <button onClick={() => handleAction('overtime', r.id, 'Rejected')} className="bg-rose-500 text-white px-3 py-1 rounded text-sm hover:bg-rose-600 font-bold">Reject</button>
                                    </div>
                                </div>
                            ))
                        ) : <p className="text-slate-400 text-sm">No pending requests.</p>}
                    </div>
                </div>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <h3 className="font-bold text-slate-700 mb-4">Employee Overview ({displayUsers.length})</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-600">
                            <tr>
                                <th className="p-3 rounded-tl-lg">Employee</th>
                                <th className="p-3">Manager</th>
                                <th className="p-3 text-center">WFH Days (Total)</th>
                                <th className="p-3 text-center">WFH Pending</th>
                                <th className="p-3 text-center">OT Hours (Total)</th>
                                <th className="p-3 text-center rounded-tr-lg">OT Pending</th>
                            </tr>
                        </thead>
                        <tbody>
                            {empSummary.map(emp => (
                                <tr key={emp.employee_no} className="border-b last:border-0 hover:bg-slate-50">
                                    <td className="p-3 font-medium">{emp.name} ({emp.employee_no})</td>
                                    <td className="p-3">{emp.manager_name || 'N/A'}</td>
                                    <td className="p-3 text-center">{emp.wfh_count}</td>
                                    <td className="p-3 text-center text-blue-600 font-bold">{emp.wfh_pending > 0 ? emp.wfh_pending : '-'}</td>
                                    <td className="p-3 text-center">{emp.ot_hours}</td>
                                    <td className="p-3 text-center text-amber-600 font-bold">{emp.ot_pending > 0 ? emp.ot_pending : '-'}</td>
                                </tr>
                            ))}
                            {empSummary.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="p-4 text-center text-slate-500">No employees found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function AdminSettings() {
    const [settings, setSettings] = useState({ admin_email: "", max_wfh_days: 2 });
    const [msg, setMsg] = useState("");

    useEffect(() => {
        fetch("/api/admin/settings").then(r=>r.json()).then(data => setSettings(data));
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        const res = await fetch("/api/admin/settings", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(settings) });
        if(res.ok) { setMsg("Settings saved successfully!"); setTimeout(()=>setMsg(""), 3000); } 
        else { setMsg("Error saving settings."); }
    };

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-6">System Settings</h2>
            {msg && <div className="bg-green-100 text-green-800 p-3 rounded mb-4 font-bold border border-green-200">{msg}</div>}
            <form onSubmit={handleSave} className="bg-white border rounded-xl p-6 shadow-sm max-w-lg">
                <h3 className="font-bold border-b pb-2 mb-4">Email Notifications</h3>
                <div className="mb-4">
                    <label className="block text-sm font-semibold mb-2">Admin / Recipient Email Address</label>
                    <input type="email" required className="w-full border p-2.5 rounded-lg" value={settings.admin_email} onChange={e=>setSettings({...settings, admin_email: e.target.value})} />
                </div>
                <h3 className="font-bold border-b pb-2 mb-4 mt-6">Company Policy</h3>
                <div className="mb-4">
                    <label className="block text-sm font-semibold mb-2">Max WFH Days Per Week</label>
                    <input type="number" min="1" max="7" required className="w-full border p-2.5 rounded-lg" value={settings.max_wfh_days} onChange={e=>setSettings({...settings, max_wfh_days: parseInt(e.target.value)})} />
                </div>
                <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 transition-colors mt-2">Save Settings</button>
            </form>
            
            <div className="mt-8">
                <LDAPSettingsPage />
            </div>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
