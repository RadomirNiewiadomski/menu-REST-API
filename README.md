# eMenu REST API 🍽️

A professional, dockerized REST API for managing restaurant menu cards. The project was built with a strong emphasis on **Code Quality**, **Test-Driven Development (TDD)**, and **Performance**.

## 🚀 About the Project

The system allows restaurants to manage their menu cards and share them with clients via a public API. The application is designed as a "Production-Ready Boilerplate" utilizing the latest standards in the Python ecosystem.

### Key Features
* **Public API (Read-Only):** Browse, filter (by name, date), search, and sort menu cards and dishes. Empty menus are hidden by default.
* **Private API (Management):** Full CRUD for Menu and Dish resources, available only after JWT authentication.
* **Media Handling:** Image upload support for dishes (using unique UUID filenames).
* **Optimization:** Solved N+1 query problems using `select_related`, `prefetch_related`, and `annotate`.
* **Background Tasks:** Daily email reports regarding menu changes sent at 10:00 AM (Celery + Redis).
* **Seed Data:** Management command to automatically populate the database with test data.

### 🛠️ Tech Stack
* **Python 3.12**
* **Django 5.2.8** & **Django REST Framework**
* **PostgreSQL 17** (Database)
* **Redis 7.1** (Message Broker)
* **Celery 5.5** (Asynchronous and periodic tasks)
* **Docker & Docker Compose** (Full environment containerization)
* **uv** (Ultra-fast Python package manager)

### 📏 Quality Standards
* **TDD (Test-Driven Development):** Code written in the Red-Green-Refactor cycle using `pytest`.
* **Type Hinting:** Full static typing checked by `mypy`.
* **Linting & Formatting:** Code formatted and checked by `ruff`.
* **Pre-commit hooks:** Automatic quality verification before every commit.

---

## ⚙️ Installation and Setup

**Docker** and **Docker Compose** are required.

1. **Clone the repository:**

    ```bash
    git clone https://github.com/RadomirNiewiadomski/menu-REST-API.git
    cd menu-REST-API
    ```


2.  **Build and run containers:**

    ```bash
    docker compose up --build
    ```

    *This command automatically:*

      * *Builds the images.*
      * *Starts PostgreSQL and Redis.*
      * *Runs migrations.*
      * *Initializes sample data (seed).*
      * *Starts the development server, Celery Worker, and Celery Beat.*

3.  **Ready\!** The application is available at `http://127.0.0.1:8000`.

-----

## 🧪 Testing and Code Quality

The project maintains high test coverage (unit and integration tests).

**Run all tests:**

```bash
docker compose run --rm app uv run pytest
```

**Check static typing (mypy):**

```bash
docker compose run --rm app uv run mypy .
```

**Check code style (ruff):**

```bash
docker compose run --rm app uv run ruff check .
```

-----

## 📖 Documentation and Access

Once the project is running, you have access to the following tools:

### 1\. Swagger UI (API Documentation)

Interactive documentation for all endpoints.
👉 **URL:** [http://127.0.0.1:8000/api/docs/]

### 2\. Django Admin Panel

Manage users and database content.
👉 **URL:** [http://127.0.0.1:8000/admin/]

### 3\. Demo Credentials

During startup (`docker compose up`), the `setup_sample_data` command creates default users (if they don't exist):

| Role | Email | Password | Description |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `password123` | Access to admin panel and all API endpoints. |
| **User** | `user@example.com` | `password123` | Standard API user. |

-----

## 📧 Email Reporting (Simulation)

The project is configured with `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`.
This means emails sent by Celery (daily report at 10:00 AM) will be visible in the **terminal logs** (`docker compose logs app`).

To force a report manually:

```bash
docker compose run --rm app python manage.py shell -c "from menu.tasks import send_daily_menu_report; print(send_daily_menu_report())"
```

-----

## Created by:
Radomir Niewiadomski
