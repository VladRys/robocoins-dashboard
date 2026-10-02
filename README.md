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
| `TEACHER` | Manage students, coins and rewards |
| `STUDENT` | Earn coins and purchase rewards    |

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

---

## 🚀 Getting Started

### Requirements

_The requirements may be modified as the project evolves_

* Python 3.13+
* Node.js 20+
* PostgreSQL
* Docker *(optional)*

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

cd app
uvicorn main:app --reload
```

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
