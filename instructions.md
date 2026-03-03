# how you run fastapi
    * environment setups:
        * python3.10 -m venv .venv 
        * source .venv/bin/activate
        * source .venv/bin/activate
    * check if you are in correct directory where your main python script (e.g. main.py or server.py or in this case its myapi.py) for project exists (e.g. dir)
    * then run `uvicorn mayapi:app --reload`
    * fastapi by default makes docs for your all available routes at [http://127.0.0.1:8000]/docs
    * another cool thing about that api docs is that we can directly test them from there without having to use any api client such as postman or thunder client or etc
    * another newer version of docs is [http://127.0.0.1:8000]/redoc

<!-- to make use of database -->
> to make use of rdbms we will need sqlalchemy and driber for your db(postgres or sql or oracle driver)

> postgresql doesnt create a database when not found in engine instance to be connected as like sqlite so we will have to do it manualy in local environment

> to create postgres db locally
```
sudo -u postgres psql -c "CREATE DATABASE db_name;"
sudo -u postgres psql -c "CREATE USER myuser WITH PASSWORD '1234';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE db_name TO myuser;"

sudo -u postgres psql -c "\l"   # List databases
sudo -u postgres psql -c "\du"  # List users   

Fix:
Connect as superuser (bypass password):
sudo -u postgres psql

Reset the password:
ALTER USER uname WITH PASSWORD 'new_password';

Exit:
\q

Connect with new password:
psql -U your_user -h localhost -d your_database


To check which tables are created in a PostgreSQL database locally, connect using psql and run:

\dt

This lists all tables in the current database's public schema.

For more details (like table size and description), use:

\dt+

To see tables in all schemas:

\dt *.*


To list all tables first (if unsure):

\dt

Then view data from any table:

SELECT * FROM your_table_name;

2. Using psql
Connect to PostgreSQL (pass: 1234) and drop the database:

psql -U postgres -h localhost -c "DROP DATABASE IF EXISTS dbname;"

Use IF EXISTS to avoid errors if the database doesn’t exist.
`

#installing packages using requirements.txt file : `pip install -r requirements.txt`