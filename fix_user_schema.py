with open("backend/schemas.py", "r") as f:
    content = f.read()

old_user = """class User(BaseModel):
    id: int
    employee_no: str
    name: str
    is_admin: bool
    role: Optional[str] = 'employee'
    team_id: Optional[int] = None
    manager_dn: Optional[str] = None
    manager_name: Optional[str] = None
    session_token: Optional[str] = None
    
    class Config:"""

new_user = """class User(BaseModel):
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
    
    class Config:"""

content = content.replace(old_user, new_user)
with open("backend/schemas.py", "w") as f:
    f.write(content)
