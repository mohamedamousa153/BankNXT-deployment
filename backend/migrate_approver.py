import sqlite3

def run_migration(db_path):
    print(f"Migrating {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(wfh_records)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "approver_dn" not in columns:
            print(f"Adding approver_dn to wfh_records in {db_path}")
            cursor.execute("ALTER TABLE wfh_records ADD COLUMN approver_dn TEXT")
            cursor.execute("ALTER TABLE wfh_records ADD COLUMN approver_name TEXT")
            
        cursor.execute("PRAGMA table_info(overtime_records)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "approver_dn" not in columns:
            print(f"Adding approver_dn to overtime_records in {db_path}")
            cursor.execute("ALTER TABLE overtime_records ADD COLUMN approver_dn TEXT")
            cursor.execute("ALTER TABLE overtime_records ADD COLUMN approver_name TEXT")
            
        conn.commit()
        conn.close()
        print(f"Migration complete for {db_path}.")
    except Exception as e:
        print(f"Skipping {db_path} due to error: {e}")

if __name__ == "__main__":
    run_migration("./dashboard.db")
    run_migration("./backend/dashboard.db")
