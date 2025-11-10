# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "gaechwi", an AI-powered job search and recruitment preparation platform built with FastAPI. The platform provides resume feedback, mock interviews, and study guides to help job seekers prepare for employment.

**Tech Stack:** FastAPI + PostgreSQL + SQLAlchemy + Redis + Docker + Nginx + AWS S3

**Team:** 3 frontend developers (React/TypeScript), 2 backend developers (Python/FastAPI)

## Development Commands

### Local Development

```bash
# Set environment (defaults to development if not set)
export ENV=development

# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Database migrations
alembic upgrade head                           # Apply all migrations
alembic revision --autogenerate -m "message"   # Create new migration
alembic downgrade -1                           # Rollback one version

# Seed code lookup table
python seed_data/seed_code.py
```

### Docker Development

```bash
# Development environment (uses .env file)
docker-compose -f docker-compose.dev.yml up --build

# Production environment (uses .env.production file)
docker-compose up --build

# Stop containers
docker-compose down

# View backend logs
docker-compose logs -f backend
```

### Key Ports
- Backend API: 8000 (via Nginx on 80/443 in production)
- PostgreSQL: 5432
- Redis: 6379
- Nginx: 80 (HTTP), 443 (HTTPS)

## Architecture

### Layered Architecture

1. **Router Layer** (`app/routers/`): API endpoints and request handling
2. **Business Logic Layer** (`login_logic.py`, etc.): Core application logic
3. **Data Access Layer** (`models.py`, `database.py`): Database interaction
4. **Schema Layer** (`user_schema.py`, `schemas.py`): Pydantic validation
5. **Utility Layer** (`security.py`, `storage_util.py`): Cross-cutting concerns

### Dual Database Engine Pattern

The application uses **both async and sync database engines** simultaneously:

- **Async Engine** (`async_engine`, `AsyncSession`): Used by FastAPI endpoints for non-blocking I/O
- **Sync Engine** (`sync_engine`, `Session`): Used by Alembic migrations

Both engines connect to the same database. The async URL is automatically converted from the sync URL in `database.py` by replacing `postgresql://` with `postgresql+asyncpg://`.

**Important:** When writing database queries in routers/logic, always use `AsyncSession`. Only use `Session` in Alembic migration scripts.

### Configuration System

Environment-based configuration with dynamic loading:

- `app/config/settings.py`: Loads config based on `ENV` environment variable (`development` or `production`)
- `app/config/base.py`: Shared configuration (JWT settings, AWS region, OAuth URLs, image limits)
- `app/config/development.py`: Debug mode ON, smaller DB pools (5/5), includes ERD/architecture links in API docs
- `app/config/production.py`: Debug mode OFF, larger DB pools (20/30), cleaner API docs

**Access configuration:** `from app.config.settings import settings`

### Database Schema

17 tables organized into logical groups:

**User Management:**
- `users`, `userblacklists` (blocks/blocked/updater relationships), `useractivitylogs`

**Core Features:**
- `jobpostings`: Job listings
- `resumes`: User resumes with related tables (`projects`, `activities`, `experiences`, `technologystacks`, `educations`, `qualifications`)
- `resumefeedbacks` + `feedbackcontents`: AI resume analysis
- `interviews` + `conversations` + `interviewfeedbacks`: Mock interview sessions
- `studyguides` + `studyitems` + `studykeywords`: Study material generation

**Supporting Tables:**
- `files`: S3 file metadata
- `codes`: Lookup table for enumerated values (gender, user_type, etc.)

**ERD:** https://www.erdcloud.com/d/KNgfev2afc4PpbBiW

### Authentication Flow

**Google OAuth 2.0** implementation:

1. Frontend initiates OAuth via Google
2. Backend receives `code` from Google at `/auth/google/callback`
3. Backend exchanges code for Google access token
4. Backend fetches user info from Google
5. Backend checks if user exists in database
6. **New user:** Returns `{"new_user": true, "user_info": {...}, "temp_token": "..."}` for frontend to complete registration
7. **Existing user:** Returns `{"access_token": "...", "user_info": {...}}` for immediate login

**JWT Token Generation:** See `security.py` - tokens include user_id, email, name with configurable expiration.

## Important Patterns and Conventions

### Code Lookup Pattern

The `codes` table stores enumerated values. Example usage:

```python
# Joining with codes table to get human-readable values
user_query = (
    select(User, Code.code_name.label("gender_name"), Code2.code_name.label("user_type_name"))
    .outerjoin(Code, and_(User.gender == Code.code_key, Code.group_id == "GENDER"))
    .outerjoin(Code2, and_(User.user_type == Code2.code_key, Code2.group_id == "USER_TYPE"))
)
```

Seed codes from `seed_data/codes.csv` before development.

### Multi-Foreign-Key Relationships

Some models have multiple foreign keys to the same table. Example from `UserBlacklist`:

```python
class UserBlacklist(Base):
    blocker_user_id = Column(String(22), ForeignKey("users.user_id"))
    blocked_user_id = Column(String(22), ForeignKey("users.user_id"))
    updated_by = Column(String(22), ForeignKey("users.user_id"))

    # Three separate relationships to User model
    blocker = relationship("User", foreign_keys=[blocker_user_id])
    blocked_user = relationship("User", foreign_keys=[blocked_user_id])
    updater = relationship("User", foreign_keys=[updated_by])
```

Always specify `foreign_keys` parameter when multiple FKs reference the same table.

### Image Validation

Use `storage_util.py` to validate uploaded images:

```python
from app.storage_util import validate_image_file

# Validates actual image format matches file extension
# Raises ValueError if validation fails
await validate_image_file(file)
```

This uses PIL to verify the image is genuinely the claimed format, preventing malicious uploads.

### Unique ID Generation

User IDs and other primary keys use 22-character URL-safe tokens:

```python
import secrets
user_id = secrets.token_urlsafe(16)  # Generates 22-character string
```

### Cascade Delete Rules

Models use comprehensive cascade relationships. Example:

```python
resume_feedbacks = relationship("ResumeFeedback", back_populates="resume", cascade="all, delete-orphan")
```

When deleting a parent entity, related children are automatically deleted. Review cascade rules in `models.py` before making schema changes.

### Environment Variables

Copy `.env.example` to `.env` (development) or `.env.production` (production) and configure:

- Database credentials: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
- Redis: `REDIS_HOST`, `REDIS_PORT`
- JWT: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- AWS S3/Lightsail: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`, `AWS_REGION`
- Google OAuth: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- CORS: `FRONTEND_DOMAIN`

## Current Implementation Status

**Completed:**
- Google OAuth authentication and JWT token generation
- User registration and login (`app/routers/auth.py`, `app/login_logic.py`)
- Full database schema with 17 tables
- Docker containerization with SSL/TLS auto-renewal
- Database migrations (4 versions in `alembic/versions/`)

**Pending (Empty Files):**
- AI integration (`app/ai.py`)
- Redis session management (`app/redis_client.py`)
- Task scheduling (`app/scheduler.py`)
- Most router endpoints (`interview.py`, `job_postings.py`, `resumes.py`, `study_guide.py`, `users.py`)

When implementing these features, follow the existing patterns in `auth.py` and `login_logic.py`.

## API Documentation

- **Swagger UI:** http://localhost:8000/docs (development only)
- **ReDoc:** http://localhost:8000/redoc (development only)

In production, API docs are disabled for security. To enable, set `DEBUG_MODE=True` in production config (not recommended).

## Deployment Notes

The application uses Nginx as a reverse proxy with SSL/TLS certificates from Let's Encrypt:

- **Certbot** runs automatic certificate renewal every 12 hours
- **Nginx** reloads configuration every 6 hours to pick up renewed certificates
- **HSTS** and security headers are configured in `nginx_config/nginx.conf`
- **HTTP to HTTPS redirect** is automatic

Domain: `gaechwi.duckdns.org` (configured via DuckDNS)

## Database Migrations Best Practices

1. Always review autogenerated migrations before applying
2. Test migrations on development database first
3. Use descriptive migration messages: `alembic revision --autogenerate -m "add memo field to users"`
4. Never edit applied migrations - create a new one to fix issues
5. Coordinate with team before running migrations on shared databases

## Additional Resources

- **Architecture Diagram:** See README.md for Google Drive link
- **ERD:** https://www.erdcloud.com/d/KNgfev2afc4PpbBiW
