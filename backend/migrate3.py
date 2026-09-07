import sqlite3

def migrate():
    conn = sqlite3.connect('/Users/mousa/BankNXT/backend/dashboard.db')
    cursor = conn.cursor()

    try:
        # Add selected_dates to wfh_records
        try:
            cursor.execute(f"ALTER TABLE wfh_records ADD COLUMN selected_dates TEXT")
        except sqlite3.OperationalError:
            pass

        # Add max_wfh_days to system_settings
        try:
            cursor.execute(f"ALTER TABLE system_settings ADD COLUMN max_wfh_days INTEGER DEFAULT 2")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        print("Migration 3 successful.")
    except Exception as e:
        print(f"Migration 3 failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
