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

 Boto3 is officialy aws adk for python
 aws console --> permission --> bucket policy to update how bucket should store the values or artifacts

 Iam policy - to instruct how the creditials or things should be used by aws

 IAM users.

 Here’s the end-to-end checklist for uploading profile images to your S3 bucket. The bucket name and prefix in this project are `fastapi-blog-upload-nov` and `profile-pics/`.

1. **Create or verify the S3 bucket** named `fastapi-blog-upload-nov`. Note its AWS region; you’ll need it in the app configuration. Keep **Block Public Access** enabled unless you have a specific public-access design.

2. **Create least-privilege IAM permissions** for the app's AWS identity under `profile-pics/`. The `aws_bucket.json` file is a bucket policy for public reads; it does not grant the app permission to delete objects. To fix `AccessDenied` on deletion, attach the identity policy in `aws_iam_policy.json` to the IAM user or role used by the app. It grants only `s3:DeleteObject` for profile images in this bucket.

   For uploads, the app's identity also needs `s3:PutObject` on the same prefix. For example:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "s3:PutObject",
         "Resource": "arn:aws:s3:::fastapi-blog-upload-nov/profile-pics/*"
       }
     ]
   }
   ```

   If the app needs to read images directly from S3, it may also need `s3:GetObject`. Don’t grant `s3:*` or access to every bucket, and don’t add delete permission to a public bucket policy.

3. **Give the app AWS credentials.** When deployed on AWS, prefer an IAM role attached to the service. For local development, use an AWS CLI profile or another secure credential method. Don’t commit access keys to source control or expose them to the browser.

4. **Configure the app** with the bucket name and region, and add an S3 client/library dependency if needed. Keep credentials out of code.

5. **Store S3 object keys.** The current upload flow stores the S3 object key (for example, `profile-pics/<filename>`) in the user record. Keep the key, rather than only the image URL, so the app can delete the object later.

6. **Decide how images will be served.** Keep the bucket private and use presigned URLs or a CDN if access should be controlled. If images are intentionally public, configure that deliberately rather than disabling bucket protections as a quick fix.

7. **Test the whole flow:** upload an image, confirm it appears under `profile-pics/`, verify the API returns a usable image URL, and test deletion too if your app supports it.

The app now ignores missing image keys and the literal `"null"`/`"none"` values rather than sending them to S3 as object keys. Ensure the bucket name and region in AWS and the app configuration match.

The correct mental model
- Engine: Usually one shared SQLAlchemy engine for the application.
- Session: A separate session for each request (or unit of work).
- Connection: Obtained from the engine's connection pool when needed.
- Cleanup: The session is closed after the request finishes.

Creating one global session and sharing it across concurrent requests can cause transaction conflicts and concurrency problems.

Component	Correct explanation
Engine	The central object that manages database connectivity and the connection pool.
Connection	An actual connection to the database used to execute SQL statements.
Session	An ORM interface that manages database operations, transactions and object state.

"SQLAlchemy sessions are not designed to be shared across concurrent requests. Sharing a global session can cause transaction interference, inconsistent ORM state and concurrency errors. Instead, we use a shared engine with a connection pool and create a separate session for each request. The session is closed after the request completes."

Two requests execute concurrently:
1. Request A reads balance = 1000.
2. Request B reads balance = 1000.
3. Request A deducts 200 and saves 800.
4. Request B deducts 300 and saves 700.
Lost update
 The expected balance is 500, but the database ends up with 700.
How can we prevent it?
Common approaches include:
- Optimistic locking: use a version column and reject updates based on stale versions.
- Pessimistic locking: use SELECT ... FOR UPDATE to lock the row during a transaction.
- Atomic SQL updates: perform calculations directly in SQL, such as UPDATE users SET balance = balance - 200.

Optimistic	                     Pessimistic
Detects conflicts	               Prevents competing access
Uses version checking	           Uses database locks
Good when conflicts are rare	   Useful when conflicts are likely

I’ll check the existing `ClientError` import and the S3 upload/delete route flow, then wire AWS errors into the current API error handling and explain how image keys move through upload and deletion.

Read , lines 1 to 60
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/routers/users.py",
  "view_range": [
    1,
    60
  ]
}

Read , lines 270 to 355
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/routers/users.py",
  "view_range": [
    270,
    355
  ]
}

Read 
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/imageUtils.py"
}

Read 
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/config.py"
}

Read 
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/aws_iam_policy.json"
}

Search for `logger|logging|ClientError|HTTP_502|HTTP_503`

Read , lines 240 to 350
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/routers/users.py",
  "view_range": [
    240,
    350
  ]
}

Read , lines 78 to 115
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/README.md",
  "view_range": [
    78,
    115
  ]
}

The `ClientError` import is already present but unused. I’ll use it to turn AWS failures into a clear API error, and adjust delete ordering so an `AccessDenied` response does not first erase the image key from the user record.

Edit 

Ran terminal command: git diff --check

Read , lines 45 to 72
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/routers/users.py",
  "view_range": [
    45,
    72
  ]
}

Read , lines 315 to 375
Completed with input: {
  "path": "/Users/saurav/Downloads/fast-api-fullStack/routers/users.py",
  "view_range": [
    315,
    375
  ]
}

Search for `s3_http_exception|def upload_to_s3|def delete_from_s3|async def upload_profil...`

Checked , no problems found

I used the existing `ClientError` import in `routers/users.py`. When S3 rejects an upload or delete, the API now returns a **502** with the AWS error code; for `AccessDenied`, the response also says to check the app’s IAM permissions.

### How the S3 image flow works

**Upload**
1. The route checks the file type and size, then validates the image.
2. `process_image` resizes it and encodes it as JPEG.
3. `upload_profile_image` makes an object key like `profile-pics/<generated-name>.jpg`.
4. `upload_to_s3` sends the image bytes to the configured bucket using `upload_fileobj`. The route saves the S3 key and URL on the user record.
5. When replacing an image, the route then tries to delete the previous object.

**Delete**
1. The route reads the saved S3 key and calls `delete_profile_image`, which calls `delete_from_s3`.
2. If S3 deletion fails, the route reports the error and keeps the image key in the user record. If it succeeds, the route clears the key and URL from the record.

The code can report an AWS permission failure, but it **cannot grant AWS permissions**. The IAM identity the app uses still needs `s3:DeleteObject` for `arn:aws:s3:::fastapi-blog-upload-nov/profile-pics/*`; uploads also need `s3:PutObject` on that path.

For this app’s **backend-to-S3 upload**, configure AWS like this:

1. **Create or verify the bucket** `fastapi-blog-upload-nov`. Note its AWS region and use that same region in the app configuration.

2. **Allow the app’s IAM user or role to upload objects.** Attach an identity policy to the AWS identity the app actually uses. Your existing `aws_iam_policy.json` grants delete access only; the app also needs `s3:PutObject` to upload. A policy for upload and delete would be:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:DeleteObject"
         ],
         "Resource": "arn:aws:s3:::fastapi-blog-upload-nov/profile-pics/*"
       }
     ]
   }
   ```

   In AWS IAM, attach this to the user/role used by the app (the error mentioned `fastapi_blog_s3`). This is an **identity policy**, not a bucket policy. You can omit `s3:DeleteObject` if the app only needs uploads.

3. **Configure the app’s AWS credentials and bucket settings.** Set `S3_BUCKET_NAME=fastapi-blog-upload-nov` and `S3_REGION_NAME` to the bucket’s actual region. Provide credentials securely, or use an IAM role when deployed on AWS. Don’t commit access keys or expose them to the browser. The app also requires its database and secret-key settings.

4. **Choose how uploaded images should be viewed.** The app currently constructs a normal S3 object URL. For that URL to work publicly, the bucket must allow `s3:GetObject` for `profile-pics/*`, and AWS Block Public Access settings must permit the public-read policy. Your `aws_bucket.json` is intended for public reads, but it does **not** grant upload or delete permission. If images should stay private, the app needs a private-image serving approach such as presigned URLs instead.

5. **No CORS setup is needed for this upload flow** because the backend sends the image to S3 using boto3; the browser is not uploading directly to S3.

After configuring AWS, try uploading an image. If AWS returns `AccessDenied`, check that the policy is attached to the identity whose credentials the app is using, and that the bucket name and `profile-pics/*` resource path match exactly.