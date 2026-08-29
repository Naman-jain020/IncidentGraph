from db.connection import init_db


if __name__ == "__main__":
    print("Creating IncidentGraph database tables...")
    init_db()
    print("Database setup completed.")