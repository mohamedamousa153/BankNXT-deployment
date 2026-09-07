import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('/Users/mousa/BankNXT/backend/dashboard.db')
    cursor = conn.cursor()

    try:
        now_str = datetime.now().isoformat()
        
        # Add created_at to overtime_records
        try:
            cursor.execute(f"ALTER TABLE overtime_records ADD COLUMN created_at TEXT DEFAULT '{now_str}'")
        except sqlite3.OperationalError:
            pass

        # Add created_at to wfh_records
        try:
            cursor.execute(f"ALTER TABLE wfh_records ADD COLUMN created_at TEXT DEFAULT '{now_str}'")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        print("Migration 2 successful.")
    except Exception as e:
        print(f"Migration 2 failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
