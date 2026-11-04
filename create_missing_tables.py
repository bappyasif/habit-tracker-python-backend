# create_missing_tables.py is a utility script that creates any missing tables in the database based on the SQLAlchemy models defined in the application. It uses the `Base.metadata.create_all()` method to create tables that do not already exist, ensuring that the database schema is up-to-date with the application's models.
# when ready run `python create_missing_tables.py` with the correct environment variables set to "PRODUCTION" or "DEVELOPMENT" create the missing tables in the database.
import os
from dotenv import load_dotenv
from src.configs.db import engine
from src.models.db import Base

load_dotenv()

def main():
    print("Creating missing tables only...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    main()