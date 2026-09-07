import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "./dashboard.db")

def init_db():
    if os.path.exists(DB_PATH):
        print("Database already exists.")
        return

    # Ensure directory exists if it's deeply nested
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

    from database import engine, Base
    import models

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import Session
    session = Session(engine)

    print("Creating local system admin...")
    admin = session.query(models.User).filter(models.User.employee_no == "admin").first()
    if not admin:
        admin = models.User(
            employee_no="admin",
            password="admin",
            name="System Administrator",
            is_admin=True,
            role="system_admin",
            team_id=0
        )
        session.add(admin)
        session.commit()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
