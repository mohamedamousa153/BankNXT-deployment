import openpyxl
from sqlalchemy.orm import Session
import models
from datetime import datetime, date, timedelta
import smtplib
from email.message import EmailMessage
import os

def generate_overtime_excel(db: Session, target_month: int, target_year: int) -> str:
    # Query records for the target month (basic string prefix matching for SQLite ISO strings)
    month_str = f"{target_year}-{target_month:02d}"
    records = db.query(models.OvertimeRecord).filter(
        models.OvertimeRecord.start_datetime.like(f"{month_str}%")
    ).all()
    
    # Filter strictly for the target month
    records = [r for r in records if datetime.fromisoformat(r.start_datetime).month == target_month]

    if not records:
        return None

    # Create a new workbook and select active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Overtime {target_month}-{target_year}"

    # Write headers
    headers = ["Employee No.", "Name", "Start Date/Time", "End Date/Time", "Duration (hrs)", "Assigned Work", "Notes"]
    ws.append(headers)

    # Write data rows
    for r in records:
        s_dt = datetime.fromisoformat(r.start_datetime)
        e_dt = datetime.fromisoformat(r.end_datetime)
        ws.append([
            r.employee_no,
            r.name,
            s_dt.strftime("%d/%m/%Y %H:%M"),
            e_dt.strftime("%d/%m/%Y %H:%M"),
            round(r.duration_hours, 2),
            r.assigned_work,
            r.notes if r.notes else ""
        ])
    
    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/Overtime_{target_month}_{target_year}.xlsx"
    wb.save(file_path)
    
    return file_path

def send_email_with_excel(file_path: str, month: int, year: int):
    # Mocking the email for now - in a real scenario we'd use environment variables
    # SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    # SMTP_PORT = int(os.getenv("SMTP_PORT", 1025)) # Use MailHog or similar for local testing
    
    print(f"[EMAIL MOCK] Sending {file_path} to HR/Managers for Overtime {month}/{year}")
    
    # Code to actually send the email:
    '''
    msg = EmailMessage()
    msg['Subject'] = f"Overtime Report - {month}/{year}"
    msg['From'] = "system@banknxt.com"
    msg['To'] = "hr@banknxt.com"
    msg.set_content("Please find attached the overtime report for the previous month.")
    
    with open(file_path, 'rb') as f:
        excel_data = f.read()
        
    msg.add_attachment(excel_data, maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=os.path.basename(file_path))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.send_message(msg)
    '''
    pass
