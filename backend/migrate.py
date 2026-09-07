import sqlite3

def migrate():
    conn = sqlite3.connect('/Users/mousa/BankNXT/backend/dashboard.db')
    cursor = conn.cursor()

    try:
        # Create SystemSettings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_email TEXT DEFAULT 'admin@banknxt.com'
        )
        ''')
        
        # Ensure at least one row exists
        cursor.execute('SELECT COUNT(*) FROM system_settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO system_settings (admin_email) VALUES ("admin@banknxt.com")')

        # Add columns to overtime_records
        ot_columns = [
            ("department", "TEXT", ""),
            ("approved_by", "TEXT", ""),
            ("approval_date", "TEXT", ""),
            ("manager_comment", "TEXT", "")
        ]
        for col, col_type, default in ot_columns:
            try:
                cursor.execute(f"ALTER TABLE overtime_records ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass # Column exists

        # Add columns to wfh_records
        wfh_columns = [
            ("department", "TEXT", ""),
            ("wfh_type", "TEXT", "Full Day"),
            ("reason", "TEXT", ""),
            ("start_time", "TEXT", ""),
            ("end_time", "TEXT", ""),
            ("end_date", "DATE", ""),
            ("approved_by", "TEXT", ""),
            ("approval_date", "TEXT", ""),
            ("manager_comment", "TEXT", "")
        ]
        for col, col_type, default in wfh_columns:
            try:
                cursor.execute(f"ALTER TABLE wfh_records ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass # Column exists

        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
