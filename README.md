# Finance Dashboard API

A backend API for managing financial records with role-based access control .

## Tech Choices & Assumptions

- **FastAPI** — I've been using it in my personal projects (Market Data Service, Signal Trade Automation) and it's the framework I'm most productive in.
- **SQLite** — Chose this over PostgreSQL so you can clone and run without Docker or database setup. The SQLAlchemy layer is database-agnostic, so switching to Postgres only requires changing the connection URL.
- **JWT auth** — Tokens expire after 30 minutes. In production, I'd add refresh tokens, but kept it simple here.
- **Categories are free-text** — I didn't use a strict enum for categories because in real finance tools, users want flexibility to create their own categories.

## Quick Start
```bash
# Clone and setup
git clone 
cd finance-backend
pip install -r requirements.txt

# Seed the database with test data
python seed.py

# Run the server
uvicorn app.main:app --reload
```

API docs available at: http://127.0.0.1:8000/docs

## Test Credentials

| Role    | Username | Password    |
|---------|----------|-------------|
| Admin   | admin    | admin123    |
| Analyst | analyst  | analyst123  |
| Viewer  | viewer   | viewer123   |

## API Overview

### Auth
- `POST /users/login` — Get JWT token
- `POST /users/register` — Create user (Admin only)
- `GET /users/me` — View own profile

### Transactions
- `POST /transactions/` — Create record (Admin only)
- `GET /transactions/` — List with filters: `category`, `type`, `start_date`, `end_date`, `limit`, `offset`
- `GET /transactions/{id}` — Get single record
- `PUT /transactions/{id}` — Update record (Admin only)
- `DELETE /transactions/{id}` — Delete record (Admin only)

### Dashboard
- `GET /dashboard/summary` — Total income, expenses, net balance (all roles)
- `GET /dashboard/category-breakdown` — Category-wise totals (Analyst, Admin)
- `GET /dashboard/monthly-trends` — Monthly income vs expense (Analyst, Admin)

## Role Permissions

| Action              | Viewer | Analyst | Admin |
|---------------------|--------|---------|-------|
| View summary        | Yes    | Yes     | Yes   |
| View transactions   | Yes    | Yes     | Yes   |
| Category breakdown  | No     | Yes     | Yes   |
| Monthly trends      | No     | Yes     | Yes   |
| Create/Edit/Delete  | No     | No      | Yes   |
| Manage users        | No     | No      | Yes   |

## What I'd Add With More Time

- Refresh tokens for better auth flow
- Soft delete instead of hard delete
- Unit tests with pytest
- Rate limiting on login endpoint
- Environment-based config (dev/staging/prod)