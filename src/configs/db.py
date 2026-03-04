from sqlalchemy import create_engine

from dotenv import dotenv_values

config = dotenv_values(".env")

db_dict = {
    "user": config["DB_USER"],
    "password": config["DB_USER_PASSWORD"],
    "host": "localhost",
    "port": "5432",
    "database": config["DB_NAME"]
}

db_url = f"postgresql://{db_dict['user']}:{db_dict['password']}@{db_dict['host']}:{db_dict['port']}/{db_dict['database']}"

engine = create_engine(db_url)