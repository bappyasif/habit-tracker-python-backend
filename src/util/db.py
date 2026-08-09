from sqlalchemy.orm import sessionmaker
import os
from src.configs.db import engine
from src.models.db import Base

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Only auto-create tables if we are explicitly running in a local/development environment"""
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        try:
            print("Running in development mode: Ensuring tables exist...")
            Base.metadata.create_all(bind=engine)
            print("Tables verified/created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")
    else:
        print("Running in production mode: Skipping automatic Base.metadata.create_all()")

# def create_tables():
#     try:
#         Base.metadata.create_all(bind=engine)
#     except Exception as e:
#         print(f"Error creating tables: {e}")