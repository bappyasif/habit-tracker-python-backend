import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load variables from .env into standard os.environ
load_dotenv()

environment = os.getenv("ENVIRONMENT", "development")

if environment == "development":
    # 1. LOCAL DEVELOPMENT CONFIGURATION
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_USER_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print(f"--> [DEV MODE] Connecting to Local PostgreSQL at {db_host}:{db_port}/{db_name}")

else:
    # 2. PRODUCTION / NEON CLOUD CONFIGURATION
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        raise ValueError("CRITICAL ERROR: ENVIRONMENT is set to 'production', but 'DATABASE_URL' is missing from environment variables!")
    
    print(f"--> [PROD MODE] Connecting to Neon Cloud Database", db_url)

engine = create_engine(db_url)