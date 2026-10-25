# 🪙 ROBOCOINS

> Educational gamification platform with virtual currency, rewards and student management.

**ROBOCOINS** is an open-source platform designed to gamify the learning process.

Students can earn virtual coins for achievements, spend them on rewards and track their transaction history. Teachers can manage students, issue coins and create rewards.

---

## ✨ Features

* 🪙 Virtual currency system
* 👨‍🎓 Student profiles
* 🎁 Reward shop
* 📜 Transaction history
* 👨‍🏫 Teacher dashboard
* 🔐 Authentication and roles
* 📊 Student balances and statistics
* 📱 Responsive interface
* 🐳 Docker support
* 🔌 REST API

---

<!-- Will be provided in future. 

## 🏗️ Architecture

```text
ROBOCOINS
│
├── frontend/        # React + TypeScript
│
├── backend/         # FastAPI
│
├── migrations/      # Database migrations
│
├── docker-compose.yml
│
└── README.md
```

-->

<!-- ================================================ -->

<!-- 
### Backend

Will be provided in future. 

```text
Route
  ↓
Schema
  ↓
Service
  ↓
Repository
  ↓
Database
```

Built with:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic

-->

<!-- Will be provided in future. 
### Frontend

Built with:

* React
* TypeScript 
-->

## 👥 Roles

| Role        | Description                        |
| ----------- | ---------------------------------- |
| `teacher` | Manage students, coins and rewards |
| `student` | Earn coins and purchase rewards    |

Every account is stored in `users` with one of these roles. Student registration
at `POST /student/register` creates both the user and the existing student
profile; `POST /teacher/register` creates a teacher account. Teachers can be
assigned when creating a group with `teacher_ids`, or later with
`PUT /group/id/{group_id}/teachers`. A group accepts up to two distinct teacher
IDs. Use `GET /users` and `GET /users/{user_id}` to read user accounts.
Student profile `id` and `user_id` are the same account ID.

Student authentication continues to use the existing access-code session flow.

---

## 🪙 How it works

Students earn coins for achievements, activities and other actions defined by teachers.

```text
+3  Good behavior
+2  Completed challenge
+1  Extra activity
```

Teachers can create and configure their own rewards, including their names, descriptions and prices.

For example:

```text
5   Random sticker
7   Chosen sticker
15	School Merch, etc. 
20  Special privilege
```

Both the **rewards and their prices are fully configurable**, allowing each class or educational program to create its own coin economy.

Every coin operation is stored in the transaction history.

### Balance API

The backend supports these balance endpoints:

* `GET /student/{student_id}/balance` — read the current balance.
* `POST /student/{student_id}/balance/transactions` — add or deduct coins. Send
  `{"operation": "deposit", "amount": 5, "reason": "Completed a challenge"}` or
  use `"deduct"` to subtract coins from the balance.
* `GET /student/{student_id}/transactions?limit=50&offset=0` — read the
  student's transaction history, newest first, in a response containing
  `transactions`, `status`, and `code`. If the student exists but has no
  transactions yet, `transactions` is an empty array and `code` is `200`.

Amounts must be positive, and a deduction cannot make the balance negative.
The balance update and transaction record are committed together. These endpoints
do not yet authenticate callers; authorization should be added before exposing
them to an untrusted network.

---

## 🚀 Getting Started

### Requirements

_The requirements may be modified as the project evolves_

* Python 3.13+
* Node.js 20+
* PostgreSQL
* Docker *(optional)*

Set separate database secrets for each mode: `DEV_DATABASE_URL` for development and `PROD_DATABASE_URL` for production. In `DEV` mode, the application and Alembic require `DEV_DATABASE_URL`; they do not fall back to `DATABASE_URL` or `TEST_DATABASE_URL`.

### Clone

```bash
git clone https://github.com/your-username/robocoins.git
cd robocoins
```

### Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# For an existing database already managed by Alembic:
alembic upgrade head

# Configure the administrator password in the deployment environment (not in source control):
# ADMIN_PASSWORD=<a-long-unique-secret>

cd app
uvicorn main:app --reload
```

Everyone signs in through `POST /auth/login` with JSON `{"code":"..."}`. A 12-character value is checked as the administrator password; normal access codes continue to authenticate teachers and students.
The first successful login provisions the single administrator account in the database.
Set `ADMIN_PASSWORD` separately for each environment, exactly 12 characters long. If it is unset, the backend generates a random 12-character password and prints it once at startup.
Existing deployments must run `alembic upgrade head` to allow the new `admin` role.

### Frontend

_Will be provided in future._

<!-- ```bash
cd frontend

npm install
npm run dev
``` -->

---

## 🐳 Docker

Run the whole project with:

```bash
docker compose up --build
```

---

<!-- Will be provided in future.
## 🛠️ Roadmap

* [x] Basic project architecture
* [ ] Authentication
* [ ] Student management
* [ ] Coin transactions
* [ ] Reward system
* [ ] Teacher dashboard
* [ ] Student dashboard
* [ ] Statistics
* [ ] Mobile optimization
* [ ] Docker deployment
* [ ] Public API documentation 

-->

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a branch

```bash
git checkout -b feature/my-feature
```

3. Commit your changes

```bash
git commit -m "feat: add my feature"
```

4. Push the branch

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

## 📄 License

This project is open-source. See the `LICENSE` file for details.
