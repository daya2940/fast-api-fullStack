# Repository guidance

## Commands

- Install and sync dependencies: `uv sync`
- Run the development server from the repository root: `uv run fastapi dev main.py`
- The app requires `DATABASE_URL` and `SECRET_KEY` in the environment or `.env`; `DATABASE_URL` defaults to SQLite in `database.py`, but `config.py` currently requires the setting when auth is imported.
- No test files, test runner, or lint command are currently configured in the repository.

## Architecture

- `main.py` creates the FastAPI app, initializes SQLAlchemy tables during lifespan startup, mounts static and media files, and registers the user and post routers.
- `database.py` owns the async SQLAlchemy engine/session factory and provides request-scoped sessions through `get_db`. `DATABASE_URL` can override the default SQLite URL.
- `models.py` defines the SQLAlchemy `User` and `Post` entities and their relationship. `schemas.py` defines Pydantic request and response shapes; response schemas limit which model fields API consumers receive.
- `routers/users.py` and `routers/posts.py` implement the `/api/users` and `/api/posts` endpoints. Routes use async database sessions and SQLAlchemy `select` statements.
- `auth.py` contains password hashing and JWT helpers; `config.py` loads settings such as the secret key and token algorithm.

## Repository-specific conventions

- API paths include their `/api/...` prefix in each route decorator; `main.py` includes routers without an additional prefix.
- Database access is asynchronous. Load related ORM objects explicitly when returning them from async routes; the post routes use `selectinload(Post.author)` so response serialization does not trigger async lazy loading.
- Use Pydantic response models to control exposed fields. Public user data uses `UserPublic`; the registration response uses `UserPrivate` when email should be included.
- Store submitted passwords as hashes in `User.password_hash`; verify credentials against that hash, and do not return password material from an API response.
- Python 3.13 or newer is required. `pyproject.toml` and `uv.lock` define dependencies and are managed with `uv`.
