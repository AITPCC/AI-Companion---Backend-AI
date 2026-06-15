# Database Onboarding Guide for the AI Companion App

Audience: beginner developers who are learning databases for the first time.

Goal: by the end of this guide, you should understand why this project uses PostgreSQL, how to run it locally with Docker, how to inspect it with DataGrip, how SQL and migrations work, and how the same idea moves from your laptop to Google Cloud SQL.

---

## 1. Why We Use PostgreSQL for This AI Companion App

Our AI companion app needs to store real application data, such as users, conversations, messages, preferences, timestamps, and later maybe structured AI memory. This data should be reliable, searchable, and safe from accidental corruption.

We use PostgreSQL because it is:

- Reliable: PostgreSQL is a mature relational database used in many production systems.
- Open source: it is free to use and has a large community.
- Strong with structured data: tables, relationships, constraints, indexes, and transactions are first-class features.
- Good for JSON too: PostgreSQL supports `jsonb`, which is useful when some AI-related data is flexible and does not fit perfectly into fixed columns.
- Extensible: PostgreSQL has a strong extension ecosystem. This matters because AI apps may later use extensions for search, analytics, or vector-like workflows.
- Supported by cloud providers: Google Cloud SQL supports PostgreSQL, so what we learn locally transfers well to production.

### Why learn PostgreSQL before MySQL?

MySQL is also popular and useful. We are not saying MySQL is bad. But for this project, PostgreSQL is a better first database because:

- PostgreSQL follows SQL standards closely, so it teaches transferable database concepts.
- PostgreSQL has strong support for data correctness, constraints, transactions, and advanced data types.
- PostgreSQL works very naturally with modern Python backend tools like SQLAlchemy, SQLModel, Alembic, and FastAPI.
- PostgreSQL's JSON support is very useful for AI companion apps, where some data may be structured and some may be semi-structured.

For beginners, the most important lesson is not "PostgreSQL vs MySQL forever." The lesson is: learn one serious relational database well, understand SQL and schema design, and then other databases become much easier to learn.

Official reference: [PostgreSQL describes itself as an open-source object-relational database with modern features such as foreign keys, triggers, transactional integrity, and MVCC](https://www.postgresql.org/docs/current/intro-whatis.html). PostgreSQL also documents why `jsonb` is usually preferred for efficient JSON querying and indexing: [PostgreSQL JSON types](https://www.postgresql.org/docs/current/datatype-json.html).

---

## 2. What Is Docker?

Docker lets us run software in containers.

A container is like a lightweight, isolated box that contains an application and the environment it needs. Instead of asking every developer to install PostgreSQL directly on their laptop, we run PostgreSQL inside a Docker container.

Why this helps:

- Everyone gets the same PostgreSQL version.
- Setup is easier to repeat.
- If something breaks, we can delete and recreate the container.
- We avoid installing database server files directly into each person's operating system.

In this project, Docker runs PostgreSQL 18 locally.

Official reference: [Docker describes Docker as a platform for developing, shipping, and running applications](https://docs.docker.com/get-started/get-docker/).

---

## 3. Install Docker Desktop

### macOS

1. Go to the official Docker Desktop for Mac page: https://docs.docker.com/desktop/setup/install/mac-install/
2. Choose the correct download:
   - Apple silicon: most newer MacBooks with M1, M2, M3, M4 chips.
   - Intel chip: older MacBooks with Intel processors.
3. Open the downloaded `.dmg` file.
4. Drag Docker into the `Applications` folder.
5. Open Docker Desktop from Applications.
6. Accept the Docker terms when prompted.
7. Wait until Docker Desktop says it is running.
8. Open Terminal and verify:

```bash
docker --version
docker compose version
```

### Windows

1. Go to the official Docker Desktop for Windows page: https://docs.docker.com/desktop/setup/install/windows-install/
2. Download Docker Desktop for Windows.
3. Run `Docker Desktop Installer.exe`.
4. Use the recommended per-user installation unless your teacher or company says otherwise.
5. When prompted, use the WSL 2 backend.
6. Finish installation and start Docker Desktop.
7. Accept the Docker terms when prompted.
8. Open PowerShell and verify:

```powershell
docker --version
docker compose version
```

If Docker asks you to install or update WSL, follow the prompt. WSL 2 is the Linux environment Docker Desktop commonly uses on Windows.

---

## 4. Run PostgreSQL 18 Locally with Docker Compose

This project already has a `docker-compose.yml` file:

```yaml
services:
  db:
    image: postgres:18
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: ai_companion
      POSTGRES_PASSWORD: ai_companion
      POSTGRES_DB: ai_companion
    volumes:
      - postgres_data:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ai_companion -d ai_companion"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

What this means:

- `image: postgres:18`: use PostgreSQL version 18.
- `ports: "5432:5432"`: expose PostgreSQL on your laptop at port `5432`.
- `POSTGRES_USER`: create a database user named `ai_companion`.
- `POSTGRES_PASSWORD`: set the password to `ai_companion`.
- `POSTGRES_DB`: create a database named `ai_companion`.
- `volumes`: keep the database data even if the container stops.
- `healthcheck`: let Docker check whether PostgreSQL is ready.

Official reference: the official Postgres Docker image supports environment variables like `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`: https://hub.docker.com/_/postgres

### Start the database

From the project root:

```bash
docker compose up -d
```

On Windows PowerShell, use the same command:

```powershell
docker compose up -d
```

The `-d` means "detached mode", so the database runs in the background.

### Check that it is running

```bash
docker compose ps
```

You should see the `db` service running.

### View logs

```bash
docker compose logs db
```

### Stop the database

```bash
docker compose down
```

This stops the container but keeps the database data volume.

### Reset the local database completely

Only do this if you want to delete all local database data:

```bash
docker compose down -v
docker compose up -d
```

The `-v` deletes the Docker volume. That means your local database data is gone.

---

## 5. Install DataGrip and Connect to the Local Database

DataGrip is a database GUI from JetBrains. A GUI means you can click around, inspect tables, run SQL, and view data without using only the terminal.

Official reference: JetBrains recommends installing DataGrip through the JetBrains Toolbox App: https://www.jetbrains.com/help/datagrip/installation-guide.html

### Install DataGrip

#### macOS

1. Download JetBrains Toolbox: https://www.jetbrains.com/toolbox-app/
2. Open the `.dmg` file.
3. Drag JetBrains Toolbox to Applications.
4. Open JetBrains Toolbox.
5. Install DataGrip from Toolbox.
6. Open DataGrip.

#### Windows

1. Download JetBrains Toolbox: https://www.jetbrains.com/toolbox-app/
2. Run the installer.
3. Open JetBrains Toolbox.
4. Install DataGrip from Toolbox.
5. Open DataGrip.

### Connect DataGrip to local PostgreSQL

Make sure Docker Desktop is running and the database is started:

```bash
docker compose up -d
```

Then in DataGrip:

1. Create or open a DataGrip project.
2. Go to `File -> New -> Data Source -> PostgreSQL`.
3. If DataGrip shows `Download missing driver files`, click it.
4. Enter these connection values:

```text
Host: localhost
Port: 5432
User: ai_companion
Password: ai_companion
Database: ai_companion
```

5. Click `Test Connection`.
6. If the test succeeds, click `OK` or `Apply`.

Official reference: JetBrains documents PostgreSQL connection fields such as host, port, user, password, database, and JDBC URL here: https://www.jetbrains.com/help/datagrip/postgresql.html

---

## 6. How to Use a Database

### What is a database?

A database is a place to store data in an organized way.

For this project, instead of storing users or messages in memory, text files, or random JSON files, we store them in PostgreSQL tables.

### What is a table?

A table is like a spreadsheet:

- Columns define the shape of the data.
- Rows are the actual records.

Example `users` table:

| id | email | username | full_name | is_active |
|---:|---|---|---|---|
| 1 | ada@example.com | ada | Ada Lovelace | true |
| 2 | grace@example.com | grace | Grace Hopper | true |

### What is SQL?

SQL means Structured Query Language.

It is the language we use to talk to relational databases.

Example:

```sql
SELECT * FROM users;
```

This means: "show me all rows from the users table."

### Common SQL categories

#### DDL: Data Definition Language

DDL changes the structure of the database.

Examples:

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE
);
```

```sql
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
```

```sql
DROP TABLE users;
```

Think: DDL changes tables and columns.

#### DML: Data Manipulation Language

DML changes or reads the data inside tables.

Examples:

```sql
INSERT INTO users (email, username, full_name)
VALUES ('ada@example.com', 'ada', 'Ada Lovelace');
```

```sql
SELECT id, email, username FROM users;
```

```sql
UPDATE users
SET full_name = 'Augusta Ada Lovelace'
WHERE email = 'ada@example.com';
```

```sql
DELETE FROM users
WHERE email = 'ada@example.com';
```

Think: DML works with rows.

#### DCL: Data Control Language

DCL controls permissions.

Examples:

```sql
GRANT SELECT ON users TO some_user;
REVOKE SELECT ON users FROM some_user;
```

Beginners do not need to focus deeply on DCL yet.

#### TCL: Transaction Control Language

TCL controls transactions.

A transaction is a group of database changes that should succeed together or fail together.

Examples:

```sql
BEGIN;
UPDATE users SET is_active = false WHERE id = 1;
COMMIT;
```

If something goes wrong:

```sql
ROLLBACK;
```

Think: transactions protect data from being half-changed.

---

## 7. New Python Dependencies for Database Integration

This project uses these database-related dependencies:

```toml
alembic>=1.18.1
psycopg[binary]>=3.2.9
sqlalchemy>=2.0.46
sqlmodel>=0.0.38
```

Important project rule: use `uv` to manage dependencies. Do not edit `pyproject.toml` directly.

To add dependencies in this project, use commands like:

```bash
uv add sqlmodel sqlalchemy "psycopg[binary]" alembic
```

### What is `psycopg`?

`psycopg` is the PostgreSQL driver. SQLAlchemy uses it to actually talk to PostgreSQL.

Our database URL uses it here:

```text
postgresql+psycopg://ai_companion:ai_companion@localhost:5432/ai_companion
```

### What is SQLAlchemy?

SQLAlchemy is a Python library for working with databases.

It gives us:

- An engine: manages database connections.
- Sessions: let us query and save data.
- ORM support: lets Python classes map to database tables.

Official reference: SQLAlchemy says every app that connects to a database uses an `Engine`, usually created once from a database URL: https://docs.sqlalchemy.org/en/20/tutorial/engine.html

### What is SQLModel?

SQLModel is built on top of SQLAlchemy and Pydantic. It is especially nice with FastAPI because it lets us define Python models that can also become database tables.

Example from this project:

```python
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    username: str | None = Field(default=None, index=True, unique=True, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### What is an ORM?

ORM means Object-Relational Mapper.

It maps:

- Python classes to database tables.
- Python objects to database rows.
- Python attributes to database columns.

Without an ORM, we write SQL strings manually for everything.

With an ORM, we can write Python code like:

```python
user = User(email="ada@example.com", username="ada")
session.add(user)
session.commit()
```

The ORM turns that into SQL behind the scenes.

Why we use an ORM:

- Less repetitive SQL for common operations.
- Python models become the source of truth for table shape.
- Easier integration with FastAPI request and response models.
- Safer query building than hand-writing lots of string SQL.

Important: ORMs do not replace learning SQL. You still need to understand SQL because the ORM eventually sends SQL to the database.

Official references:

- SQLAlchemy ORM quick start: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- SQLModel with FastAPI session dependency: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/

---

## 8. What Is Database Migration and Why Do We Need Alembic?

A database schema is the structure of the database: tables, columns, indexes, constraints, and relationships.

As the app grows, the schema changes.

Examples:

- Add a `users` table.
- Add a `messages` table.
- Add a `profile_image_url` column.
- Rename a column.
- Add an index for faster search.

A migration is a versioned file that describes one schema change.

We use Alembic because:

- It records schema history.
- It lets every developer apply the same schema changes.
- It lets local, staging, and production databases stay in sync.
- It can upgrade and downgrade schema versions.
- It works naturally with SQLAlchemy and SQLModel metadata.

Official reference: Alembic's tutorial shows the common workflow of creating revisions and applying them with `alembic upgrade head`: https://alembic.sqlalchemy.org/en/latest/tutorial.html

---

## 9. How This Project Integrates FastAPI, SQLModel, SQLAlchemy, and Alembic

### Step 1: Database URL in app config

The project has this setting in `app/core/config.py`:

```python
database_url: str = (
    "postgresql+psycopg://ai_companion:ai_companion@localhost:5432/ai_companion"
)
```

The same value appears in `app/.env.sample`:

```text
DATABASE_URL=postgresql+psycopg://ai_companion:ai_companion@localhost:5432/ai_companion
```

Meaning:

- `postgresql`: database type.
- `psycopg`: Python driver.
- `ai_companion`: username.
- `ai_companion`: password.
- `localhost`: database host.
- `5432`: PostgreSQL port.
- `ai_companion`: database name.

### Step 2: Create the SQLAlchemy engine

File: `app/db/engine.py`

```python
from sqlmodel import create_engine

from app.core.config import get_settings

engine = create_engine(get_settings().database_url)
```

The engine is the main database connection factory.

### Step 3: Create a FastAPI session dependency

File: `app/db/session.py`

```python
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.db.engine import engine


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

This pattern means route handlers can ask FastAPI for a database session. FastAPI opens the session for the request and closes it afterward.

This follows the SQLModel/FastAPI dependency style shown in the official SQLModel docs: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/

### Step 4: Create a user table model

File: `app/models/user.py`

```python
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    username: str | None = Field(default=None, index=True, unique=True, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

Important ideas:

- `table=True`: this model maps to a real database table.
- `__tablename__ = "users"`: the table name is `users`.
- `primary_key=True`: `id` uniquely identifies each row.
- `unique=True`: no two users can have the same email or username.
- `index=True`: database creates an index to make lookup faster.

### Step 5: Configure Alembic to read SQLModel metadata

File: `alembic/env.py`

```python
from sqlmodel import SQLModel

from app.core.config import get_settings
import app.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = SQLModel.metadata
```

Why this matters:

- Alembic needs to know what tables our models define.
- `SQLModel.metadata` contains the table definitions.
- Importing `app.models` makes sure the model classes are loaded before Alembic compares metadata to the database.
- `config.set_main_option(...)` makes Alembic use our app's database URL instead of a hardcoded placeholder.

### Step 6: Generate a migration

After creating or changing a model, run:

```bash
uv run alembic revision --autogenerate -m "create users table"
```

What this does:

- Alembic looks at your SQLModel metadata.
- Alembic looks at the current database schema.
- Alembic creates a migration file describing the difference.

Always open the generated migration file and review it. Autogenerate is helpful, but developers are still responsible for checking the result.

This project's migration is:

```text
alembic/versions/202606100001_create_users_table.py
```

It creates:

- The `users` table.
- A unique index for `email`.
- A unique index for `username`.

### Step 7: Apply the migration to local PostgreSQL

Make sure the database is running:

```bash
docker compose up -d
```

Then apply migrations:

```bash
uv run alembic upgrade head
```

`head` means "the newest migration version."

### Step 8: Verify in DataGrip

1. Open DataGrip.
2. Connect to local PostgreSQL.
3. Refresh the database/schema.
4. Look for the `users` table.
5. Open a query console and run:

```sql
SELECT * FROM users;
```

The table may be empty. That is okay. Empty table means the structure exists but no users have been inserted yet.

### Step 9: Insert a test user

In DataGrip:

```sql
INSERT INTO users (email, username, full_name, is_active, created_at, updated_at)
VALUES (
  'ada@example.com',
  'ada',
  'Ada Lovelace',
  true,
  NOW(),
  NOW()
);
```

Then:

```sql
SELECT * FROM users;
```

You should see one row.

### Step 10: Common migration commands

Create a migration:

```bash
uv run alembic revision --autogenerate -m "describe your change"
```

Apply all pending migrations:

```bash
uv run alembic upgrade head
```

Show current database migration version:

```bash
uv run alembic current
```

Show migration history:

```bash
uv run alembic history
```

Downgrade one migration:

```bash
uv run alembic downgrade -1
```

Be careful with downgrades. They may delete columns or tables depending on the migration.

---

## 10. Create a PostgreSQL Database Instance on GCP Cloud SQL

Local Docker PostgreSQL is for development on your laptop.

Cloud SQL is for a managed PostgreSQL database in Google Cloud.

Managed database means Google handles many operational tasks like running the database server, backups, updates, and reliability features. You still need to design your schema, manage users, protect credentials, and control access.

Official reference: Google Cloud SQL PostgreSQL instance creation docs: https://docs.cloud.google.com/sql/docs/postgres/create-instance

### Before you start

You need:

- A Google Cloud account.
- A Google Cloud project.
- Billing enabled.
- Permission to create Cloud SQL instances.

### Create the instance in Google Cloud Console

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Select your project.
3. Search for `Cloud SQL`.
4. Click `Create instance`.
5. Choose `PostgreSQL`.
6. Set an instance ID, for example:

```text
ai-companion-postgres-dev
```

7. Set a password for the default PostgreSQL user.
8. Choose PostgreSQL version 18 if available in your region and project. Google Cloud's API name for PostgreSQL 18 is `POSTGRES_18`.
9. Choose a region near your app or team.
10. For learning/dev, choose a small machine size to control cost.
11. Configure storage. For learning, keep it small.
12. Enable backups if this database matters.
13. Create the instance.

Important: Cloud SQL costs money while it exists. Stop or delete learning resources when you no longer need them.

### Create the app database and user

After the instance is created:

1. Open the Cloud SQL instance.
2. Go to `Databases`.
3. Create a database:

```text
ai_companion
```

4. Go to `Users`.
5. Create a user:

```text
ai_companion
```

6. Save the password somewhere secure.

Do not commit cloud database passwords into Git.

---

## 11. Connect DataGrip to Cloud SQL PostgreSQL

There are several ways to connect to Cloud SQL. For beginners, the safest learning path is usually the Cloud SQL Auth Proxy.

The Cloud SQL Auth Proxy runs on your computer and creates a local secure connection to the Cloud SQL instance. Then DataGrip connects to `localhost`, similar to how it connects to Docker PostgreSQL.

Official reference: Google Cloud SQL Auth Proxy docs: https://docs.cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy

### Step 1: Install and authenticate Google Cloud CLI

Install Google Cloud CLI:

https://cloud.google.com/sdk/docs/install

Then sign in:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

For Windows PowerShell:

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

### Step 2: Find the instance connection name

In Google Cloud Console:

1. Open Cloud SQL.
2. Click your PostgreSQL instance.
3. Find `Connection name`.

It looks like:

```text
project-id:region:instance-id
```

Example:

```text
my-ai-project:asia-southeast1:ai-companion-postgres-dev
```

Google's docs also show this format as `project-id:region:instance-id`.

### Step 3: Download Cloud SQL Auth Proxy

Follow the official install instructions for your OS:

https://docs.cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy

### Step 4: Start the proxy

Open a terminal and run the proxy.

macOS:

```bash
./cloud-sql-proxy PROJECT_ID:REGION:INSTANCE_ID
```

Windows PowerShell:

```powershell
.\cloud-sql-proxy.exe PROJECT_ID:REGION:INSTANCE_ID
```

Keep this terminal open while using DataGrip.

By default, the proxy listens locally. If your local Docker PostgreSQL is already using port `5432`, use another local port for Cloud SQL, for example `5433`:

macOS:

```bash
./cloud-sql-proxy --port 5433 PROJECT_ID:REGION:INSTANCE_ID
```

Windows PowerShell:

```powershell
.\cloud-sql-proxy.exe --port 5433 PROJECT_ID:REGION:INSTANCE_ID
```

### Step 5: Connect DataGrip through the proxy

In DataGrip:

1. Go to `File -> New -> Data Source -> PostgreSQL`.
2. Enter:

```text
Host: localhost
Port: 5433
User: ai_companion
Password: the Cloud SQL password you created
Database: ai_companion
```

3. Click `Test Connection`.
4. If successful, click `Apply` or `OK`.

If you used the default proxy port `5432`, then use port `5432` in DataGrip. If local Docker PostgreSQL is also running, prefer `5433` for Cloud SQL to avoid conflicts.

### Step 6: Apply migrations to Cloud SQL

Be careful: migrations change the database schema.

For learning, make sure you are pointing to the Cloud SQL database intentionally.

Set your `DATABASE_URL` to the Cloud SQL proxy connection:

```text
DATABASE_URL=postgresql+psycopg://ai_companion:YOUR_PASSWORD@localhost:5433/ai_companion
```

Then run:

```bash
uv run alembic upgrade head
```

After that, refresh DataGrip and verify the `users` table exists.

---

## 12. Local vs Cloud: Mental Model

Local Docker PostgreSQL:

- Runs on your laptop.
- Good for learning and development.
- Easy to reset.
- Uses `localhost:5432`.
- Credentials in this project are simple because it is local only.

Cloud SQL PostgreSQL:

- Runs in Google Cloud.
- Good for shared development, staging, or production.
- Costs money.
- Needs stronger passwords and access control.
- Should never use committed secrets.
- Usually connect with Cloud SQL Auth Proxy or approved cloud networking.

---

## 13. Beginner Checklist

Use this checklist when setting up from scratch:

1. Install Docker Desktop.
2. Start Docker Desktop.
3. Clone/open the project.
4. Run `docker compose up -d`.
5. Run `docker compose ps`.
6. Install DataGrip.
7. Connect DataGrip to local PostgreSQL:
   - Host: `localhost`
   - Port: `5432`
   - User: `ai_companion`
   - Password: `ai_companion`
   - Database: `ai_companion`
8. Install Python dependencies using `uv`, not manual `pyproject.toml` edits.
9. Run `uv run alembic upgrade head`.
10. Refresh DataGrip.
11. Confirm the `users` table exists.
12. Run `SELECT * FROM users;`.
13. Insert a test user.
14. Query the test user.

---

## 14. Troubleshooting

### Docker command not found

Docker Desktop may not be installed or may not be running. Open Docker Desktop first, then try:

```bash
docker --version
```

### Port 5432 is already in use

Another PostgreSQL server may already be running.

Options:

- Stop the other PostgreSQL server.
- Change the local Docker port in `docker-compose.yml`, for example `"5433:5432"`.
- If you change the port, update DataGrip and `DATABASE_URL`.

### DataGrip cannot connect

Check:

- Is Docker Desktop running?
- Did you run `docker compose up -d`?
- Does `docker compose ps` show the database is running?
- Are host, port, user, password, and database correct?
- Did you click `Download missing driver files` in DataGrip?

### Alembic cannot connect

Check:

- Is PostgreSQL running?
- Is `DATABASE_URL` correct?
- Are you in the project root?
- Did you use `uv run alembic upgrade head`?

### Table does not appear in DataGrip

Try:

- Refresh the database/schema in DataGrip.
- Run `uv run alembic current`.
- Run `uv run alembic upgrade head`.
- Check whether you are connected to the correct database.

---

## 15. Key Terms

- Database: organized place to store data.
- PostgreSQL: the database system we use.
- Table: a structured collection of rows and columns.
- Row: one record in a table.
- Column: one field in a table.
- Primary key: unique identifier for a row.
- Foreign key: a column that points to another table.
- Index: data structure that makes lookup faster.
- SQL: language used to talk to a relational database.
- DDL: SQL that changes database structure.
- DML: SQL that reads or changes rows.
- Transaction: a group of changes that succeeds or fails together.
- Docker: tool for running software in containers.
- Container: isolated running environment.
- Docker Compose: tool for running multi-service Docker setups from a YAML file.
- ORM: maps Python classes and objects to database tables and rows.
- SQLAlchemy: Python database toolkit and ORM.
- SQLModel: Python library combining SQLAlchemy and Pydantic, useful with FastAPI.
- Alembic: database migration tool.
- Migration: versioned schema change.
- Cloud SQL: Google Cloud's managed database service.
- Cloud SQL Auth Proxy: local proxy that helps connect securely to Cloud SQL.

---

## 16. Official Docs Used

- PostgreSQL 18: https://www.postgresql.org/docs/current/
- PostgreSQL JSON types: https://www.postgresql.org/docs/current/datatype-json.html
- Docker Get Started: https://docs.docker.com/get-started/get-docker/
- Docker Desktop for Mac: https://docs.docker.com/desktop/setup/install/mac-install/
- Docker Desktop for Windows: https://docs.docker.com/desktop/setup/install/windows-install/
- Official Postgres Docker image: https://hub.docker.com/_/postgres
- DataGrip installation: https://www.jetbrains.com/help/datagrip/installation-guide.html
- DataGrip PostgreSQL connection: https://www.jetbrains.com/help/datagrip/postgresql.html
- SQLAlchemy 2.0 engine docs: https://docs.sqlalchemy.org/en/20/tutorial/engine.html
- SQLAlchemy ORM quick start: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- SQLModel FastAPI session dependency: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Google Cloud SQL PostgreSQL create instance: https://docs.cloud.google.com/sql/docs/postgres/create-instance
- Google Cloud SQL Auth Proxy: https://docs.cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy
