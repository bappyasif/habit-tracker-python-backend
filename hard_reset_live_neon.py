import os
from dotenv import load_dotenv
from src.configs.db import engine
from src.models.db import Base

load_dotenv()

def main():
    try:
        print("⚠️  WARNING: This will delete ALL data and tables in the database.")
        
        # 1. Drop all tables defined in your Base metadata
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # 2. Recreate all tables from scratch
        print("Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database hard reset complete. All tables are fresh.")
    except Exception as e:
        print(f"❌ Reset failed: {e}")

if __name__ == "__main__":
    main()
