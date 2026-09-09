
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  componentDidCatch(error, errorInfo) {
    this.setState({ hasError: true, error: error, errorInfo: errorInfo });
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', background: '#fee', color: '#900', border: '1px solid #c00', margin: '20px', borderRadius: '8px', fontFamily: 'monospace' }}>
          <h2>Something went wrong.</h2>
          <p><b>{this.state.error && this.state.error.toString()}</b></p>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function safeJSONParse(str, fallback = []) {
    if (!str) return fallback;
    try {
        return JSON.parse(str);
    } catch(e) {
        return fallback;
    }
}

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
          <div className="col-span-2 flex justify-between items-center">
            <div className="text-sm text-slate-500">Manager / Approver: <span className="font-bold text-slate-700">{user.manager_name || "Not Assigned"}</span></div>
            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button>
          </div>
        </form>
        
        <h3 className="font-bold text-lg mb-4">My Past Records</h3>
        <div className="overflow-x-auto"><table className="w-full text-left text-sm border rounded-xl overflow-hidden"><thead className="bg-slate-50 border-b"><tr><th className="p-3">Start</th><th className="p-3">End</th><th className="p-3">Duration</th><th className="p-3">Status</th><th className="p-3">Approver Details</th><th className="p-3">Action</th></tr></thead>
          <tbody className="divide-y">{records.map(r => (
            <tr key={r.id}>
                <td className="p-3">{formatDateTime(r.start_datetime)}</td>
                <td className="p-3">{formatDateTime(r.end_datetime)}</td>
                <td className="p-3 font-bold text-blue-700">{(r.duration_hours || 0).toFixed(2)}h</td>
                <td className="p-3"><StatusBadge status={r.status}/></td>
                <td className="p-3 text-xs text-slate-600">
                    <div className="mb-1"><span className="text-slate-400">Approver:</span> <span className="font-bold">{r.approver_name || "Not Assigned"}</span></div>
                    {r.approved_by ? <><span className="text-slate-400">Action by:</span> <span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : ''}
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
              try { safeJSONParse(r.selected_dates, []).forEach(d => dates.add(d)); } catch(e){}
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
          <div className="mt-6 flex justify-between items-center">
            <div className="text-sm text-slate-500">Manager / Approver: <span className="font-bold text-slate-700">{user.manager_name || "Not Assigned"}</span></div>
            <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded font-bold hover:bg-blue-700 transition-colors">Submit Request</button>
          </div>
        </form>

        <h3 className="font-bold text-lg mb-4">My WFH History</h3>
        <div className="overflow-x-auto"><table className="w-full text-left text-sm border rounded-xl overflow-hidden"><thead className="bg-slate-50 border-b"><tr><th className="p-3">Req ID</th><th className="p-3">Selected Dates</th><th className="p-3">Type</th><th className="p-3">Reason</th><th className="p-3">Submitted</th><th className="p-3">Status</th><th className="p-3">Approver Details</th><th className="p-3">Action</th></tr></thead>
          <tbody className="divide-y">{records.map(r => {
              // Handle discrete selected dates natively
              let datesDisplay = "-";
              if (r.selected_dates) {
                  try {
                      datesDisplay = safeJSONParse(r.selected_dates, []).map(d => formatDateOnly(d)).join(<br/>);
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
                             {safeJSONParse(r.selected_dates, []).map(d => <span key={d}>{formatDateOnly(d)}</span>)}
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
                      <div className="mb-1"><span className="text-slate-400">Approver:</span> <span className="font-bold">{r.approver_name || "Not Assigned"}</span></div>
                      {r.approved_by ? <><span className="text-slate-400">Action by:</span> <span className="font-bold text-slate-800">{r.approved_by}</span><br/>{formatDateTime(r.approval_date)}<br/><i className="text-slate-500">{r.manager_comment}</i></> : ''}
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
            return safeJSONParse(r.selected_dates, []).includes(formatDateOnly(new Date()));
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
                                        <p className="text-sm text-slate-500">{getWFHDaysCount(r)} Days: {r.selected_dates ? safeJSONParse(r.selected_dates, []).join(', ') : r.date}</p>
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

function LDAPSettingsPage({ user }) {
  const [config, setConfig] = useState(null);
  const [msg, setMsg] = useState("");
  const [isError, setIsError] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetch('/api/admin/ldap/config')
    .then(r => r.json())
    .then(data => {
        // Ensure defaults if missing
        setConfig({
            ...data,
            server_url: data.server_url || '',
            base_dn: data.base_dn || '',
            bind_username: data.bind_username || '',
            bind_password: data.bind_password || '',
            user_search_base: data.user_search_base || '',
            user_search_filter: data.user_search_filter || '',
            group_search_base: data.group_search_base || '',
            group_membership_attr: data.group_membership_attr || 'uniqueMember',
            group_sysadmin: data.group_sysadmin || '',
            group_manager: data.group_manager || '',
            group_employee: data.group_employee || ''
        });
    });
  }, [user]);

  const handleChange = (e) => {
      const { name, value, type, checked } = e.target;
      setConfig(prev => ({
          ...prev,
          [name]: type === 'checkbox' ? checked : value
      }));
  };

  const handleSave = async (e) => {
      e.preventDefault();
      try {
          const res = await fetch('/api/admin/ldap/config', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(config)
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || 'Error saving');
          setConfig(data);
          setMsg("Configuration saved successfully.");
          setIsError(false);
          setTimeout(() => setMsg(""), 3000);
      } catch (err) {
          setMsg(err.message);
          setIsError(true);
      }
  };

  const handleTest = async () => {
      setTesting(true);
      setMsg("Testing connection...");
      setIsError(false);
      try {
          const res = await fetch('/api/admin/ldap/test-connection', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(config)
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || 'Connection failed');
          setMsg(`✓ ${data.message}`);
          setIsError(false);
      } catch (err) {
          setMsg(`✗ LDAP connection failed: ${err.message}`);
          setIsError(true);
      } finally {
          setTesting(false);
      }
  };

  if (!config) return <div className="p-6">Loading configuration...</div>;

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-slate-800 mb-6">LDAP / Active Directory Configuration</h2>
        
        {msg && (
            <div className={`p-4 rounded-lg mb-6 font-bold ${isError ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
                {msg}
            </div>
        )}
        
        <form onSubmit={handleSave} className="space-y-8">
            {/* Status */}
            <div>
                <label className="flex items-center gap-2 font-bold text-slate-700">
                    <input type="checkbox" name="enabled" checked={config.enabled} onChange={handleChange} className="w-5 h-5 text-blue-600 rounded" />
                    Enable LDAP Authentication
                </label>
                <p className="text-sm text-slate-500 mt-1 ml-7">If disabled, the system will use local authentication.</p>
            </div>

            {/* Connection */}
            <div>
                <h3 className="font-bold text-lg border-b pb-2 mb-4 text-slate-800">Connection Settings</h3>
                <div className="grid grid-cols-2 gap-4">
                    <div><label className="block text-xs font-bold mb-1">LDAP Server Host / IP</label><input type="text" name="server_url" value={config.server_url} onChange={handleChange} className="w-full border p-2 rounded" placeholder="e.g. 10.10.10.10 or ldap.example.com" /></div>
                    <div><label className="block text-xs font-bold mb-1">Port</label><input type="number" name="port" value={config.port} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                    <div><label className="block text-xs font-bold mb-1">Protocol</label>
                        <select name="protocol" value={config.protocol} onChange={handleChange} className="w-full border p-2 rounded">
                            <option value="LDAP">LDAP</option>
                            <option value="LDAPS">LDAPS</option>
                        </select>
                    </div>
                    <div className="flex items-center mt-6">
                        <label className="flex items-center gap-2 font-bold text-sm text-slate-700">
                            <input type="checkbox" name="use_tls" checked={config.use_tls} onChange={handleChange} className="w-4 h-4 rounded" /> Enable SSL/TLS
                        </label>
                    </div>
                    <div className="col-span-2"><label className="block text-xs font-bold mb-1">Base DN</label><input type="text" name="base_dn" value={config.base_dn} onChange={handleChange} className="w-full border p-2 rounded" placeholder="e.g. DC=example,DC=local" /></div>
                    <div><label className="block text-xs font-bold mb-1">Bind Username (DN)</label><input type="text" name="bind_username" value={config.bind_username} onChange={handleChange} className="w-full border p-2 rounded" placeholder="e.g. CN=admin,OU=Service Accounts,DC=..." /></div>
                    <div><label className="block text-xs font-bold mb-1">Bind Password</label><input type="password" name="bind_password" value={config.bind_password} onChange={handleChange} className="w-full border p-2 rounded" placeholder={config.bind_password === "********" ? "******** (Configured)" : "Enter new password to change"} /></div>
                    <div><label className="block text-xs font-bold mb-1">Connection Timeout (seconds)</label><input type="number" name="timeout" value={config.timeout} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                </div>
                <div className="mt-4">
                    <button type="button" onClick={handleTest} disabled={testing} className="bg-slate-800 text-white px-4 py-2 rounded font-bold hover:bg-slate-700 disabled:opacity-50 transition-colors">
                        {testing ? "Testing..." : "Test Connection"}
                    </button>
                </div>
            </div>

            {/* User Mapping */}
            <div>
                <h3 className="font-bold text-lg border-b pb-2 mb-4 text-slate-800">User Mapping & Search</h3>
                <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2"><label className="block text-xs font-bold mb-1">User Search Base DN (Optional)</label><input type="text" name="user_search_base" value={config.user_search_base} onChange={handleChange} className="w-full border p-2 rounded" placeholder="Leave empty to use global Base DN" /></div>
                    <div className="col-span-2"><label className="block text-xs font-bold mb-1">User Search Filter</label><input type="text" name="user_search_filter" value={config.user_search_filter} onChange={handleChange} className="w-full border p-2 rounded" placeholder="e.g. (objectClass=person)" /></div>
                    
                    <div><label className="block text-xs font-bold mb-1">Username Attribute</label><input type="text" name="attr_username" value={config.attr_username} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                    <div><label className="block text-xs font-bold mb-1">Employee Number Attribute</label><input type="text" name="attr_employee_no" value={config.attr_employee_no} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                    <div><label className="block text-xs font-bold mb-1">Display Name Attribute</label><input type="text" name="attr_display_name" value={config.attr_display_name} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                    <div><label className="block text-xs font-bold mb-1">Email Attribute</label><input type="text" name="attr_email" value={config.attr_email} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                    <div><label className="block text-xs font-bold mb-1">Manager Attribute</label><input type="text" name="attr_manager" value={config.attr_manager} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                    <div><label className="block text-xs font-bold mb-1">Department/Team Attribute</label><input type="text" name="attr_department" value={config.attr_department} onChange={handleChange} className="w-full border p-2 rounded" /></div>
                </div>
            </div>

            {/* Group Mapping */}
            <div>
                <h3 className="font-bold text-lg border-b pb-2 mb-4 text-slate-800">Group & Role Mapping</h3>
                <div className="grid grid-cols-1 gap-4">
                    <div><label className="block text-xs font-bold mb-1">System Admin Group DN</label><input type="text" name="group_sysadmin" value={config.group_sysadmin} onChange={handleChange} className="w-full border p-2 rounded" placeholder="e.g. CN=HRPortal-Admins,OU=Groups,DC=..." /></div>
                    <div><label className="block text-xs font-bold mb-1">Manager / Team Head Group DN</label><input type="text" name="group_manager" value={config.group_manager} onChange={handleChange} className="w-full border p-2 rounded" placeholder="e.g. CN=HRPortal-Managers,OU=Groups,DC=..." /></div>
                    <div><label className="block text-xs font-bold mb-1">Employee Group DN</label><input type="text" name="group_employee" value={config.group_employee} onChange={handleChange} className="w-full border p-2 rounded" placeholder="e.g. CN=HRPortal-Employees,OU=Groups,DC=..." /></div>
                </div>
            </div>

            <div className="pt-4 border-t">
                <button type="submit" className="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors w-full">Save Configuration</button>
            </div>
        </form>
    </div>
  );
}

function AdminDashboard({ user }) {
  const [rechartsLoaded, setRechartsLoaded] = useState(!!window.Recharts);
  
  useEffect(() => {
      if (window.Recharts) return;
      const interval = setInterval(() => {
          if (window.Recharts) {
              setRechartsLoaded(true);
              clearInterval(interval);
          }
      }, 200);
      return () => clearInterval(interval);
  }, []);

  const Recharts = window.Recharts || {};
  const { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } = Recharts;

  const [overtime, setOvertime] = useState([]);
  const [wfh, setWfh] = useState([]);
  const [dateFilter, setDateFilter] = useState("This Month");

  const [hierarchy, setHierarchy] = useState({direct_reports: [], all_subordinates: []});
  const [viewFilter, setViewFilter] = useState('direct');
  const [users, setUsers] = useState([]);
  const [adminTab, setAdminTab] = useState(user.role === 'manager' ? 'hierarchy' : 'global');
  

  const fetchData = async () => {
      const [wfhRes, otRes, teamRes, userRes] = await Promise.all([
          fetch(`/api/wfh?requester=${user.employee_no}`),
          fetch(`/api/overtime?requester=${user.employee_no}`),
          fetch(`/api/users/hierarchy`),
          fetch(`/api/users?requester=${user.employee_no}`)
      ]);
      const wData = await wfhRes.json();
      const oData = await otRes.json();
      const hData = await teamRes.json();
      const uData = await userRes.json();
      
      setWfh(Array.isArray(wData) ? wData : (wData.items ? wData.items : []));
      setOvertime(Array.isArray(oData) ? oData : (oData.items ? oData.items : []));
      setHierarchy(hData && hData.direct_reports ? hData : {direct_reports: [], all_subordinates: []});
      setUsers(Array.isArray(uData) ? uData : []);
  };
  useEffect(() => { fetchData(); }, []);

  const handleAction = async (type, id, newStatus) => {
    let comment = "";
    if (newStatus === "Rejected" || newStatus === "Returned") {
        comment = prompt(`Please enter a reason for marking this as ${newStatus}:`);
        if (comment === null) return; 
    }
    const endpoint = type === 'wfh' ? `/api/wfh/${id}?requester=${user.employee_no}` : `/api/overtime/${id}?requester=${user.employee_no}`;
    await fetch(endpoint, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: newStatus, manager_comment: comment, approved_by: user.name }) });
    fetchData();
  };

  // FILTERING LOGIC
  const filterByDateRange = (dateStr) => {
      if (!dateStr) return false;
      const d = new Date(dateStr);
      const now = new Date();
      if (dateFilter === "Today") return d.toDateString() === now.toDateString();
      if (dateFilter === "This Week") {
          const mon = getSunday(now);
          return d >= mon && d <= addDays(mon, 6);
      }
      if (dateFilter === "This Month") return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
      if (dateFilter === "Last Month") return d.getMonth() === (now.getMonth() - 1 + 12) % 12 && d.getFullYear() === (now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear());
      if (dateFilter === "This Year") return d.getFullYear() === now.getFullYear();
      return true; // All Time
  };

  const isWfhInDateRange = (r) => {
      if (r.selected_dates) {
          try {
              const dates = safeJSONParse(r.selected_dates, []);
              return dates.some(d => filterByDateRange(d));
          } catch(e) { return false; }
      }
      
      if (r.date) {
          let cur = new Date(r.date);
          let end = r.end_date ? new Date(r.end_date) : cur;
          while (cur <= end) {
              if (filterByDateRange(cur.toISOString())) return true;
              cur.setDate(cur.getDate() + 1);
          }
      }
      return false;
  };
  const filteredWfh = wfh.filter(isWfhInDateRange);
  const filteredOt = overtime.filter(r => filterByDateRange(r.created_at || r.start_datetime));

  // Flatten WFH days for accurate date-range analytics
  const flattenedWfhDays = [];
  filteredWfh.forEach(r => {
      if (r.selected_dates) {
          try {
              safeJSONParse(r.selected_dates, []).forEach(d => {
                  if (filterByDateRange(d)) flattenedWfhDays.push({ ...r, exact_date: d });
              });
          } catch(e) {}
      } else if (r.date) {
          let cur = new Date(r.date);
          let end = r.end_date ? new Date(r.end_date) : cur;
          while (cur <= end) {
              const dStr = cur.toISOString();
              if (filterByDateRange(dStr)) flattenedWfhDays.push({ ...r, exact_date: dStr });
              cur.setDate(cur.getDate() + 1);
          }
      }
  });

  const getWFHDaysCount = (r) => r.selected_dates ? safeJSONParse(r.selected_dates, []).length : (r.end_date && r.end_date !== r.date ? 2 : 1);
  const totalWFHDays = flattenedWfhDays.length;
  const approvedWfh = filteredWfh.filter(r => r.status === 'Approved').length;
  
  const totalOTHours = filteredOt.reduce((acc, r) => acc + (r.duration_hours || 0), 0);
  const approvedOt = filteredOt.filter(r => r.status === 'Approved').length;
  
  // Overnight OT calculation
  const overnightOt = filteredOt.filter(r => {
      const s = new Date(r.start_datetime).toDateString();
      const e = new Date(r.end_datetime).toDateString();
      return s !== e;
  }).reduce((acc, r) => acc + (r.duration_hours || 0), 0);

  const uniqueEmpWfh = new Set(filteredWfh.map(r => r.employee_no)).size;
  const uniqueEmpOt = new Set(filteredOt.map(r => r.employee_no)).size;

  // WFH Days by Weekday (Chart 1)
  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu"];
  const wfhByDayObj = {};
  flattenedWfhDays.forEach(r => {
      const day = new Date(r.exact_date).toLocaleDateString('en-US', {weekday: 'short'});
      wfhByDayObj[day] = (wfhByDayObj[day] || 0) + 1;
  });
  const wfhByDayChart = daysOfWeek.map(k => ({ name: k, days: wfhByDayObj[k] || 0 }));

  // Top WFH Employees
  const wfhEmpMap = {};
  flattenedWfhDays.forEach(r => {
      const name = r.name || "Unknown";
      wfhEmpMap[name] = (wfhEmpMap[name] || 0) + 1;
  });
  const wfhEmpChart = Object.keys(wfhEmpMap).map(k => ({ name: k, days: wfhEmpMap[k] })).sort((a,b) => b.days - a.days).slice(0, 5);

  // OT Status
  const otStatusMap = { 'Pending Approval': 0, 'Approved': 0, 'Rejected': 0, 'Cancelled': 0 };
  filteredOt.forEach(r => otStatusMap[r.status] = (otStatusMap[r.status] || 0) + 1);
  const otStatusPie = [
      { name: 'Approved', value: otStatusMap['Approved'], color: '#22c55e' },
      { name: 'Pending', value: otStatusMap['Pending Approval'], color: '#eab308' },
      { name: 'Rejected', value: otStatusMap['Rejected'] + otStatusMap['Cancelled'], color: '#ef4444' }
  ].filter(d => d.value > 0);


  // Department Aggregation
  const deptMap = {};
  [...filteredWfh, ...filteredOt].forEach(r => {
      const d = r.department || "Unassigned";
      if(!deptMap[d]) deptMap[d] = { dept: d, wfh_req:0, wfh_days:0, ot_req:0, ot_hours:0, emps: new Set() };
      deptMap[d].emps.add(r.employee_no);
  });
  flattenedWfhDays.forEach(r => {
      const d = r.department || "Unassigned";
      deptMap[d].wfh_days++;
  });
  filteredWfh.forEach(r => {
      const d = r.department || "Unassigned";
      deptMap[d].wfh_req++;
  });
  filteredOt.forEach(r => {
      const d = r.department || "Unassigned";
      deptMap[d].ot_req++;
      deptMap[d].ot_hours += (r.duration_hours || 0);
  });
  const deptList = Object.values(deptMap).map(d => ({...d, emps: d.emps.size}));

  // Top OT Employees
  const empOtMap = {};
  filteredOt.forEach(r => {
      if(!empOtMap[r.employee_no]) empOtMap[r.employee_no] = { emp: r.name, id: r.employee_no, dept: r.department, req:0, hrs:0 };
      empOtMap[r.employee_no].req++;
      empOtMap[r.employee_no].hrs += (r.duration_hours || 0);
  });
  const topEmployees = Object.values(empOtMap).sort((a,b)=>b.hrs - a.hrs).slice(0, 5);

  const pendingWfh = filteredWfh.filter(r => r.status === 'Pending Approval' && (user.role === 'system_admin' || !r.approver_dn || r.approver_dn === user.user_dn));
  const pendingOt = filteredOt.filter(r => r.status === 'Pending Approval' && (user.role === 'system_admin' || !r.approver_dn || r.approver_dn === user.user_dn));

  // WFH Status Chart
  const statusPie = [
      { name: 'Approved', value: approvedWfh, color: '#22c55e' },
      { name: 'Pending', value: pendingWfh.length, color: '#eab308' },
      { name: 'Rejected', value: filteredWfh.filter(r => r.status === 'Rejected').length, color: '#ef4444' }
  ].filter(x => x.value > 0);

  return (
    <div className="p-6 bg-slate-50 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800">{user.role === 'manager' ? "My Reports Dashboard" : "HR Analytics Dashboard"}</h2>
        <div className="flex gap-4 items-center">
            <select className="border p-2 rounded-lg font-medium shadow-sm bg-white" value={dateFilter} onChange={e=>setDateFilter(e.target.value)}>
                <option>Today</option>
                <option>This Week</option>
                <option>This Month</option>
                <option>Last Month</option>
                <option>This Year</option>
                <option>All Time</option>
            </select>
            <div className="flex gap-2">
                <a href="/api/export/wfh" className="bg-green-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-green-700 shadow-sm flex items-center gap-2">⬇️ WFH Report</a>
                <a href="/api/export/overtime" className="bg-green-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-green-700 shadow-sm flex items-center gap-2">⬇️ OT Report</a>
            </div>
        </div>
      </div>

      {user.role === 'system_admin' && (
      <div className="flex gap-4 mb-6">
          <button onClick={() => setAdminTab('global')} className={`px-4 py-2 font-bold rounded-lg ${adminTab === 'global' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border'}`}>Global Analytics</button>
          <button onClick={() => setAdminTab('hierarchy')} className={`px-4 py-2 font-bold rounded-lg ${adminTab === 'hierarchy' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border'}`}>My Reports Overview</button>

      </div>
      )}
      
      {adminTab === 'global' && (
        <>


      {filteredWfh.length === 0 && filteredOt.length === 0 && (
          <div className="bg-white p-6 rounded-xl border border-dashed border-slate-300 text-center text-slate-500 mb-6 font-medium">
              No data available for the selected period.
          </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 border-t-4 border-t-blue-500">
              <div className="text-xs font-bold text-slate-400 uppercase">WFH Requests</div>
              <div className="text-3xl font-bold mt-1 text-slate-800">{filteredWfh.length}</div>
              <div className="text-xs font-medium text-slate-500 mt-1">{totalWFHDays} Total WFH Days</div>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 border-t-4 border-t-purple-500">
              <div className="text-xs font-bold text-slate-400 uppercase">OT Requests</div>
              <div className="text-3xl font-bold mt-1 text-slate-800">{filteredOt.length}</div>
              <div className="text-xs font-medium text-slate-500 mt-1">{totalOTHours.toFixed(1)} Total OT Hours</div>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 border-t-4 border-t-indigo-500">
              <div className="text-xs font-bold text-slate-400 uppercase">Overnight OT</div>
              <div className="text-3xl font-bold mt-1 text-slate-800">{overnightOt.toFixed(1)} <span className="text-sm font-normal">hrs</span></div>
              <div className="text-xs font-medium text-slate-500 mt-1">Crossing Midnight</div>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 border-t-4 border-t-emerald-500">
              <div className="text-xs font-bold text-slate-400 uppercase">Active Employees</div>
              <div className="text-3xl font-bold mt-1 text-slate-800">{Math.max(uniqueEmpWfh, uniqueEmpOt)}</div>
              <div className="text-xs font-medium text-slate-500 mt-1">Submitting requests</div>
          </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Charts */}
          <div className="col-span-1 md:col-span-2 bg-white p-5 rounded-xl shadow-sm border border-slate-100">
              <h3 className="font-bold text-slate-700 mb-4">WFH Days by Weekday</h3>
              <div className="h-64">
                {!rechartsLoaded ? <div className="flex h-full items-center justify-center text-slate-400">Loading charts...</div> :
                 wfhByDayChart.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={wfhByDayChart}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} />
                          <XAxis dataKey="name" axisLine={false} tickLine={false} />
                          <YAxis allowDecimals={false} axisLine={false} tickLine={false} />
                          <Tooltip cursor={{fill: '#f8fafc'}} />
                          <Bar dataKey="days" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                      </BarChart>
                  </ResponsiveContainer>
                ) : <div className="flex h-full items-center justify-center text-slate-400">No data</div>}
              </div>
          </div>

          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100">
              <h3 className="font-bold text-slate-700 mb-4">WFH Status</h3>
              <div className="h-64">
                {!rechartsLoaded ? <div className="flex h-full items-center justify-center text-slate-400">Loading charts...</div> :
                 statusPie.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                          <Pie data={statusPie} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                              {statusPie.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                          </Pie>
                          <Tooltip />
                          <Legend verticalAlign="bottom" height={36}/>
                      </PieChart>
                  </ResponsiveContainer>
                ) : <div className="flex h-full items-center justify-center text-slate-400">No data</div>}
              </div>
          </div>
          
          <div className="col-span-1 md:col-span-3 bg-white p-5 rounded-xl shadow-sm border border-slate-100">
              <h3 className="font-bold text-slate-700 mb-4">Overtime Hours by Department</h3>
              <div className="h-64">
                {!rechartsLoaded ? <div className="flex h-full items-center justify-center text-slate-400">Loading charts...</div> :
                 deptList.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={deptList}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} />
                          <XAxis dataKey="dept" axisLine={false} tickLine={false} />
                          <YAxis allowDecimals={false} axisLine={false} tickLine={false} />
                          <Tooltip cursor={{fill: '#f8fafc'}} />
                          <Bar dataKey="ot_hours" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={50} />
                      </BarChart>
                  </ResponsiveContainer>
                ) : <div className="flex h-full items-center justify-center text-slate-400">No data</div>}
              </div>
          </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 overflow-x-auto">
              <h3 className="font-bold text-slate-700 mb-4">Top Overtime Employees</h3>
              {topEmployees.length > 0 ? (
              <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-slate-500 uppercase text-xs"><tr><th className="p-2 rounded-l-lg">Employee</th><th className="p-2">Dept</th><th className="p-2">Reqs</th><th className="p-2 rounded-r-lg">Total Hours</th></tr></thead>
                  <tbody className="divide-y">{topEmployees.map(e => (
                      <tr key={e.id}><td className="p-2 font-bold">{e.emp}</td><td className="p-2">{e.dept || "-"}</td><td className="p-2">{e.req}</td><td className="p-2 font-bold text-blue-600">{e.hrs.toFixed(2)}</td></tr>
                  ))}</tbody>
              </table>) : <div className="text-slate-400">No data</div>}
          </div>

          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 overflow-x-auto">
              <h3 className="font-bold text-slate-700 mb-4">Department Summary</h3>
              {deptList.length > 0 ? (
              <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-slate-500 uppercase text-xs"><tr><th className="p-2 rounded-l-lg">Dept</th><th className="p-2">WFH Days</th><th className="p-2 rounded-r-lg">OT Hrs</th></tr></thead>
                  <tbody className="divide-y">{deptList.map(d => (
                      <tr key={d.dept}><td className="p-2 font-bold">{d.dept}</td><td className="p-2">{d.wfh_days}</td><td className="p-2 font-bold text-blue-600">{d.ot_hours.toFixed(2)}</td></tr>
                  ))}</tbody>
              </table>) : <div className="text-slate-400">No data</div>}
          </div>
      </div>
      
      {/* Pending Approvals */}
      <h3 className="font-bold text-lg mb-2 flex items-center gap-2"><span className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">{pendingWfh.length}</span> Pending WFH Approvals</h3>
      {pendingWfh.length === 0 ? <div className="p-4 bg-white text-slate-500 rounded-lg mb-8 shadow-sm">No pending WFH requests in this period.</div> : (
      <div className="overflow-x-auto"><table className="w-full text-left text-sm border rounded-xl overflow-hidden mb-8 shadow-sm"><thead className="bg-slate-50 border-b"><tr><th className="p-3">Emp</th><th className="p-3">Dates</th><th className="p-3">Type</th><th className="p-3">Status</th><th className="p-3">Action</th></tr></thead>
        <tbody className="divide-y bg-white">{pendingWfh.map(r => (
          <tr key={r.id}>
              <td className="p-3 font-bold text-slate-700">{r.name}</td>
              <td className="p-3">
                  {r.selected_dates ? safeJSONParse(r.selected_dates, []).map(d=>formatDateOnly(d)).join(", ") : formatDateOnly(r.date)}
              </td>
              <td className="p-3">{r.wfh_type}</td>
              <td className="p-3"><StatusBadge status={r.status}/></td>
              <td className="p-3 flex gap-2">
                <button onClick={()=>handleAction('wfh', r.id, 'Approved')} className="bg-green-100 text-green-700 px-3 py-1.5 rounded text-xs font-bold hover:bg-green-200">Approve</button>
                <button onClick={()=>handleAction('wfh', r.id, 'Rejected')} className="bg-red-100 text-red-700 px-3 py-1.5 rounded text-xs font-bold hover:bg-red-200">Reject</button>
                <button onClick={()=>handleAction('wfh', r.id, 'Returned')} className="bg-orange-100 text-orange-700 px-3 py-1.5 rounded text-xs font-bold hover:bg-orange-200">Return</button>
              </td>
          </tr>
        ))}</tbody>
      </table></div>
      )}

      <h3 className="font-bold text-lg mb-2 flex items-center gap-2"><span className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">{pendingOt.length}</span> Pending Overtime Approvals</h3>
      {pendingOt.length === 0 ? <div className="p-4 bg-white text-slate-500 rounded-lg mb-8 shadow-sm">No pending OT requests in this period.</div> : (
      <div className="overflow-x-auto"><table className="w-full text-left text-sm border rounded-xl overflow-hidden shadow-sm"><thead className="bg-slate-50 border-b"><tr><th className="p-3">Emp</th><th className="p-3">Start/End</th><th className="p-3">Hrs</th><th className="p-3">Status</th><th className="p-3">Action</th></tr></thead>
        <tbody className="divide-y bg-white">{pendingOt.map(r => (
          <tr key={r.id}><td className="p-3 font-bold text-slate-700">{r.name}</td><td className="p-3 text-xs leading-relaxed">{formatDateTime(r.start_datetime)} <br/> {formatDateTime(r.end_datetime)}</td><td className="p-3 font-bold text-blue-700">{(r.duration_hours || 0).toFixed(2)}</td><td className="p-3"><StatusBadge status={r.status}/></td>
          <td className="p-3 flex gap-2">
            <button onClick={()=>handleAction('ot', r.id, 'Approved')} className="bg-green-100 text-green-700 px-3 py-1.5 rounded text-xs font-bold hover:bg-green-200">Approve</button>
            <button onClick={()=>handleAction('ot', r.id, 'Rejected')} className="bg-red-100 text-red-700 px-3 py-1.5 rounded text-xs font-bold hover:bg-red-200">Reject</button>
          </td></tr>
        ))}</tbody>
      </table></div>
      )}

        </>
      )}



      {adminTab === 'hierarchy' && (
          <HierarchyOverview 
              wfh={filteredWfh} 
              overtime={filteredOt} 
              hierarchy={hierarchy} 
              users={users} 
              viewFilter={viewFilter} 
              setViewFilter={setViewFilter} 
              dateFilter={dateFilter}
              formatDateOnly={formatDateOnly}
              getWFHDaysCount={getWFHDaysCount}
              user={user}
              handleAction={handleAction}
          />
      )}
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
root.render(<ErrorBoundary><App /></ErrorBoundary>);
