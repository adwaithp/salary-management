# Architecture & Design Decisions

## System Overview

```
Browser → React (Vite, :3000)
            ↓ /api/* proxy
         Django + DRF (:8000)
            ↓
         PostgreSQL (:5432)
```

## Data Model

Single `employees` table. No separate HR/admin table.

```
Employee
─────────────────────────────────────
id           SERIAL PK
user_id      FK → auth_user (nullable) — only set for HR login accounts
first_name   VARCHAR(100)
last_name    VARCHAR(100)
email        EMAIL UNIQUE
job_title    VARCHAR(100)
department   VARCHAR(50)  ENUM choices
country      VARCHAR(100)
salary       NUMERIC(12,2)
hire_date    DATE
is_active    BOOLEAN DEFAULT true
created_at   TIMESTAMPTZ
updated_at   TIMESTAMPTZ

Indexes: country, job_title, (country, job_title)
```

**Why single table?** HR staff and employees share the same data shape. Separating into HR/Employee tables would add joins for zero benefit at this scope.

**Why `user` is nullable?** Only HR accounts need login. Seeded employees and API-created employees are pure data records. The `user=NULL` marker cleanly separates seeded data from real accounts.

## Layer Responsibilities

```
views.py      → HTTP in/out, auth, routing to services
services.py   → aggregation logic (pure functions, no HTTP)
serializers.py → data validation and shape
models.py     → schema and DB constraints only
```

Services are pure functions: `get_country_salary_summary(queryset)` — the caller controls the filter. This makes them trivially testable without HTTP.

## Auth Design

- HR accounts created via `create_hr_user` management command or Django admin
- No public registration endpoint
- JWT tokens (60 min expiry)
- `IsAuthenticated` — any logged-in user has full access (all users are HR)

## Seed Script Performance

```
❌ Naive:  10,000 × INSERT  = 10,000 DB round-trips
✅ Ours:   20 × bulk_create = 20 DB round-trips (batch_size=500)
```

Name files read once into memory. All Employee objects built in Python first, then inserted in batches.

## Trade-offs

| Decision | Alternative | Why this way |
|----------|-------------|--------------|
| Single Employee table | Separate HR + Employee tables | No unique data per role; joins add complexity for zero gain |
| Soft delete | Hard delete | Preserves salary history for auditing |
| No employee login | Employee self-service portal | User persona is HR manager only |
| `@property` for full_name | DB column | No need to query by full_name; first+last are indexed separately |
| SQLite for tests | Test Postgres | Faster test cycle; schema is simple enough that SQLite differences don't matter |
