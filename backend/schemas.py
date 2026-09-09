from pydantic import BaseModel
import datetime
from typing import Optional

class UserLogin(BaseModel):
    employee_no: str
    password: str

class User(BaseModel):
    id: int
    employee_no: str
    name: str
    is_admin: bool
    role: Optional[str] = 'employee'
    team_id: Optional[int] = None
    manager_dn: Optional[str] = None
    manager_name: Optional[str] = None
    session_token: Optional[str] = None
    has_direct_reports: Optional[bool] = False
    
    class Config:
        from_attributes = True

class OvertimeBase(BaseModel):
    employee_no: str
    name: str
    department: Optional[str] = None
    team_id: Optional[int] = None
    start_datetime: str
    end_datetime: str
    assigned_work: str
    notes: Optional[str] = None

class OvertimeCreate(OvertimeBase):
    pass

class Overtime(OvertimeBase):
    id: int
    duration_hours: float
    status: str
    approved_by: Optional[str] = None
    approval_date: Optional[str] = None
    manager_comment: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class WFHBase(BaseModel):
    employee_no: str
    name: str
    department: Optional[str] = None
    team_id: Optional[int] = None
    date: Optional[datetime.date] = None # Legacy
    end_date: Optional[datetime.date] = None # Legacy
    selected_dates: Optional[str] = None # JSON array string of selected dates
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    wfh_type: Optional[str] = "Full Day"
    reason: Optional[str] = None

class WFHCreate(WFHBase):
    pass

class WFH(WFHBase):
    id: int
    week_number: Optional[int] = None
    year: Optional[int] = None
    status: str
    approved_by: Optional[str] = None
    approval_date: Optional[str] = None
    manager_comment: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class Settings(BaseModel):
    admin_email: str
    max_wfh_days: int
    
    class Config:
        from_attributes = True

class LDAPSettingsBase(BaseModel):
    enabled: bool = False
    server_url: Optional[str] = None
    port: int = 389
    protocol: str = 'LDAP'
    use_tls: bool = False
    base_dn: Optional[str] = None
    bind_username: Optional[str] = None
    bind_password: Optional[str] = None
    timeout: int = 10
    
    user_search_base: Optional[str] = None
    user_search_filter: Optional[str] = None
    attr_username: str = 'sAMAccountName'
    attr_employee_no: str = 'employeeNumber'
    attr_display_name: str = 'displayName'
    attr_email: str = 'mail'
    attr_manager: str = 'manager'
    attr_department: str = 'department'
    
    group_search_base: Optional[str] = None
    group_membership_attr: str = 'uniqueMember'
    group_sysadmin: Optional[str] = None
    group_manager: Optional[str] = None
    group_employee: Optional[str] = None

class LDAPSettingsCreate(LDAPSettingsBase):
    pass

class LDAPSettingsResponse(LDAPSettingsBase):
    id: int
    bind_password: Optional[str] = None  # Will be masked or removed in the endpoint
    
    class Config:
        orm_mode = True
