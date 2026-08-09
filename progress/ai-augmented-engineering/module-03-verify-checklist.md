# Module 03 VERIFY: Convention Matching Checklist

**Date:** 2026-08-08  
**Purpose:** Verify that context packages produce output matching existing codebase conventions

---

## Overview

After running 3 tasks with context packages, check CONSISTENCY not CORRECTNESS. The question: does the output look like it belongs in this codebase?

The convention checklist ensures that even if the AI makes a logic error, at least it makes that error in a way that's consistent with the project's patterns. Consistency catches problems faster than scattered conventions.

---

## Convention Checklist Template

For each task output, verify:

### 1. Naming Conventions

**Check: Variable Names**
- Existing pattern in codebase: `snake_case` (e.g., `created_at`, `db_session`, `link_id`)
- What to verify:
  - ✅ Agent used `team_id` (consistent)
  - ❌ Agent used `teamId` (inconsistent — camelCase when project uses snake_case)

**Check: Function Names**
- Existing pattern: `{verb}_{resource}` (e.g., `create_link`, `list_links`, `get_link_by_id`)
- What to verify:
  - ✅ Agent wrote `create_team()`, `add_team_member()` (consistent)
  - ❌ Agent wrote `createTeam()` (inconsistent — camelCase)
  - ❌ Agent wrote `teamCreate()` (inconsistent — wrong ordering)

**Check: Class Names**
- Existing pattern: `PascalCase` (e.g., `Link`, `LinkCreate`, `LinkListResponse`)
- What to verify:
  - ✅ Agent wrote `Team`, `TeamMember`, `TeamCreateResponse` (consistent)
  - ❌ Agent wrote `team`, `team_member` (inconsistent — lowercase)

**Check: File Names**
- Existing pattern: `snake_case.py` for modules (e.g., `links_service.py`, `request_logging.py`)
- What to verify:
  - ✅ Agent created `teams_service.py` (consistent)
  - ❌ Agent created `TeamsService.py` or `teams-service.py` (inconsistent)

**Check: Table Names**
- Existing pattern: `snake_case`, plural (e.g., `links`, `click_events`)
- What to verify:
  - ✅ Agent created tables `teams`, `team_members` (consistent)
  - ❌ Agent created table `Team` or `team_member` (inconsistent)

**Check: Column Names**
- Existing pattern: `snake_case` (e.g., `created_at`, `long_url`, `expires_at`)
- What to verify:
  - ✅ Agent wrote `created_at`, `updated_at`, `team_id` (consistent)
  - ❌ Agent wrote `createdAt`, `TeamId`, `creation_date` (inconsistent)

---

### 2. Error Handling

**Check: Error Response Format**
- Existing pattern in links_service.py:
  ```python
  raise HTTPException(status_code=404, detail="Link not found")
  ```
- What to verify:
  - ✅ Agent wrote `HTTPException(status_code=404, detail="Team not found")` (consistent)
  - ❌ Agent wrote `raise Exception("Team not found")` (inconsistent — wrong exception type)
  - ❌ Agent wrote `return {"error": "Team not found"}` (inconsistent — returning instead of raising)

**Check: HTTP Status Codes**
- Existing patterns:
  - 201 for POST that creates resource (Link creation uses 201)
  - 404 for not found
  - 400 for validation errors
  - 500 for internal errors
- What to verify:
  - ✅ Agent uses 201 for POST create_team
  - ✅ Agent uses 404 for "team not found"
  - ✅ Agent uses 400 for "invalid role"
  - ❌ Agent uses 403 for "team not found" (wrong status code)

**Check: Error Utility Usage**
- Existing pattern: Use `HTTPException` from FastAPI, not custom error classes
- What to verify:
  - ✅ Agent imported and used `from fastapi import HTTPException`
  - ❌ Agent created custom class `TeamException` (inconsistent)

---

### 3. Imports and Dependencies

**Check: Existing Library Reuse**
- Existing pattern: Use only what's in `api/requirements.txt`
- What to verify:
  - ✅ Agent imported only existing libraries (fastapi, sqlalchemy, pydantic)
  - ❌ Agent added `pip install marshmallow` for serialization (redundant — can use Pydantic)
  - ❌ Agent used `import simplejson` (should use standard json)

**Check: Shared Utility Import**
- Existing pattern: Functions are defined in services and imported into routes
- What to verify:
  - ✅ Agent imported: `from app.services.teams_service import create_team`
  - ❌ Agent wrote the same logic inline in the route
  - ❌ Agent created duplicate validation function when `normalize_and_validate_url()` already exists

**Check: Import Organization**
- Existing pattern: stdlib → third-party → local imports (in app/routers/links.py)
- What to verify:
  - ✅ Agent's imports organized: datetime → fastapi → sqlalchemy → app.db
  - ❌ Agent's imports mixed: app imports at top, then datetime at bottom

---

### 4. File Organization

**Check: File Placement**
- Existing pattern:
  - Models go in `app/models.py` (all in one file)
  - Schemas go in `app/schemas/{resource}.py` (per-resource files)
  - Services go in `app/services/{resource}_service.py`
  - Routes go in `app/routers/{resource}.py`
- What to verify:
  - ✅ Agent created `app/services/teams_service.py`
  - ✅ Agent modified `app/models.py` to add Team, TeamMember classes
  - ✅ Agent would create `app/schemas/team.py` for Team schemas
  - ❌ Agent created `app/TeamsService.py` (wrong directory, wrong naming)

**Check: Migration File Placement**
- Existing pattern: `api/alembic/versions/{timestamp}_{description}.py`
- What to verify:
  - ✅ Agent creates file in `api/alembic/versions/` directory
  - ✅ Agent names it like `3_create_teams.py` or with timestamp
  - ❌ Agent puts migration in `api/migrations/` (wrong directory)

---

### 5. ORM Model Pattern

**Check: Inheritance**
- Existing pattern: All models inherit from `app.db.Base`
- What to verify:
  - ✅ Agent wrote `class Team(Base):`
  - ❌ Agent wrote `class Team(SQLModel):` (wrong base class)

**Check: Type Hints**
- Existing pattern: SQLAlchemy 2.0 modern style with `Mapped` type hints
  ```python
  id: Mapped[int] = mapped_column(primary_key=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  ```
- What to verify:
  - ✅ Agent used `Mapped[int]`, `Mapped[str]`, `Mapped[datetime]`
  - ❌ Agent used old-style: `id = Column(Integer, primary_key=True)` (outdated pattern)

**Check: Relationship Definition**
- Existing pattern: Uses `relationship()` with `back_populates`
  ```python
  click_events: Mapped[list["ClickEvent"]] = relationship(
      back_populates="link", cascade="all, delete-orphan"
  )
  ```
- What to verify:
  - ✅ Agent defined: `team_members: Mapped[list["TeamMember"]] = relationship(...)`
  - ❌ Agent tried to use ForeignKey in model (that's for columns, not relationships)

**Check: Timestamps**
- Existing pattern:
  ```python
  created_at: Mapped[datetime] = mapped_column(
      DateTime(timezone=True), server_default=func.now()
  )
  ```
- What to verify:
  - ✅ Agent used `DateTime(timezone=True)` and `server_default=func.now()`
  - ❌ Agent used `DateTime()` without timezone awareness
  - ❌ Agent used Python `datetime.now()` instead of database `func.now()`

---

### 6. Validation Pattern

**Check: Schema Validator Usage**
- Existing pattern: Pydantic models with `@field_validator` decorators
- What to verify:
  - ✅ Agent defined validators in schema, not route
  - ❌ Agent put validation logic in the route handler

**Check: Validation Function Reuse**
- Existing pattern: Shared validation functions like `normalize_and_validate_url()`
- What to verify:
  - ✅ Agent reuses `can_perform()` from Task 1 to validate roles
  - ❌ Agent writes inline role validation

---

### 7. Service Layer Pattern

**Check: Service Function Signature**
- Existing pattern: `service_function(db_session: Session, ...) -> ReturnType:`
  ```python
  def create_link(db_session: Session, payload: LinkCreate) -> Link:
  ```
- What to verify:
  - ✅ Agent wrote `def create_team(db_session: Session, user_id: str, team_name: str) -> Team:`
  - ❌ Agent wrote `def create_team(team_name: str) -> Team:` (missing db_session)

**Check: Error Handling in Service**
- Existing pattern: Service raises HTTPException
  ```python
  if link is None:
      raise HTTPException(status_code=404, detail="Link not found")
  ```
- What to verify:
  - ✅ Agent raises `HTTPException(status_code=404, detail="Team not found")`
  - ❌ Agent returns `None` and lets caller handle

**Check: Database Commit**
- Existing pattern: Service handles commit/refresh
  ```python
  db_session.add(link)
  db_session.commit()
  db_session.refresh(link)
  return link
  ```
- What to verify:
  - ✅ Agent commits changes before returning
  - ❌ Agent doesn't commit (caller has to)

**Check: Logging**
- Existing pattern: Use `log_event()` from logging_config
  ```python
  log_event(logging.INFO, "link created", short_code=code)
  ```
- What to verify:
  - ✅ Agent used `log_event(logging.INFO, "team created", team_id=...)`
  - ❌ Agent used `logger.info("team created")`
  - ❌ Agent used `print(f"Team created: {id}")`

---

## What Success Looks Like

**Green flags (context package working):**
- ✅ All naming is consistent (snake_case functions, PascalCase classes, snake_case columns)
- ✅ All errors use HTTPException with correct status codes
- ✅ All models use SQLAlchemy 2.0 style with Mapped type hints
- ✅ All services follow the same pattern (take db_session, return objects, raise HTTPException)
- ✅ All files are in expected directories with expected names
- ✅ All imports are organized correctly
- ✅ Logging uses log_event() consistently

**Red flags (context package incomplete):**
- ❌ Inconsistent naming (some camelCase, some snake_case)
- ❌ Error handling uses different patterns in different files
- ❌ One service uses HTTPException, another returns None
- ❌ Models use old-style SQLAlchemy in some files, new-style in others
- ❌ Logging is inconsistent (log_event vs logger vs print)

---

## What to Check For Each Task

### Task 1 Output (Role Enum)
- ✅ Enum uses PascalCase: `class Role(str, Enum):`
- ✅ Enum values use UPPERCASE: `ADMIN = "admin"`
- ✅ Function name: `can_perform()` (snake_case)
- ✅ Return type: `bool`
- ✅ No HTTPException raised (this is pure Python)

### Task 2 Output (Team Models & Migration)
- ✅ Models inherit from `app.db.Base`
- ✅ Use `Mapped[T]` type hints
- ✅ Use `DateTime(timezone=True)` with `server_default=func.now()`
- ✅ Table names: `teams`, `team_members` (snake_case, plural)
- ✅ Column names: snake_case (e.g., `team_id`, `created_at`)
- ✅ Migration has both `upgrade()` and `downgrade()`
- ✅ Migration uses alembic API, not raw SQL

### Task 3 Output (Team Service Functions)
- ✅ File name: `teams_service.py`
- ✅ Function names: `create_team()`, `add_team_member()`, `get_team()`, etc.
- ✅ All take `db_session: Session` as first parameter
- ✅ Error handling: raise `HTTPException(...)`
- ✅ Logging: use `log_event(logging.INFO, ...)`
- ✅ Imports: organized stdlib → third-party → local

---

## Next Step: If Something Does NOT Match

**Do NOT fix it yet.**

Instead, ask: "Which file was missing from my context package that would have prevented this mismatch?"

Example: If agent used `logger.info()` instead of `log_event()`:
- **Observation:** Logging pattern doesn't match
- **Root cause:** Context package didn't include `app/logging_config.py` as a reference file
- **Fix (for next time):** Add `app/logging_config.py` to files-to-read with reason "Shows log_event() pattern for consistent structured logging"

This is how context packages improve over iterations.
