from sqlalchemy import Column, Integer, String, Date, Time, Boolean
from database import Base

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    ldap_group_id = Column(String, unique=True, nullable=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String, unique=True, index=True)
    user_dn = Column(String, unique=True, nullable=True)
    name = Column(String)
    password = Column(String) # Storing plain text just for this temporary local dev
    is_admin = Column(Boolean, default=False)
    role = Column(String, default='employee')
    team_id = Column(Integer, nullable=True)
    manager_dn = Column(String, nullable=True)
    manager_name = Column(String, nullable=True)
    session_token = Column(String)

class OvertimeRecord(Base):
    __tablename__ = "overtime_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String, index=True)
    name = Column(String)
    department = Column(String)
    team_id = Column(Integer, nullable=True)
    
    start_datetime = Column(String)
    end_datetime = Column(String)
    duration_hours = Column(Integer)
    
    assigned_work = Column(String)
    notes = Column(String, nullable=True)
    status = Column(String, default="Pending Approval")
    
    approved_by = Column(String)
    approval_date = Column(String)
    manager_comment = Column(String)
    created_at = Column(String)

class WFHRecord(Base):
    __tablename__ = "wfh_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String, index=True)
    name = Column(String)
    department = Column(String)
    team_id = Column(Integer, nullable=True)
    
    date = Column(Date) # Start date
    end_date = Column(Date)
    start_time = Column(String)
    end_time = Column(String)
    wfh_type = Column(String, default="Full Day")
    reason = Column(String)
    
    week_number = Column(Integer)
    year = Column(Integer)
    status = Column(String, default="Pending Approval")
    
    approved_by = Column(String)
    approval_date = Column(String)
    manager_comment = Column(String)
    created_at = Column(String)
    selected_dates = Column(String) # JSON array of date strings

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, index=True)
    admin_email = Column(String, default="admin@banknxt.com")
    max_wfh_days = Column(Integer, default=2)

class LDAPSettings(Base):
    __tablename__ = "ldap_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    enabled = Column(Boolean, default=False)
    server_url = Column(String)
    port = Column(Integer, default=389)
    protocol = Column(String, default='LDAP')
    use_tls = Column(Boolean, default=False)
    base_dn = Column(String)
    bind_username = Column(String)
    bind_password = Column(String)
    timeout = Column(Integer, default=10)
    
    user_search_base = Column(String)
    user_search_filter = Column(String)
    attr_username = Column(String, default='sAMAccountName')
    attr_employee_no = Column(String, default='employeeNumber')
    attr_display_name = Column(String, default='displayName')
    attr_email = Column(String, default='mail')
    attr_manager = Column(String, default='manager')
    attr_department = Column(String, default='department')
    
    group_search_base = Column(String)
    group_membership_attr = Column(String, default='uniqueMember')
    group_sysadmin = Column(String)
    group_manager = Column(String)
    group_employee = Column(String)
