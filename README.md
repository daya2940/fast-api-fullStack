Models represents the database table.They are used for creating tables,querying rows,inserting data ,relationships

Schema - These represents api data shape

we are using sqlAlchemy but in production use only postgres or sql

sync vs async

async do not help with computing or cpubound operations.
so those will be synchronous function only

in async sqlAlchemy lazy loading is not supported but so if you want to load an author without explicity loading it will give you the error
it happens because lazy loading requires running a synchronous query in async context
and that is not allowed

synchronous will work when we have simple calculations

python -c "import secrets;
print(secrets.token_hex(32))" this is how we can run in terminal the python code

So auth.py and config.py lays out the building blocks for password hashing and JWT-based login, but the login/token flow still needs to be wired up and checked against the settings.

we have made modification to schemas also becasue user do not need to know all the details for eg in a post he should see only the post not the email this is what can be achieved using proper schemas

authentication covers who are you 
authorization covers what are you allowed to send or do

CurrentUser basically appying authorixation for each route if there will be no user then current user will return 401 and the route will not go through

class PostCreate(PostBase):
    title: str=Field(min_length=1, max_length=100)
    content: str
    published: bool = Field(default=True)
    user_id: int  here user_id is not safe approach because  anybody can personate any other user so we will be validating it with the help of current user function

Annotated lets you attach extra information to a type without changing the type itself.
aiosmtplib - for email type for checking because python based are synchrinous 

used homebrew to create the db on local system 


psql postgres -c "CREATE USER bloguser WITH PASSWORD '';"

createdb blog -O bloguser

uv add  "psycopg[binary]". This is the driver needed to run the postgres

async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    #startup code
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    #shutdown code
    await engine.dispose(). this part of sqllite is just the creation system it just create the table if it does not exist.
    Migration is not possible with sqllite

    Alembic is the database migration tool for SQLAlchemy. It tracks changes to your database schema over time—such as adding a column or creating a table—and lets you apply or roll back those changes in a controlled way.

    uv run alembic init ... runs Alembic using the project’s Python environment. The init command creates the initial migration setup: a configuration file and a folder for migration scripts.

uv run alembic init -t alembic uv run alembic init -t async alembic
In this command, -t means “use this template.” So -t alembic asks Alembic to use a template named alembic; it does not name the migration folder. That’s likely not what you want, and the command also omits the required folder name.
uv run alembic revision --autogenerate - this is to generate the migration schema from sqlAlchemy to postgres basic

psql blog -U bloguser - to checkinto homebrew and \dt to see the table
psql blog -U bloguser -d blog -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public - to delete all the tables
uv run alembic upgrade head - this tells that we wanted to apply all the migrations to the lastest versions

\d helps you to see the individual table in postgres
 we can check if we are the updated version of elembic or not using - uv run alembic upgrade head