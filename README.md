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

