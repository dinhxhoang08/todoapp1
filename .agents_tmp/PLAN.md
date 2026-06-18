# 1. OBJECTIVE

Build a complete, production-ready Todo List web application using Python 3.12+, FastAPI, SQLAlchemy 2.0, SQLite, Alembic, Pydantic v2, Jinja2 templates, Bootstrap 5, HTMX, and JWT/session authentication. The application will support user registration/login, task management (CRUD, archive, restore, complete, duplicate), categories, tags, full-text search, filtering/sorting, a Chart.js dashboard, activity logging, CSV/Excel export, dark mode, and Docker deployment.

# 2. CONTEXT SUMMARY

- **Workspace**: `/workspace/project` is completely empty (greenfield).
- **Database**: SQLite file-based at `app/database/todo.db`.
- **ORM**: SQLAlchemy 2.0 with async (optional) or sync sessions. Given SQLite simplicity, sync with connection pooling is fine; we can use `sqlalchemy` directly.
- **Auth**: JWT tokens stored in secure HttpOnly cookies + session fallback. Bcrypt via `passlib[bcrypt]`.
- **Frontend**: Jinja2 server-side rendering enhanced with HTMX for partial page updates. Bootstrap 5 + custom CSS for the SaaS dashboard look.
- **Charts**: Chart.js (CDN) on the dashboard.
- **Export**: CSV via Python csv module, Excel via `openpyxl`.
- **Testing**: pytest with httpx for API tests, coverage target 80%+.
- **Docker**: Multi-stage Dockerfile + docker-compose.yml with a single app service and SQLite volume.
- **Dependencies**: All packages listed in `requirements.txt`.

**Key constraints**:
- SQLite concurrency is limited — acceptable for single-user/multi-user with moderate load (WAL mode should be enabled).
- No task queue (Celery/Redis) — export and heavy operations run synchronously.
- The user explicitly asked for clean architecture layers: routers → services → repositories → models → schemas.
- All code must be executable, no pseudocode.

# 3. APPROACH OVERVIEW

The implementation is divided into **9 logical phases**, each building on the previous. Dependencies flow top-down:

1. **Scaffolding & Configuration** — project directory structure, requirements, env, Docker config, main entry point, Alembic setup.
2. **Core Infrastructure** — database engine, session factory, config management, security utilities (JWT, bcrypt, CSRF), app lifecycle.
3. **Data Layer (Models & Schemas)** — all SQLAlchemy models + Pydantic v2 schemas for request/response validation.
4. **Data Layer (Repositories)** — CRUD abstraction per entity with composable query methods for filtering, sorting, and searching.
5. **Business Logic (Services)** — auth, task, category, tag, activity, export services.
6. **API & Web Routes** — FastAPI routers for both JSON REST API and Jinja2 HTML endpoints.
7. **Frontend (Templates & Static)** — Jinja2 templates, Bootstrap 5 layout, HTMX enhanced partials, Chart.js dashboard, dark mode CSS, toast notifications.
8. **Testing** — pytest unit, API, and repository tests with coverage config.
9. **Polish & Documentation** — README, final verification.

Each file will be created in order such that the application can be tested incrementally (though the first fully runnable point is after Phase 6).

# 4. IMPLEMENTATION STEPS

---

## Phase 1: Project Scaffolding & Configuration

### Step 1.1 — Create directory structure

**Goal**: Create all required directories for the clean architecture layout.

**Method**:
```bash
mkdir -p {app/{api,services,repositories,models,schemas,templates,templates/{auth,dashboard,tasks,categories,tags,profile,components},static/{css,js,img},core,database},alembic/versions,tests}
```

**Files created**: Directory structure only.

---

### Step 1.2 — Create `requirements.txt`

**Goal**: Pin all Python dependencies.

**Method**: Write `requirements.txt` with these packages:
- `fastapi==0.115.*`
- `uvicorn[standard]==0.34.*`
- `sqlalchemy==2.0.*`
- `alembic==1.14.*`
- `pydantic==2.*`
- `pydantic-settings==2.*`
- `passlib[bcrypt]==1.7.*`
- `python-jose[cryptography]==3.3.*`
- `jinja2==3.1.*`
- `python-multipart==0.0.*`
- `python-dateutil==2.9.*`
- `openpyxl==3.1.*`
- `python-dotenv==1.0.*`
- `slowapi==0.1.*`
- `pytest==8.*`
- `pytest-cov==5.*`
- `httpx==0.27.*`
- `aiosqlite==0.20.*` (if using async; optional for sync)

---

### Step 1.3 — Create `.env.example`

**Goal**: Provide template for environment variables.

**Method**: Write `.env.example` with:
```
DATABASE_URL=sqlite:///./app/database/todo.db
SECRET_KEY=change-me-to-a-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEBUG=True
```

---

### Step 1.4 — Create `.env`

**Goal**: Copy of `.env.example` with real values for immediate development.

**Method**: Same content as `.env.example` but with a generated default secret key placeholder.

---

### Step 1.5 — Create `alembic.ini`

**Goal**: Alembic configuration pointing to our models.

**Method**: Use `alembic init alembic`-style configuration. Set `sqlalchemy.url = sqlite:///./app/database/todo.db` and reference `app.models.base` for `target_metadata`.

---

### Step 1.6 — Create `alembic/env.py`

**Goal**: Alembic environment that imports our Base and all models.

**Method**: In `alembic/env.py`:
- Set `target_metadata = app.models.Base.metadata`
- Import all model classes to ensure they are registered

---

### Step 1.7 — Create `Dockerfile`

**Goal**: Multi-stage Docker build.

**Method**:
- Stage 1: Python 3.12-slim, install dependencies from requirements.txt
- Expose port 8000
- Run `uvicorn main:app --host 0.0.0.0 --port 8000`

---

### Step 1.8 — Create `docker-compose.yml`

**Goal**: Single service app that mounts the SQLite data directory as a volume.

**Method**:
```yaml
version: '3.9'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app/database:/app/app/database
      - .env:/app/.env
    environment:
      - DATABASE_URL=sqlite:///./app/database/todo.db
```

---

## Phase 2: Core Infrastructure

### Step 2.1 — Create `app/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 2.2 — Create `app/core/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 2.3 — Create `app/core/config.py`

**Goal**: Central configuration via Pydantic Settings.

**Method**:
- Use `pydantic-settings.BaseSettings`
- Fields: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DEBUG`
- Load from `.env` file using `model_config = SettingsConfigDict(env_file=".env")`

---

### Step 2.4 — Create `app/core/security.py`

**Goal**: JWT creation/verification, password hashing, CSRF token generation.

**Method**:
- `create_access_token(data: dict) -> str` — uses `jose.jwt.encode` with HS256
- `verify_token(token: str) -> dict` — decodes and validates JWT
- `hash_password(password: str) -> str` — uses `passlib.hash.bcrypt`
- `verify_password(plain: str, hashed: str) -> bool`
- `create_csrf_token() -> str`
- `verify_csrf_token(token: str) -> bool`

---

### Step 2.5 — Create `app/core/dependencies.py`

**Goal**: FastAPI dependency injection — get DB session, get current user.

**Method**:
- `get_db()` — yields `Session` from `app.database.session_factory`
- `get_current_user()` — decodes JWT from request cookies, loads user from DB, or raises 401
- Optional: `get_optional_user()` — returns `None` if no valid token (for public pages)

---

### Step 2.6 — Create `app/database/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 2.7 — Create `app/database/session.py`

**Goal**: SQLAlchemy engine and session factory.

**Method**:
- Create engine with `create_engine` from `sqlalchemy`
- Enable WAL mode for SQLite via `@event.listens_for(engine, "connect")`
- `SessionLocal = sessionmaker(bind=engine)`
- `Base = declarative_base()`
- `init_db()` function to create all tables (for development; migrations for production)

---

## Phase 3: Data Layer (Models)

### Step 3.1 — Create `app/models/__init__.py`

**Goal**: Package init and import all models for Alembic.

**Method**: Import all model classes and `Base`.

---

### Step 3.2 — Create `app/models/base.py`

**Goal**: Declarative Base with common mixins.

**Method**:
- `Base = declarative_base()`
- Mixin class with `id`, `created_at`, `updated_at` fields

---

### Step 3.3 — Create `app/models/user.py`

**Goal**: User model.

**Method**:
- Fields: `id` (Integer PK), `username` (String, unique), `email` (String, unique), `hashed_password` (String), `is_active` (Boolean), `created_at`, `updated_at`
- Relationships: `tasks`, `categories`, `tags`, `activity_logs`

---

### Step 3.4 — Create `app/models/category.py`

**Goal**: Category model.

**Method**:
- Fields: `id`, `user_id` (FK), `name` (String), `color` (String, optional), `created_at`, `updated_at`
- Relationship: `tasks`

---

### Step 3.5 — Create `app/models/tag.py`

**Goal**: Tag model.

**Method**:
- Fields: `id`, `user_id` (FK), `name` (String, unique per user), `color` (String, optional), `created_at`
- Relationship: `tasks` through `task_tags`

---

### Step 3.6 — Create `app/models/task.py`

**Goal**: Task model.

**Method**:
- Fields: `id`, `user_id` (FK), `category_id` (FK, nullable), `title` (String, max 255), `description` (Text, nullable), `status` (Enum: pending/in_progress/completed/archived), `priority` (Enum: low/medium/high/urgent), `due_date` (DateTime, nullable), `completed_at` (DateTime, nullable), `created_at`, `updated_at`
- Relationships: `tags` through `task_tags`, `category`

---

### Step 3.7 — Create `app/models/task_tag.py`

**Goal**: Many-to-many association table.

**Method**:
- Fields: `task_id` (FK), `tag_id` (FK)
- Composite PK

---

### Step 3.8 — Create `app/models/activity_log.py`

**Goal**: Activity tracking.

**Method**:
- Fields: `id`, `user_id` (FK), `action` (String), `entity_type` (String), `entity_id` (Integer, nullable), `details` (Text, nullable), `created_at`

---

### Step 3.9 — Generate Alembic migration

**Goal**: Initial database migration.

**Method**: Write `alembic/versions/001_initial.py` — creates all tables with columns, constraints, and indexes (including FTS index for tasks if using `FTS5`).

Note: Since SQLite has limited ALTER TABLE support, initial migration should be the authoritative schema.

---

## Phase 4: Data Layer (Schemas)

### Step 4.1 — Create `app/schemas/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 4.2 — Create `app/schemas/user.py`

**Goal**: Pydantic v2 schemas for users.

**Method**:
- `UserCreate(BaseModel)` — username, email, password
- `UserLogin(BaseModel)` — username/email, password
- `UserResponse(BaseModel)` — id, username, email, is_active, created_at
- `UserUpdate(BaseModel)` — username, email
- `ChangePasswordRequest(BaseModel)` — old_password, new_password
- All with proper validators (email format, password min length, username constraints)

---

### Step 4.3 — Create `app/schemas/task.py`

**Goal**: Task schemas.

**Method**:
- `TaskCreate(BaseModel)` — title (required, max 255), description (optional, max 5000), priority (Enum), due_date (optional datetime), category_id (optional int), tag_ids (optional list[int])
- `TaskUpdate(BaseModel)` — same as create but all optional
- `TaskResponse(BaseModel)` — all fields + category name, tag names, timestamps
- Use `model_config = ConfigDict(from_attributes=True)`

---

### Step 4.4 — Create `app/schemas/category.py`

**Goal**: Category schemas.

**Method**:
- `CategoryCreate(BaseModel)` — name, color
- `CategoryUpdate(BaseModel)` — name, color
- `CategoryResponse(BaseModel)` — id, name, color, task_count, created_at

---

### Step 4.5 — Create `app/schemas/tag.py`

**Goal**: Tag schemas.

**Method**:
- `TagCreate(BaseModel)` — name, color
- `TagResponse(BaseModel)` — id, name, color, task_count, created_at

---

### Step 4.6 — Create `app/schemas/dashboard.py`

**Goal**: Dashboard data schema.

**Method**:
- `DashboardStats(BaseModel)` — total_tasks, completed_tasks, pending_tasks, overdue_tasks, completion_rate, tasks_by_status, tasks_by_priority, tasks_by_category, recent_activity

---

## Phase 5: Data Layer (Repositories)

### Step 5.1 — Create `app/repositories/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 5.2 — Create `app/repositories/base.py`

**Goal**: Generic CRUD base repository.

**Method**:
- `BaseRepository[T]` — generic class with:
  - `get(id) -> T | None`
  - `list(*, skip, limit, filters) -> list[T]`
  - `create(obj_in) -> T`
  - `update(id, obj_in) -> T`
  - `delete(id) -> None`
  - `count(filters) -> int`

---

### Step 5.3 — Create `app/repositories/user_repository.py`

**Goal**: User-specific DB operations.

**Method**:
- `UserRepository(BaseRepository[User])`:
  - `get_by_username(username) -> User | None`
  - `get_by_email(email) -> User | None`
  - `create_user(user_create) -> User`

---

### Step 5.4 — Create `app/repositories/task_repository.py`

**Goal**: Task DB operations with filtering, sorting, search.

**Method**:
- `TaskRepository(BaseRepository[Task])`:
  - `list_by_user(user_id, *, status, priority, due_date_from, due_date_to, category_id, tag_ids, search_query, sort_by, sort_order, skip, limit) -> list[Task]`
  - `get_by_user(user_id, task_id) -> Task | None`
  - `get_overdue(user_id) -> list[Task]`
  - `get_completion_stats(user_id) -> dict`
  - `search(user_id, query) -> list[Task]` — uses SQL `LIKE` on title and description
  - `count_by_status(user_id) -> dict`
  - `count_by_priority(user_id) -> dict`

---

### Step 5.5 — Create `app/repositories/category_repository.py`

**Goal**: Category CRUD.

**Method**:
- `CategoryRepository(BaseRepository[Category])`:
  - `list_by_user(user_id)`
  - `get_by_user(user_id, category_id)`
  - `get_task_count(category_id) -> int`

---

### Step 5.6 — Create `app/repositories/tag_repository.py`

**Goal**: Tag CRUD.

**Method**:
- `TagRepository(BaseRepository[Tag])`:
  - `list_by_user(user_id)`
  - `get_by_user(user_id, tag_id)`
  - `get_task_count(tag_id) -> int`

---

### Step 5.7 — Create `app/repositories/activity_log_repository.py`

**Goal**: Activity log queries.

**Method**:
- `ActivityLogRepository`:
  - `log_action(user_id, action, entity_type, entity_id, details)`
  - `get_recent(user_id, limit) -> list[ActivityLog]`

---

## Phase 6: Business Logic (Services)

### Step 6.1 — Create `app/services/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 6.2 — Create `app/services/auth_service.py`

**Goal**: Authentication business logic.

**Method**:
- `AuthService`:
  - `register(user_create) -> User` — validate uniqueness, hash password, create user, log activity
  - `login(user_login, remember_me) -> str` — verify credentials, return JWT
  - `change_password(user_id, old_password, new_password)` — verify old, hash new, update
  - `get_profile(user_id) -> User`

---

### Step 6.3 — Create `app/services/task_service.py`

**Goal**: Task business logic.

**Method**:
- `TaskService`:
  - `create_task(user_id, task_create) -> Task` — handle category/tag assignment, log activity
  - `update_task(user_id, task_id, task_update) -> Task`
  - `delete_task(user_id, task_id)` — log activity
  - `archive_task(user_id, task_id) -> Task`
  - `restore_task(user_id, task_id) -> Task`
  - `complete_task(user_id, task_id) -> Task`
  - `duplicate_task(user_id, task_id) -> Task` — create copy with "(copy)" suffix
  - `get_task(user_id, task_id) -> Task`
  - `list_tasks(user_id, filters) -> list[Task]`
  - `get_dashboard_stats(user_id) -> DashboardStats`

---

### Step 6.4 — Create `app/services/category_service.py`

**Goal**: Category business logic.

**Method**:
- `CategoryService`:
  - `create_category(user_id, category_create)`
  - `update_category(user_id, category_id, category_update)`
  - `delete_category(user_id, category_id)` — unlink tasks or prevent if tasks exist
  - `list_categories(user_id)`

---

### Step 6.5 — Create `app/services/tag_service.py`

**Goal**: Tag business logic.

**Method**:
- `TagService`:
  - `create_tag(user_id, tag_create)`
  - `delete_tag(user_id, tag_id)`
  - `list_tags(user_id)`

---

### Step 6.6 — Create `app/services/export_service.py`

**Goal**: CSV and Excel export.

**Method**:
- `ExportService`:
  - `export_tasks_csv(user_id) -> StringIO` — write CSV with headers
  - `export_tasks_excel(user_id) -> BytesIO` — create workbook with openpyxl, return BytesIO

---

### Step 6.7 — Create `app/services/activity_service.py`

**Goal**: Activity logging service.

**Method**:
- `ActivityService`:
  - `log(user_id, action, entity_type, entity_id, details)`
  - `get_recent(user_id, limit=10)`

---

## Phase 7: API & Web Routes

### Step 7.1 — Create `app/api/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 7.2 — Create `app/api/router.py`

**Goal**: Central API router aggregator.

**Method**: Create an `APIRouter` that includes all sub-routers.

---

### Step 7.3 — Create `app/api/auth_routes.py`

**Goal**: Authentication endpoints.

**Method**:
- `GET /auth/login` — render login page
- `POST /auth/login` — authenticate, set JWT cookie, redirect
- `GET /auth/register` — render register page
- `POST /auth/register` — create user, set JWT cookie, redirect
- `POST /auth/logout` — clear cookie, redirect
- `GET /auth/profile` — render profile page
- `POST /auth/change-password` — change password
- `POST /auth/profile/update` — update profile info

---

### Step 7.4 — Create `app/api/dashboard_routes.py`

**Goal**: Dashboard endpoints.

**Method**:
- `GET /` — redirect to /dashboard
- `GET /dashboard` — render dashboard with stats, recent activity, Chart.js data
- `GET /dashboard/stats` — HTMX partial — returns JSON for chart updates

---

### Step 7.5 — Create `app/api/task_routes.py`

**Goal**: Task management endpoints (both HTML and JSON).

**Method**:

**HTML endpoints (HTMX-friendly)**:
- `GET /tasks` — list tasks with filters/sort/search (renders HTML)
- `GET /tasks/new` — modal form for new task
- `POST /tasks` — create task, return HTMX fragment
- `GET /tasks/{id}/edit` — edit form modal
- `PUT /tasks/{id}` — update task, return HTMX fragment
- `DELETE /tasks/{id}` — delete task
- `POST /tasks/{id}/complete` — toggle complete
- `POST /tasks/{id}/archive` — toggle archive
- `POST /tasks/{id}/restore` — restore from archive
- `POST /tasks/{id}/duplicate` — duplicate task

**JSON REST API endpoints**:
- `GET /api/tasks` — list tasks (JSON)
- `GET /api/tasks/{id}` — get task (JSON)
- `POST /api/tasks` — create task (JSON)
- `PUT /api/tasks/{id}` — update task (JSON)
- `DELETE /api/tasks/{id}` — delete task (JSON)

---

### Step 7.6 — Create `app/api/category_routes.py`

**Goal**: Category management.

**Method**:
- `GET /categories` — list categories
- `GET /categories/new` — create form modal
- `POST /categories` — create category
- `GET /categories/{id}/edit` — edit form modal
- `PUT /categories/{id}` — update category
- `DELETE /categories/{id}` — delete category

---

### Step 7.7 — Create `app/api/tag_routes.py`

**Goal**: Tag management.

**Method**:
- `GET /tags` — list tags
- `POST /tags` — create tag
- `DELETE /tags/{id}` — delete tag

---

### Step 7.8 — Create `app/api/export_routes.py`

**Goal**: Export endpoints.

**Method**:
- `GET /export/csv` — download CSV file
- `GET /export/excel` — download Excel file

---

## Phase 8: Frontend (Templates & Static)

### Step 8.1 — Create base layout template

**File**: `app/templates/base.html`

**Goal**: Full Bootstrap 5 + HTMX layout with:
- Navigation sidebar (collapsible on mobile)
- Dark mode toggle (CSS class on body, persisted in localStorage)
- Toast notification container
- Block structure for title, head_extra, content, scripts

---

### Step 8.2 — Create components

**Files**: `app/templates/components/`
- `toast.html` — toast notification snippet (triggered via HTMX response headers)
- `modal.html` — reusable modal wrapper
- `pagination.html` — pagination component
- `task_card.html` — task card partial (for HTMX updates)
- `empty_state.html` — empty state with illustration

---

### Step 8.3 — Create auth templates

**Files**: `app/templates/auth/`
- `login.html` — login form with username/email and password, remember me checkbox
- `register.html` — registration form
- `profile.html` — profile page with edit form and change password form

---

### Step 8.4 — Create dashboard template

**File**: `app/templates/dashboard/index.html`

**Goal**: Modern SaaS dashboard with:
- Stat cards (total, completed, pending, overdue, completion rate)
- Chart.js area/bar chart showing tasks per status
- Chart.js donut chart for priority distribution
- Recent activity feed
- Quick-add task button

---

### Step 8.5 — Create task templates

**Files**: `app/templates/tasks/`
- `list.html` — full task list with filter bar (status, priority, category, date range, search), sort dropdown, task table/cards, bulk actions
- `filters.html` — HTMX filter partial (reloads task list on change)
- `task_rows.html` — HTMX partial for the task table rows (updated by filters/pagination)
- `form.html` — modal form for create/edit task
- `detail.html` — single task view modal/panel

---

### Step 8.6 — Create category templates

**Files**: `app/templates/categories/`
- `list.html` — category cards with task count, color indicator
- `form.html` — modal form for create/edit

---

### Step 8.7 — Create tag templates

**Files**: `app/templates/tags/`
- `list.html` — tag pills/badges with task count
- `form.html` — modal form for create

---

### Step 8.8 — Create static assets

**CSS** (`app/static/css/`):
- `style.css` — custom styles:
  - Dark mode variables (`.dark-mode` class)
  - SaaS-style card styling
  - Smooth transitions
  - Custom scrollbars
  - Sidebar layout
  - Form styling enhancements

**JS** (`app/static/js/`):
- `main.js` — core functionality:
  - Dark mode toggle (persists to localStorage)
  - Toast notification handler (listens for HTMX `HX-Trigger` headers)
  - Form validation styling
  - Modal handlers
  - Confirm dialogs for destructive actions
  - Loading indicator management (hx-indicator)
- `dashboard.js` — Chart.js initialization and data fetching (auto-refresh options)

**Favicon**: `app/static/img/favicon.ico` (simple SVG or placeholder)

---

### Step 8.9 — Create `main.py`

**Goal**: Application entry point.

**Method**:
- Create FastAPI app with:
  - Jinja2Templates mounted
  - Static files mounted at `/static`
  - Include HTML routers
  - Include API routers (prefixed with `/api`)
  - CSRF middleware
  - Rate limiting via slowapi
  - Lifespan handler (init DB, run Alembic migration on startup optionally)
- Configure session middleware (or use JWT entirely)
- Configure CORS if needed

---

## Phase 9: Testing

### Step 9.1 — Create `tests/__init__.py`

**Goal**: Package init.

**Method**: Empty file.

---

### Step 9.2 — Create `tests/conftest.py`

**Goal**: Test fixtures.

**Method**:
- `db_session()` — in-memory SQLite session for tests
- `test_client()` — `httpx.AsyncClient` with FastAPI app
- `test_user()` — create a test user
- `test_task()` — create a test task
- `auth_headers()` — JWT token for test user

---

### Step 9.3 — Create `tests/test_repositories.py`

**Goal**: Repository unit tests.

**Method**: Test each repository CRUD operation and query method with at least one happy path and one edge case per method.

---

### Step 9.4 — Create `tests/test_api_auth.py`

**Goal**: Auth endpoint tests.

**Method**:
- Register (success, duplicate username, duplicate email, invalid data)
- Login (success, wrong password, non-existent user)
- Logout clears cookie
- Change password (success, wrong old password)

---

### Step 9.5 — Create `tests/test_api_tasks.py`

**Goal**: Task API tests.

**Method**:
- CRUD operations
- Status transitions
- Archive/restore
- Complete
- Duplicate
- Filtering, sorting, search

---

### Step 9.6 — Create `tests/test_api_categories.py`

**Goal**: Category API tests.

**Method**:
- CRUD operations
- Preventing delete of category with tasks (configurable behavior)

---

### Step 9.7 — Create `tests/test_api_tags.py`

**Goal**: Tag API tests.

**Method**:
- Create, delete tag
- Assign tags to tasks
- Verify tag-task relationship

---

### Step 9.8 — Create `tests/test_export.py`

**Goal**: Export functionality tests.

**Method**:
- CSV export returns valid CSV with correct headers
- Excel export returns valid .xlsx file

---

### Step 9.9 — Create `pytest.ini` or `pyproject.toml` test config

**Goal**: Coverage configuration.

**Method**: In `pyproject.toml` or `pytest.ini`:
```
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=app --cov-report=term-missing --cov-fail-under=80"
```

---

## Phase 10: Documentation

### Step 10.1 — Create `README.md`

**Goal**: Comprehensive project documentation.

**Method**: Include:
- Project title and description
- Features list
- Tech stack
- Quick start (docker, manual)
- Project structure tree
- Configuration
- API documentation summary
- Testing instructions
- License

---

# 5. TESTING AND VALIDATION

## Manual Validation (Post-Implementation)

1. **Docker build & run**: `docker compose up --build` starts successfully, app accessible at `http://localhost:8000`
2. **Registration**: Navigate to `/auth/register`, create account, redirected to dashboard
3. **Login/Logout**: Login with created account, verify session persists, logout clears
4. **Dashboard**: View stats, verify charts render, verify counts are correct
5. **Task CRUD**: Create task via modal, verify it appears in list; edit; complete; archive; restore; delete; duplicate
6. **Categories**: Create category, assign to task, edit, delete
7. **Tags**: Create tag, assign to tasks via multi-select, filter by tag
8. **Search**: Search by title, description — results update via HTMX
9. **Filters**: Filter by status, priority, date range — list updates without page reload
10. **Export**: Download CSV and Excel, verify content
11. **Dark mode**: Toggle dark mode, refresh page — mode persists
12. **Responsive**: Test on mobile viewport — sidebar collapses, cards stack

## Automated Testing

- Run `pytest` — all tests pass
- Coverage report shows ≥80% coverage
- Specific assertions:
  - Auth tests: successful register returns user data; login with bad credentials returns 401; duplicate registration returns 400
  - Task tests: create returns correct data; update modifies fields; delete removes; archive sets status; duplicate creates copy
  - Category tests: delete with tasks either fails or unlinks; delete without tasks succeeds
  - Export tests: CSV has correct header row; Excel opens without corruption
  - Repository tests: filtering returns correct subset; search finds matching records

## Security Validation

- Passwords stored as bcrypt hashes (not plaintext)
- JWT tokens expire after configured duration
- CSRF token validated on state-changing POST requests
- Rate limiting on auth endpoints (5 attempts per minute)
- SQL injection not possible via parameterized queries (SQLAlchemy)
- Input validation via Pydantic rejects malformed data
- No sensitive data exposed in error responses

## Edge Cases

- Empty task list shows "No tasks yet" empty state
- Empty search results show "No results found"
- Overdue tasks highlighted in red on dashboard
- SQLite WAL mode handles concurrent reads
- Long task titles truncated in table view
- Special characters in task title/description handled safely
- Dates in the past can be set (user choice)
- Removing all tags from a task works
- Category deletion with tasks shows warning or prevents
