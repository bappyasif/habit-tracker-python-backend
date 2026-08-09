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


# # use this block of code one time to check if database url is available or not for creating tables in neon cloud after that comment this block as it is oly going to extract db url based on environment variable. 
# # uncomment this only when you need to create tables in neon cloud say for instance when you brought any changes to your database model and needs to recreate tables in neon cloud.
# import os
# from sqlalchemy import create_engine
# from dotenv import load_dotenv

# # Load variables from .env into standard os.environ so os.getenv() works everywhere
# load_dotenv()

# environment = os.getenv("ENVIRONMENT", "development")

# # CHANGE THIS LOGIC: Always use DATABASE_URL if it exists, regardless of environment!
# db_url = os.getenv("DATABASE_URL")

# if not db_url:
#     # Fallback to local if no DATABASE_URL is provided in .env
#     db_user = os.getenv("DB_USER", "postgres")
#     db_password = os.getenv("DB_USER_PASSWORD", "")
#     db_host = os.getenv("DB_HOST", "localhost")
#     db_port = os.getenv("DB_PORT", "5432")
#     db_name = os.getenv("DB_NAME", "postgres")
#     db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
#     print(f"--> Using LOCAL Database URL")
# else:
#     print(f"--> Using NEON Cloud Database URL from .env")

# engine = create_engine(db_url)




# import os
# from sqlalchemy import create_engine
# from dotenv import load_dotenv

# # Load variables from .env into standard os.environ so os.getenv() works everywhere
# load_dotenv()

# environment = os.getenv("ENVIRONMENT", "development")

# if environment == "development":
#     # Local PostgreSQL configuration
#     db_user = os.getenv("DB_USER", "postgres")
#     db_password = os.getenv("DB_USER_PASSWORD", "")
#     db_host = os.getenv("DB_HOST", "localhost")
#     db_port = os.getenv("DB_PORT", "5432")
#     db_name = os.getenv("DB_NAME", "postgres")
    
#     db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
#     print(f"--> Using LOCAL Database URL")
# else:
#     # Production / Neon Database configuration
#     db_url = os.getenv("DATABASE_URL")
#     if not db_url:
#         raise ValueError("CRITICAL ERROR: ENVIRONMENT is set to production, but DATABASE_URL is missing from .env!")
#     print(f"--> Using NEON Cloud Database URL")

# engine = create_engine(db_url)



# from sqlalchemy import create_engine

# from dotenv import dotenv_values

# config = dotenv_values(".env")

# db_dict = {
#     "user": config["DB_USER"],
#     "password": config["DB_USER_PASSWORD"],
#     "host": "localhost",
#     "port": "5432",
#     "database": config["DB_NAME"]
# }

# # db_url = f"postgresql://{db_dict['user']}:{db_dict['password']}@{db_dict['host']}:{db_dict['port']}/{db_dict['database']}"

# # db_url needs to be different based on production and development environment
# if config["ENVIRONMENT"] == "development":
#     db_url = f"postgresql://{db_dict['user']}:{db_dict['password']}@{db_dict['host']}:{db_dict['port']}/{db_dict['database']}"
# else:
#     db_url = config["DATABASE_URL"]

# engine = create_engine(db_url)