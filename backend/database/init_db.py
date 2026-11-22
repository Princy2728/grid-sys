import sys
from backend.database.connection import engine, Base
from backend.models.entities import *

def init_database():
    """Initializes tables in the SQLite database."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_database()
