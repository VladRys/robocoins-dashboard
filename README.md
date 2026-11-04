# RoboCoins Dashboard

RoboCoins is an educational platform for managing student groups, virtual coins, and rewards. The backend uses FastAPI, SQLAlchemy, and PostgreSQL. The browser pages are in `pages/`.

## Features

- 🪙 Virtual currency for student achievements and activities
- 👨‍🎓 Student profiles with customizable nicknames and avatars
- 👨‍🏫 Teacher management of assigned groups and students
- 👥 Group enrollment and teacher assignments
- 🎁 Reward and privilege shop with configurable prices
- 📜 Student transaction history and balance tracking
- 🔐 Role-based accounts for students, teachers, and administrators

## Roles and access

| Role | Capabilities |
| --- | --- |
| `admin` | Manage teachers, courses, groups, and rewards; edit any student's profile; manage group membership |
| `teacher` | Work with assigned groups and their students, including student profile edits and group membership |
| `student` | View their own profile and credentials, and use student features |

All accounts use `POST /auth/login` with `{"code":"..."}`. Successful login sets an HTTP-only session cookie. Normal teacher and student accounts log in with their access code. The administrator uses the 12-character `ADMIN_PASSWORD`.

Set a unique `ADMIN_PASSWORD` per environment. When it is not configured, the server generates a 12-character password at startup and writes it to the application log. The administrator account is created the first time that password successfully logs in. Keep the password and logs private.

The admin testing page is available at `/admin`.

## API overview

All requests and responses use JSON unless noted otherwise. Authenticated endpoints use the session cookie established by `/auth/login`.

### Students

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/student/register` | Public | Create a student and assign initial groups |
| `GET` | `/student` | Admin | List student profiles |
| `GET` | `/student/{student_id}` | Authenticated | Read a student profile |
| `PATCH` | `/student/{student_id}/nickname` | Student themselves, assigned teacher, or admin | Change the student's nickname |
| `PATCH` | `/student/{student_id}/avatar` | Student themselves, assigned teacher, or admin | Change the student's avatar |
| `GET` | `/auth/me/credentials` | Student | Read their own access credentials |

Nickname updates synchronize the student's profile and user account names. The nickname request body is `{"new_nickname":"Alex"}`; the avatar request body is `{"new_avatar":"🤖"}`.

### Groups and teachers

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/teacher/register` | Admin | Create a teacher account |
| `POST` | `/group/create` | Admin | Create a group |
| `PUT` | `/group/id/{group_id}/teachers` | Admin | Set up to two teachers for a group |
| `PUT` | `/group/id/{group_id}/student` | Assigned teacher or admin | Add one student to the group; body: `{"student_id":123}` |
| `DELETE` | `/group/id/{group_id}/student/{student_id}` | Assigned teacher or admin | Remove a student from that group |
| `GET` | `/group/id/{group_id}` | Authenticated | Read a group and its students |

Removing a student only removes that group's membership. It does not delete the student or change their other group memberships.

### Balances and rewards

- `GET /student/{student_id}/balance` reads a balance.
- `POST /student/{student_id}/balance/transactions` records a balance change. Example: `{"operation":"deposit","amount":5,"reason":"Completed a challenge"}`. Use `"deduct"` to subtract coins.
- `GET /student/{student_id}/transactions?limit=50&offset=0` lists transactions, newest first.
- `GET /rewards` lists rewards; `POST /rewards` creates one.

Amounts must be positive and deductions cannot reduce a balance below zero. Review authorization before exposing balance endpoints to untrusted clients.

## Run locally

Requirements: Python 3.13+ and PostgreSQL. Install dependencies from the repository root:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

Configure a PostgreSQL URL in `.env` or the process environment. Development mode requires `DEV_DATABASE_URL`; it does not fall back to `DATABASE_URL` or `TEST_DATABASE_URL`.

```dotenv
PRODUCT_MODE=DEV
DEV_DATABASE_URL=postgresql+asyncpg://robocoins:robocoins@localhost:5432/robocoins
ADMIN_PASSWORD=replace-with-your-12-character-secret
```

Run the API from the repository root:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is at `http://localhost:8000`, OpenAPI docs at `http://localhost:8000/docs`, and the admin testing page at `http://localhost:8000/admin`. On startup, the app creates missing tables. For an existing database that is already managed by Alembic, apply pending migrations from the repository root with `alembic upgrade head`.

## Docker Compose

Docker Compose starts PostgreSQL and the API:

```bash
docker compose up --build
```

Open `http://localhost:8000/docs` or `http://localhost:8000/admin`. Set `ADMIN_PASSWORD` in the environment or the project `.env` file to configure that deployment's administrator password. It must be exactly 12 characters. If unset, the app generates one and writes it to the API container logs:

```bash
docker compose logs app
```

This Compose configuration runs the app in `DEV` mode and is intended for local development. Do not deploy it as-is. Production needs `PRODUCT_MODE=PROD`, `PROD_DATABASE_URL` (or `DATABASE_URL`), and `PROD_CORS_ORIGINS` configured in the deployment environment. The default database credentials in `docker-compose.yml` are for local development. PostgreSQL data is stored in the `postgres_data` volume. To stop the containers while preserving data, run `docker compose down`; to remove the local database volume as well, run `docker compose down --volumes`.

## License

See [LICENSE](LICENSE).
