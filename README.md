Models represents the database table.They are used for creating tables,querying rows,inserting data ,relationships

Schema - These represents api data shape

we are using sqlAlchemy but in production use only postgres or sql

sync vs async

async do not help with computing or cpubound operations.
so those will be synchronous function only

in async sqlAlchemy lazy loading is not supported but so if you want to load an author without explicity loading it will give you the error
it happens because lazy loading requires running a synchronous query in async context
and that is not allowed

