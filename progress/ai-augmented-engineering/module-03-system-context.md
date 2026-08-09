# System-Level Context Document
## FastAPI URL Shortener / Team Collaboration Feature

**Last Updated:** 2026-08-08  
**Framework:** FastAPI (Python 3.11+)  
**Database:** SQLAlchemy ORM with PostgreSQL (alembic migrations)

---

## Architecture Summary

### Framework & Structure
- **Framework:** FastAPI (modern async Python web framework)
- **Package:** `api/` folder contains full application
- **Main entry:** `api/app/main.py` (FastAPI app initialization)
- **Module organization:**
  - `api/app/routers/` — Route handlers (endpoints)
  - `api/app/schemas/` — Pydantic request/response models
  - `api/app/services/` — Business logic (queries, operations)
  - `api/app/models.py` — SQLAlchemy ORM models
  - `api/app/middleware/` — Custom middleware
  - `api/app/config.py` — Configuration and environment
  - `api/app/db.py` — Database session management

### Database & ORM
- **ORM:** SQLAlchemy 2.0 (modern style with Mapped, mapped_column)
- **Base class:** `app.db.Base` (all models inherit from this)
- **Migrations:** Alembic (`api/alembic/` folder)
  - Migration format: `api/alembic/versions/<timestamp>_<description>.py`
  - Must run migrations before using new tables
- **Session management:** `get_db_session()` dependency in `app/db.py`

### Route Registration
- Routes are defined as **plain `def` functions, NOT async** (this is critical)
- Routes use FastAPI's `APIRouter` class for grouping
- Example:
  ```python
  router = APIRouter(prefix="/links", tags=["links"])
  
  @router.post("", response_model=LinkCreateResponse, status_code=status.HTTP_201_CREATED)
  def create_link_route(
      payload: LinkCreate,
      db_session: Session = Depends(get_db_session),
  ) -> LinkCreateResponse:
      # business logic here
      return response
  ```
- Routers are included in main app: `app.include_router(links.router)`

### Middleware
- **Only middleware currently in system:** `RequestLoggingMiddleware` (logs request/response with timing)
- **No auth middleware yet** (will be added for team collaboration feature)
- Middleware is added in main.py: `app.add_middleware(RequestLoggingMiddleware)`

### Error Handling
- **Global exception handlers** in main.py:
  - `RequestValidationError` → 400 with detail list
  - Generic `Exception` → 500 with environment-aware detail level
- **Per-service error pattern:** Use FastAPI's `HTTPException` with status code and detail
  - Example: `raise HTTPException(status_code=404, detail="Link not found")`
- **Error responses:**
  - Validation errors: 400 with `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`
  - Not found: 404 with `{"detail": "Link not found"}`
  - Generic errors: 500 with `{"error": "Internal Server Error"}` (or include details in dev/staging)

### Dependency Injection
- FastAPI uses `Depends()` for dependency injection
- Common dependencies:
  - `Depends(get_db_session)` — injects SQLAlchemy Session
  - Future: `Depends(get_current_user)` — will inject authenticated user

---

## Coding Conventions

### Naming Conventions
- **Functions:** `snake_case` (e.g., `create_link`, `list_links`, `get_link_by_id`)
- **Classes:** `PascalCase` (e.g., `Link`, `LinkCreate`, `RequestLoggingMiddleware`)
- **Variables:** `snake_case` (e.g., `db_session`, `link_id`, `created_at`)
- **Constants:** `UPPERCASE_SNAKE_CASE` (e.g., `CODE_LENGTH = 6`, `MAX_TAGS = 10`)
- **Route names:** `{resource}_{action}_route` (e.g., `create_link_route`, `list_links_route`)

### File Naming
- **Modules:** `snake_case.py` (e.g., `links_service.py`, `request_logging.py`)
- **Models file:** `models.py` (all ORM models in one file)
- **Schemas file:** Per-resource schema files (e.g., `schemas/link.py`)
- **Routers file:** Per-resource router files (e.g., `routers/links.py`)

### Import Style
- Imports grouped: stdlib → third-party → local
- Example from existing code:
  ```python
  import logging
  from datetime import UTC, datetime
  
  from fastapi import APIRouter, Depends, Query
  from sqlalchemy.orm import Session
  
  from app.db import get_db_session
  from app.logging_config import log_event
  from app.models import Link
  ```

### Validation Pattern
- Use Pydantic models with `field_validator` decorators
- Validators run in schema definition, not in route handler
- Example:
  ```python
  class LinkCreate(BaseModel):
      long_url: str
      
      @field_validator("long_url")
      @classmethod
      def validate_long_url(cls, value: str) -> str:
          if not value or not value.startswith(("http://", "https://")):
              raise ValueError("long_url must be a valid http/https URL")
          return value
  ```
- Custom validation functions can be reused (e.g., `normalize_and_validate_url()`)

### Database Model Pattern
- Use SQLAlchemy 2.0 modern style:
  ```python
  class Link(Base):
      __tablename__ = "links"
      
      id: Mapped[int] = mapped_column(primary_key=True)
      code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
      long_url: Mapped[str] = mapped_column(String(2048))
      created_at: Mapped[datetime] = mapped_column(
          DateTime(timezone=True), server_default=func.now()
      )
      tags: Mapped[list[str]] = mapped_column(JSON, default=list, server_default="[]")
      
      # Relationships
      click_events: Mapped[list["ClickEvent"]] = relationship(
          back_populates="link", cascade="all, delete-orphan"
      )
  ```
- **Timestamp pattern:** Use `DateTime(timezone=True)` + `server_default=func.now()`
- **Relationships:** Use `relationship()` with `back_populates` for bidirectional
- **Nullable fields:** Use `| None` in type and `nullable=True` in column definition

### Service Layer Pattern
- Business logic goes in `services/` not routes
- Route handler calls service, service returns result or raises HTTPException
- Example:
  ```python
  # In services/links_service.py
  def create_link(db_session: Session, payload: LinkCreate) -> Link:
      link = Link(code=code, long_url=payload.long_url, ...)
      db_session.add(link)
      db_session.commit()
      db_session.refresh(link)
      return link
  
  # In routers/links.py
  @router.post("", response_model=LinkCreateResponse)
  def create_link_route(payload: LinkCreate, db_session: Session = Depends(get_db_session)):
      link = create_link(db_session, payload)
      return build_link_create_response(link, short_url)
  ```

### Response Model Pattern
- Define Pydantic schema for every response
- Use `response_model=` in route decorator
- Example:
  ```python
  class LinkCreateResponse(BaseModel):
      id: int
      code: str
      short_url: str
      long_url: str
      created_at: datetime
  
  @router.post("", response_model=LinkCreateResponse, status_code=status.HTTP_201_CREATED)
  def create_link_route(...) -> LinkCreateResponse:
      ...
  ```

### Logging Pattern
- Use `app.logging_config.log_event()` for structured logging
- Example: `log_event(logging.INFO, "link created", short_code=code, url=long_url)`
- Arguments become JSON fields in the log

---

## Constraints for Team Collaboration Feature

### No New Dependencies Without Documentation
- Before adding `pip install X`, ask: does the project already have this?
- Look in `api/requirements.txt`
- If not present: state in the code comment why this dependency is needed
- Default choice: use existing libraries (FastAPI, SQLAlchemy, Pydantic)

### Must Use Existing Patterns, Not Invent New Ones
- ❌ Do NOT create a custom error handling system if HTTPException exists
- ❌ Do NOT create custom validation if Pydantic validators exist
- ✅ DO extend existing patterns (add new validators, add new middleware)

### Auth Middleware Will Be Built in Task X
- **Current state:** No auth middleware exists yet
- **Upcoming:** JWT-based auth middleware will be added (Task 5)
- **For now:** Do NOT assume `current_user` in kwargs or request state
- **When available:** Auth middleware will inject `current_user` dependency

### Database Changes Require Migrations
- New tables or columns → new migration file
- Migration format: `api/alembic/versions/<timestamp>_<description>.py`
- Migration must be idempotent (can run multiple times safely)
- Always include both `upgrade()` and `downgrade()` functions

### Response Format Consistency
- All responses use defined Pydantic schemas
- All errors use HTTPException
- Response status codes:
  - 200 for successful read (default)
  - 201 for successful create
  - 204 for successful delete
  - 400 for validation error
  - 401 for auth error (future)
  - 403 for permission error (future)
  - 404 for not found
  - 500 for server error

### Naming & Consistency Rules
- Table names: `snake_case`, plural (e.g., `links`, `click_events`, `teams`, `team_members`)
- Column names: `snake_case` (e.g., `created_at`, `long_url`, `user_id`)
- Route paths: `/resource` for collections, `/resource/{id}` for items
- No abbreviations in names (❌ `usr` → ✅ `user`, ❌ `evt` → ✅ `event`)

### Testing & Verification
- Routes are tested by calling them and checking responses
- Services are tested by calling them with mock db_session
- Validators are tested by creating schemas with invalid data and catching exceptions
- Use real database for integration tests (not mocks)

---

## Critical Assumptions for Team Collaboration Feature

### Data Model
- Teams are owned by users (one-to-many: users can own multiple teams, each team has one owner)
- Team membership is tracked in a `team_members` join table (many-to-many relationship)
- Role is stored per membership (not per team), allowing users to have different roles in different teams
- Role values: `"admin"`, `"member"`, `"viewer"` (strings stored in database)

### Auth Flow (When Implemented)
- User logs in → receives JWT token
- Token contains user_id + user role
- Auth middleware validates token → injects `current_user` dependency
- Route handler uses `current_user` to check permissions
- Permissions are enforced via decorator: `@requires_role(Role.ADMIN)`

### Immutable Contracts
- Role enum values are final: `ADMIN`, `MEMBER`, `VIEWER` (will not change)
- Team model structure is locked: `id`, `name`, `owner_id`, `created_at`, `updated_at`
- Team membership is locked: `id`, `team_id`, `user_id`, `role`, `joined_at`
- These contracts are defined in Module 02 and must not change in downstream tasks

---

## Files to Reference (Always Include These)

1. **app/main.py** — Shows FastAPI app structure, exception handlers, middleware registration
2. **app/routers/links.py** — Shows route pattern, dependency injection, response models
3. **app/schemas/link.py** — Shows validation pattern, Pydantic models
4. **app/models.py** — Shows SQLAlchemy model pattern, relationships, timestamps
5. **app/services/links_service.py** — Shows business logic pattern, error handling, queries

These files define the conventions. Reference them when writing new code.

---

## Quick Reference Checklist

When writing code for the team collaboration feature, verify:
- ✅ Routes are plain `def`, not `async def`
- ✅ All routes use `Depends(get_db_session)` for database access
- ✅ All routes have `response_model=` defined
- ✅ Validation happens in Pydantic schema, not route
- ✅ Business logic lives in services, not routes
- ✅ Errors are raised via `HTTPException`, not custom exceptions
- ✅ All models inherit from `app.db.Base`
- ✅ All timestamps use `DateTime(timezone=True)` + `server_default=func.now()`
- ✅ Database changes include migration files
- ✅ New files follow naming conventions (snake_case, descriptive names)
- ✅ Imports are organized (stdlib → third-party → local)
- ✅ No new dependencies added without justification
