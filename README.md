# Todo App

A production-ready Todo List web application built with **FastAPI**, **SQLAlchemy 2.0**, **SQLite**, **Alembic**, **Pydantic v2**, **Jinja2**, **Bootstrap 5**, **HTMX**, and **JWT** authentication.

## Features

- **User Authentication** — Register, login, logout, profile management, password change
- **Task Management** — CRUD operations, status tracking (pending/in_progress/completed/archived), priority levels, due dates
- **Categories** — Organize tasks with color-coded categories
- **Tags** — Flexible tagging system for cross-cutting task organization
- **Advanced Filtering** — Filter tasks by status, priority, category, tags, and search keywords
- **Dashboard** — Real-time stats, charts (Chart.js), recent activity log
- **Export** — CSV and Excel download
- **JSON REST API** — Full API alongside HTML/HTMX interface
- **Dark Mode** — Persisted toggle
- **HTMX** — AJAX partial page updates, modals, instant actions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (WAL mode) |
| Migration | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| Frontend | Jinja2 + Bootstrap 5 |
| Dynamic UI | HTMX + Chart.js |
| Testing | pytest + httpx + Starlette TestClient |
| Container | Docker / docker-compose |

## Quick Start

```bash
# Clone and enter directory
cd todo-app

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000 — register an account and start managing tasks.

### Docker

```bash
docker compose up --build
```

## Project Structure

```
todo-app/
├── main.py                    # FastAPI app entry point
├── alembic.ini                # Alembic configuration
├── alembic/
│   └── versions/
│       └── 001_initial.py     # Initial migration
├── app/
│   ├── api/                   # Route handlers
│   │   ├── router.py          # Route aggregator
│   │   ├── auth_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── task_routes.py     # HTML + JSON REST
│   │   ├── category_routes.py
│   │   ├── tag_routes.py
│   │   └── export_routes.py
│   ├── core/                  # Infrastructure
│   │   ├── config.py          # Settings
│   │   ├── security.py        # JWT + bcrypt
│   │   └── dependencies.py    # DI (db, current user)
│   ├── database/
│   │   └── session.py         # DB engine + WAL
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   └── activity_log.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   └── dashboard.py
│   ├── repositories/          # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── task_repository.py
│   │   ├── category_repository.py
│   │   ├── tag_repository.py
│   │   └── activity_log_repository.py
│   ├── services/              # Business logic
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   ├── category_service.py
│   │   ├── tag_service.py
│   │   ├── export_service.py
│   │   └── activity_service.py
│   ├── templates/             # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/              # Login, Register
│   │   ├── dashboard/         # Dashboard page
│   │   ├── tasks/             # Task list, form, rows
│   │   ├── categories/        # Category list, form
│   │   ├── tags/              # Tag list, form
│   │   └── profile/           # Profile page
│   └── static/                # Static assets
│       ├── css/style.css
│       └── js/main.js
├── tests/
│   ├── conftest.py
│   ├── test_repositories.py
│   ├── test_api_auth.py
│   ├── test_api_tasks.py
│   └── test_api_categories_tags.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env / .env.example
```

## API Endpoints

### Web (HTML + HTMX)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard` | Dashboard with charts & stats |
| GET | `/tasks` | Task list (with filters) |
| GET | `/tasks/new` | New task form (modal) |
| POST | `/tasks` | Create task |
| GET | `/tasks/{id}/edit` | Edit task form |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| POST | `/tasks/{id}/complete` | Mark complete |
| POST | `/tasks/{id}/archive` | Archive task |
| POST | `/tasks/{id}/restore` | Restore task |
| POST | `/tasks/{id}/duplicate` | Duplicate task |
| GET | `/categories` | Category list |
| GET | `/tags` | Tag list |

### JSON REST API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tasks` | List tasks (all filters) |
| GET | `/api/tasks/{id}` | Get task detail |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |

### Export

| Method | Path | Description |
|--------|------|-------------|
| GET | `/export/csv` | Download as CSV |
| GET | `/export/excel` | Download as Excel (.xlsx) |

## Running Tests

```bash
pytest tests/ -v --tb=short
```
