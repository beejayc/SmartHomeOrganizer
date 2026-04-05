# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Smart Home Organizer

## Project Overview

**Smart Home Organizer** is a web and mobile application for families to track and manage family activites. Key activities to track - kids' daily activities—food intake, moods, play dates schedule —in one place. It also organizes multistore grocery lists. Calendar appointments for the families.

**Key Features:**
- Unified interface (web + mobile) for activity logging
- Multi-channel input: WhatsApp (voice, text), email, calendar invites sync to → single dashboard
- Google Calendar and Google Keep integration
- Voice notes transcription and extraction of information
- Grocery organization across multiple stores
- Daily reminders
- Authentication with password access
- Data security as core requirement

**Users:** Families with young children; caregivers, nannies, parents.

---

## Architecture & Tech Stack

### Backend
- **Framework:** Python FastAPI.
- **Database:** PostgreSQL 16 (Running on Ubuntu machine).
- **Task Queue:** Redis (for handling background transcription and reminders).
- **Integrations:** - Google Calendar API / MCPs.
  - Google Keep API / MCPs.
  - WhatsApp (via whatsapp-bridge Go server ).
  - OpenAI SDK for local LLM inference.
- **AI Stack (Local):** - **Transcription:** OpenAI Whisper (running locally).
  - **Logic/Analysis:** Local LLM (served via Ollama or LocalAI) for parsing transcriptions and sorting messages.

### Frontend
- **Web:** React (Next.js preferred for routing simplicity).
- **Mobile:** React Native.
- **Philosophy:** "Thin" frontend—UI is a presentation layer; all business logic resides in the FastAPI backend.

### Data Flow (High-Level)
1. **User Input → Frontend:** User logs in, adds activity, or views dashboard.
2. **Frontend → Backend API:** Requests sent via REST to FastAPI endpoints.
3. **Backend Processing:** 
   - Handles auth, validation, business logic
   - Queries PostgreSQL for user data and activity logs
   - Pushes background tasks to Redis (transcription, reminders, calendar sync)
4. **Async Tasks (Redis Queue):**
   - WhatsApp messages → transcribed by Whisper (AI-engine) → parsed by local LLM → stored in DB
   - Daily reminders → generated, sent via email/SMS
   - Calendar sync → triggered on schedule, pulls events from Google Calendar API → stores/updates in DB
5. **External Integrations:**
   - Google Calendar/Keep APIs for sync (read/write)
   - WhatsApp Bridge (via `whatsapp-mcp`) for incoming messages
   - OpenAI Whisper (running locally in `ai-engine`) for transcription
6. **Response → Frontend:** Backend returns JSON; frontend displays in UI.

## Deployment & Docker Strategy (Ubuntu Host)

The application is deployed on a dedicated Ubuntu machine using **Docker Compose** for service orchestration.

### Container Orchestration
1.  **`backend`**: FastAPI application.
2.  **`db`**: PostgreSQL with persistent volume mapping to `/var/lib/postgresql/data`.
3.  **`ai-engine`**: Dedicated container for local LLM/Whisper inference (Ollama/LocalAI). 
4.  **`redis`**: Message broker for asynchronous task handling.
5.  **`nginx`**: Reverse proxy handling SSL/HTTPS termination.

### Docker Guidelines
- **Internal Networking:** Only the Nginx and Backend containers should expose public ports. The DB and AI-Engine stay on an internal Docker network.
- **Persistence:** All data-heavy directories (Postgres data, local model weights) must be mounted as host volumes to survive container restarts.
- **Resource Allocation:** Ensure the `ai-engine` container has access to necessary CPU/GPU resources on the Ubuntu host.
- **Health Checks:** Implement `depends_on` with `service_healthy` conditions to ensure the DB is ready before the Backend starts.


---



## Working Style & Priorities

### Team
- 2 engineers
- User (PM) is non-frontend developer—logic should live in Python backend and serve the front end as API calls

### Development Approach
1. **Speed & pragmatism over perfection.** Get features working quickly; refine later if needed.
2. **Backend-first.** When unclear, push logic to FastAPI; keep frontend dumb.
3. **Security first.** Auth, data encryption, and access control are non-negotiable from day one.
4. **Simplicity.** Intuitive UX matters—no complex dashboards or hidden workflows.

---

## Key Requirements

### Must-Have
- [x] Authentication (password-based login)
- [x] Data security (encryption at rest, secure transport)
- [x] Google Calendar sync (read/write events)
- [x] Google Keep sync (read/write notes)
- [x] WhatsApp input channel (voice, text, calendar parsing)
- [x] Grocery tracker across stores
- [x] Daily activity logging (food, moods, play dates)
- [x] Daily reminders (email, push, SMS)
- [x] Web interface
- [x] Mobile interface

### Nice-to-Have (Later)
- Two-factor authentication
- Role-based access (parent vs. nanny)
- Reporting/analytics
- Offline sync
- Advanced grocery list sharing

---

## Project Constraints & Gotchas

### What to Avoid
- **Don't over-engineer the frontend.** React/React Native should be thin wrappers around FastAPI endpoints.
- **Don't store secrets in code.** Use environment variables (`.env`, secrets manager).
- **Don't integrate WhatsApp directly without a service.** Use Twilio, MessageBird, or similar for reliability.
- **Don't skip auth early.** Build password auth and basic encryption from the start.
- **Don't assume calendar formats.** Google Calendar and email invites have edge cases—handle gracefully.

### Infrastructure Notes
- Ubuntu machine: ensure it has enough disk for PostgreSQL + backups.
- Network: secure HTTPS only (use reverse proxy like Nginx).
- Backups: automate daily DB backups.

---

## Code & Repository Guidelines

### File Structure
```text
smart-home-organizer/
├── docker-compose.yml
├── .env.example
├── backend/              # FastAPI app
│   ├── app/
│   │   ├── models/       # Pydantic & SQLAlchemy schemas
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic & AI orchestration
│   │   └── integrations/ # Google/WhatsApp/MCP/Local LLM clients
│   │   └── auth/         # Authentication   
│   └── Dockerfile
├── frontend/             # React web app
├── mobile/               # React Native app
└── nginx/                # Reverse proxy configuration
└── docs/                 # Deployment, API docs



### Code Style & Standards
- **Python:** Follow PEP 8. Use type hints for clarity.
- **React:** Functional components, hooks. Keep components small and focused.
- **Commits:** Clear, actionable messages. Reference issues or features.
- **Testing:** Unit tests for backend services. Integration tests for APIs.
- **Documentation:** API docs (FastAPI auto-generates). Document integrations.

### API Design Patterns
- **Routes:** Group related endpoints in `app/routes/` by domain (e.g., `auth.py`, `activities.py`, `reminders.py`).
- **Request/Response Models:** Use Pydantic models for validation and serialization. Keep models in `app/models/schemas.py`.
- **Error Handling:** Return consistent error responses with HTTP status codes and descriptive messages.
  ```python
  # Example error response
  {"detail": "User not found", "status": 404, "error_code": "USER_NOT_FOUND"}
  ```
- **Pagination:** For list endpoints, support `?page=1&limit=20`. Return metadata: `{"items": [...], "total": 100, "page": 1}`.
- **Authentication:** Use JWT tokens in `Authorization: Bearer <token>` header. Validate on protected routes via dependency injection.
- **Rate Limiting:** Implement on auth endpoints (prevent brute force) and public APIs (prevent abuse).

### Database Patterns
- **Models:** Keep SQLAlchemy models in `app/models/database.py`. Use descriptive column names and proper indexing.
- **Migrations:** Use Alembic for all schema changes. Never manually alter production databases.
  ```bash
  alembic revision --autogenerate -m "Describe change"
  alembic upgrade head
  ```
- **Relationships:** Properly define foreign keys and relationships. Use lazy loading strategically to avoid N+1 queries.
- **Timestamps:** Add `created_at` and `updated_at` to all tables for audit trails.
- **Soft Deletes:** For critical data, use `deleted_at` column instead of hard deletes where appropriate.

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ (for web frontend)
- PostgreSQL 16
- Redis
- Docker & Docker Compose (for running full stack)
- `uvx` (from the [`uv`](https://docs.astral.sh/uv/) package manager) — used to spawn MCP processes

### Backend Setup
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with local PostgreSQL and Redis connection details

# Initialize database
cd backend && alembic upgrade head && cd ..

# Run FastAPI server in development
cd backend && uvicorn app.main:app --reload && cd ..
```

### Frontend Setup
```bash
# Web (React/Next.js)
cd frontend && npm install && npm run dev

# Mobile (React Native)
cd mobile && npm install && npm start
```

### Running Full Stack (Docker)
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend  # or db, redis, ai-engine, nginx

# Tear down
docker-compose down -v  # -v removes volumes
```

### WhatsApp Integration (Optional)
The WhatsApp integration uses `whatsapp-mcp` (MCP server wrapper around WhatsApp Bridge). To enable:
```bash
# First-time setup: clone and run whatsapp-bridge
git clone https://github.com/lharries/whatsapp-mcp
cd whatsapp-mcp/whatsapp-bridge
go run main.go  # Scan QR code to link phone

# The backend will spawn `uvx whatsapp-mcp` automatically when configured
```

---

## Common Development Commands

### Backend
```bash
# Run tests
cd backend && pytest

# Run specific test file
cd backend && pytest tests/test_auth.py

# Run with coverage
cd backend && pytest --cov=app tests/

# Lint and format
cd backend && ruff check . && ruff format .

# Type checking
cd backend && mypy app/

# Database migrations
cd backend && alembic revision --autogenerate -m "Add users table"
cd backend && alembic upgrade head
cd backend && alembic downgrade -1  # Rollback one migration
```

### Frontend (Web)
```bash
# Development server
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Run tests
cd frontend && npm test

# Lint
cd frontend && npm run lint
```

### Frontend (Mobile)
```bash
# Development
cd mobile && npm start

# Run on iOS
cd mobile && npm run ios

# Run on Android
cd mobile && npm run android

# Tests
cd mobile && npm test
```

---

## Testing Strategy

### Backend
- **Unit Tests:** Test individual services, data models, and utilities. Mock external APIs and databases.
- **Integration Tests:** Test API endpoints against a real test database. Verify data flow through the system.
- **Test Structure:** Place tests in `backend/tests/` mirroring app structure (e.g., `tests/services/test_auth_service.py` for `app/services/auth_service.py`).
- **Fixtures:** Use pytest fixtures for common test data (mock users, test tokens, sample activities).
- **Database:** Use a separate PostgreSQL test database or in-memory SQLite for speed.
- **Coverage Goal:** Aim for 70%+ coverage on critical paths (auth, API endpoints, integrations).

### Frontend
- **Unit Tests:** Test React components and utility functions. Use React Testing Library (avoid Enzyme).
- **Integration Tests:** Test user flows end-to-end (login → add activity → view dashboard).
- **Snapshot Tests:** Use sparingly for UI components that are stable.
- **E2E Tests:** Use Playwright or Cypress for critical user journeys (optional for early stage).

### Async Tasks & Integrations
- **Mock Redis:** Use `fakeredis` or similar for testing task queues without a running Redis.
- **Mock External APIs:** Use `unittest.mock` or `responses` library to mock Google Calendar, WhatsApp, etc.
- **Task Testing:** Verify that background jobs (transcription, reminders) enqueue properly and produce correct outputs.

---

## Debugging & Troubleshooting

### Backend Issues
- **Database connection errors:** Check PostgreSQL is running and credentials in `.env` are correct.
  ```bash
  psql -h localhost -U postgres -d smart_home -c "SELECT 1"
  ```
- **Task queue issues:** Verify Redis is running and accessible.
  ```bash
  redis-cli ping  # Should return PONG
  ```
- **Import errors:** Ensure you're in the correct directory when running code. Use absolute imports from `app/`.
- **FastAPI doesn't reload:** Check file permissions and that `--reload` flag is used during development.
- **Integration test failures:** Mock external APIs properly; don't hit real APIs in tests.

### Frontend Issues
- **Module not found:** Ensure dependencies are installed (`npm install`). Clear node_modules if needed.
- **CORS errors:** Backend CORS is misconfigured. Check FastAPI `CORSMiddleware` settings match frontend origin.
- **API calls return 401:** Token may be expired or invalid. Check JWT token in localStorage and refresh if needed.

### Docker Issues
- **Container won't start:** Check logs with `docker-compose logs service_name`. Verify port conflicts.
- **Database won't initialize:** Ensure migrations ran. Run `docker-compose exec backend alembic upgrade head`.
- **Secrets not accessible:** Verify `.env` file exists and variables are loaded in `docker-compose.yml`.

### Quick Diagnostics
```bash
# Check all services are running
docker-compose ps

# View backend logs in real-time
docker-compose logs -f backend

# Run a quick backend health check
curl http://localhost:8000/health

# Verify database connection
docker-compose exec db psql -U postgres -d smart_home -c "SELECT 1"

# Check Redis connectivity
docker-compose exec redis redis-cli ping
```

---

## How I Should Help

### What I'm Here For
1. **Backend development:** FastAPI endpoints, business logic, integrations.
2. **API design:** RESTful endpoints, data models, error handling.
3. **Integration work:** Google Calendar/Keep, WhatsApp, email parsing.
4. **Database:** Schema design, migrations, queries.
5. **Debugging:** Root cause analysis, pragmatic fixes.
6. **Code review:** Suggest improvements, flag security issues.

### What I Won't Assume
- **Frontend expertise is your strength.** I'll keep React/React Native simple and backend-centric.
- **Early stage means some unknowns.** I'll ask clarifying questions before building.
- **Security is always in scope.** If I spot a vulnerability, I'll flag it immediately.

### Working with Me
- **Tell me the goal, not the how.** If you say "users should see a daily reminder," I'll design the backend endpoint and suggest a simple UI.
- **Call out blockers early.** If something doesn't make sense, I'll ask.
- **Pragmatism first.** We'll use existing libraries and APIs, not reinvent wheels.

---

## Security Checklist

Before any feature ships:
- [ ] Passwords hashed (bcrypt or similar)
- [ ] HTTPS only (no HTTP)
- [ ] SQL injection prevention (ORM or parameterized queries)
- [ ] CORS configured properly (allow frontend, deny others)
- [ ] Secrets in environment variables, never in code
- [ ] API rate limiting (prevent brute force)
- [ ] Input validation on all endpoints
- [ ] Database backups automated and tested

---

## Getting Started

1. **Set up repo:** Backend (FastAPI), Frontend (React), Mobile (React Native).
2. **Database:** PostgreSQL on Ubuntu machine.
3. **Auth:** Implement password login first (users table, password hashing, JWT tokens).
4. **Core endpoints:** Activity logging, user profile, settings.
5. **Integrations:** Start with Google Calendar sync.
6. **UI:** Simple dashboard showing today's activities and reminders.
7. **Test:** Manual testing on Ubuntu machine, then iterate.

---

**Last Updated:** 2026-04-05  
**Team:** 2 engineers + PM  
**Status:** Early stage, ready to build
