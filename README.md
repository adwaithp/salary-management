# Salary Management Tool

A full-stack salary management application for HR teams to manage employee records and view salary insights across a 10,000-person organisation.

---

## AI-Assisted Development

This project was designed and built using **Claude (Anthropic)** as an AI pair programmer.

The approach was intentional — not vibe coding. I drove every architectural decision, defined the requirements, designed the data model, chose the tech stack, and directed the implementation through precise technical instructions. Claude accelerated the implementation while I maintained full ownership of:

- System architecture and design trade-offs
- TDD approach — writing failing tests first, then implementation
- Incremental commit strategy to show solution evolution
- Code review — understanding and validating all generated code before committing
- Debugging and course-correcting when output didn't meet requirements

See `artifacts/` for design notes, architecture decisions, and a log of how AI was used throughout.

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Django 5 + Django REST Framework    |
| Database  | PostgreSQL                          |
| Auth      | JWT (djangorestframework-simplejwt) |
| Frontend  | React + Vite + Tailwind CSS         |
| Container | Docker + Docker Compose             |

---

## Quick Start (Docker)

```bash
git clone <repo-url>
cd salary-management
docker-compose up --build
```

This automatically:
1. Starts PostgreSQL
2. Runs Django migrations
3. Creates a default HR admin account
4. Seeds 10,000 employees
5. Starts the API on `http://localhost:8000`
6. Starts the frontend on `http://localhost:3000`

**Login at:** `http://localhost:3000`
```
Email:    admin@company.com
Password: admin123
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- [uv](https://docs.astral.sh/uv/) package manager

### Backend

```bash
uv sync
cp .env.example .env 

python manage.py migrate
python manage.py create_hr_user \
  --email hr@company.com \
  --password yourpassword \
  --first-name Jane \
  --last-name Doe
python manage.py seed_employees
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000` and proxies API calls to `http://localhost:8000`.

### Running migrations with Docker Postgres

```bash
# While containers are running
docker-compose exec backend uv run python manage.py makemigrations
docker-compose exec backend uv run python manage.py migrate

# Or rebuild — migrate runs automatically on startup
docker-compose down && docker-compose up --build
```

---

## Creating Additional HR Users

HR accounts can only be created in two ways — there is no public registration endpoint by design.

**Option 1 — Management command:**
```bash
python manage.py create_hr_user \
  --email newhr@company.com \
  --password securepass123 \
  --first-name Alice \
  --last-name Smith
```

**Option 2 — Django Admin panel:**
1. Go to `http://localhost:8000/admin/`
2. Log in with a superuser account
3. Create a `User` under **Authentication and Authorization**
4. Create an `Employee` record linked to that user

To create a Django superuser:
```bash
python manage.py createsuperuser
```

---

## API Reference

| Method | Endpoint                        | Description                                          | Auth |
|--------|---------------------------------|------------------------------------------------------|------|
| POST   | `/api/auth/token/`              | Login — returns access + refresh token               | No   |
| POST   | `/api/auth/token/refresh/`      | Refresh access token                                 | No   |
| GET    | `/api/employees/`               | List employees (paginated, filterable, searchable)   | Yes  |
| POST   | `/api/employees/`               | Create employee                                      | Yes  |
| GET    | `/api/employees/{id}/`          | Get employee detail                                  | Yes  |
| PUT    | `/api/employees/{id}/`          | Full update                                          | Yes  |
| PATCH  | `/api/employees/{id}/`          | Partial update                                       | Yes  |
| DELETE | `/api/employees/{id}/`          | Soft delete                                          | Yes  |
| GET    | `/api/insights/overview/`       | Org-wide: total headcount, avg/min/max salary        | Yes  |
| GET    | `/api/insights/by-country/`     | Salary stats grouped by country                      | Yes  |
| GET    | `/api/insights/by-job-title/`   | Avg salary by job title (`?country=India`)           | Yes  |
| GET    | `/api/insights/by-department/`  | Salary stats grouped by department                   | Yes  |
| GET    | `/api/insights/top-earners/`    | Top N earners (`?limit=10`)                          | Yes  |

**Interactive docs:**
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

**Authentication:**
```
Authorization: Bearer <access_token>
```

**Employee list query params:**
```
?search=alice
?country=India
?department=engineering
?job_title=Engineer
?ordering=-salary
```

---

## Running Tests

```bash
pytest                          # all tests
pytest --cov=salary_app         # with coverage
pytest salary_app/tests/test_services.py -v   # specific file
```

---

## Project Structure

```
salary-management/
├── artifacts/                        # Design notes, AI usage log, decisions
├── data/
│   ├── first_names.txt
│   └── last_names.txt
├── salary_app/
│   ├── management/commands/
│   │   ├── create_hr_user.py         # Create HR login accounts
│   │   └── seed_employees.py         # Seed 10k employees (bulk_create)
│   ├── tests/
│   │   ├── test_model.py
│   │   ├── test_auth.py
│   │   ├── test_services.py
│   │   ├── test_insights_api.py
│   │   ├── test_create_hr_user.py
│   │   └── test_seed_employees.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py                   # Salary aggregation — pure functions
│   └── views.py
├── salary_management/
│   ├── settings.py
│   └── urls.py
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Employees.jsx
│       │   └── Insights.jsx
│       └── api/
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

---

## Key Design Decisions

**HR-only access** — Only HR accounts (created via command or Django admin) can log in. Employee records are pure data — no login accounts for individual employees. This matches the user persona: an HR manager tool, not a self-service portal.

**Soft delete** — `is_active=False` instead of hard delete. Salary history is preserved for auditing and trend analysis.

**Service layer for insights** — All aggregation logic lives in `services.py` as pure functions that accept a queryset. Views stay thin. Services are unit-tested independently without any HTTP overhead.

**Seed performance** — `bulk_create(batch_size=500)` means 20 INSERT statements for 10,000 rows instead of 10,000. Name files are read once into memory before the loop, not per-row. The `--clear` flag removes only seeded employees (`user=NULL`), preserving real HR accounts.

**Three DB indexes** on `country`, `job_title`, and `(country, job_title)` — directly serve the insights aggregation queries. On 10k rows, this turns full table scans into index scans.