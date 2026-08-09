# Per-Task Context Bundles for Module 02 Tasks

**System Context:** Always include `progress/ai-augmented-engineering/module-03-system-context.md`

---

## Task 1: Role Enum & Permission Model

**Description:** Create a Role enum and permission checking function in app/models.py

**Why This Task:** Permissions are cross-cutting (needed by Tasks 2, 3, 4+). Build this first.

### FILES TO READ (with justification):

**1. app/models.py**
- **Reason:** Shows SQLAlchemy model pattern and import style. Understanding where models live helps with adding Role enum.
- **If omitted:** Agent might create Role in a different file or use different import style.

**2. app/schemas/link.py**
- **Reason:** Shows Pydantic model and validator pattern. If we later add role validation to schemas, consistency matters.
- **If omitted:** Agent might define validators differently later.

### FILES TO MODIFY:

- `app/models.py` (append Role enum and can_perform function)

### EXPECTED OUTPUT:

- File: `app/models.py` (additions at end of file)
- Content: 
  - Role enum with 3 values: ADMIN, MEMBER, VIEWER (as strings)
  - can_perform(role: Role, action: str) -> bool function
  - Permissions: ADMIN can perform all 7 actions; MEMBER can perform add_member, send_invite; VIEWER can perform nothing
  - No database model for roles (pure Python)
  - No route decorator (scope ends here)

### CONSTRAINTS (From System Context):

- No new dependencies
- Follow existing import style
- No HTTP exceptions in this module (pure Python)
- This is NOT about route protection (that's a later task)

### INTERFACE CONTRACT (What Downstream Tasks Expect):

```python
from app.models import Role, can_perform

# Downstream will import and use:
Role.ADMIN  # returns "admin" (string)
Role.MEMBER  # returns "member"
Role.VIEWER  # returns "viewer"

can_perform(Role.ADMIN, "delete_team")  # returns True
can_perform(Role.MEMBER, "delete_team")  # returns False
```

---

## Task 2: Team ORM Model & Migration

**Description:** Create Team and TeamMember ORM models with corresponding database migration

**Why This Task:** Defines the data schema that all downstream tasks depend on.

### FILES TO READ (with justification):

**1. app/models.py (current)**
- **Reason:** Shows SQLAlchemy 2.0 model pattern (Mapped, mapped_column, relationships). Team model must follow the same style.
- **If omitted:** Agent might use older SQLAlchemy style or import patterns inconsistently.

**2. alembic/versions/fce59a06c84a_init.py**
- **Reason:** Shows migration file format and pattern (upgrade/downgrade). New migration must follow the same structure.
- **If omitted:** Agent might write migrations in wrong format or use raw SQL instead of alembic API.

**3. app/db.py**
- **Reason:** Shows Base class that all models inherit from. Team must inherit from Base.
- **If omitted:** Agent might define models without proper inheritance.

### FILES TO MODIFY:

- `app/models.py` (add Team class, add TeamMember class, add imports if needed)
- `api/alembic/versions/` (create new migration file)

### EXPECTED OUTPUT:

- File: `app/models.py` (additions, same file as Task 1)
  - Team model: id (int PK), name (str), owner_id (str FK to... wait, user table doesn't exist yet, so owner_id is just str for now), created_at, updated_at
  - TeamMember model: id (int PK), team_id (int FK), user_id (str), role (str CHECK constraint for 'admin'/'member'/'viewer'), joined_at
  - Relationships: Team has many TeamMembers (relationship + cascade delete)

- File: `api/alembic/versions/<timestamp>_create_teams_and_team_members.py`
  - Create teams table with columns: id, name, owner_id, created_at, updated_at
  - Create team_members table with columns: id, team_id, user_id, role, joined_at
  - Add foreign key from team_members.team_id to teams.id
  - Add constraint on role column to only allow ('admin', 'member', 'viewer')
  - Both functions (upgrade/downgrade)

### CONSTRAINTS (From System Context):

- Must inherit from `app.db.Base`
- Must follow SQLAlchemy 2.0 style (Mapped, mapped_column)
- Timestamps: use `DateTime(timezone=True)` + `server_default=func.now()`
- Migrations: must include both upgrade() and downgrade()
- Role column: must only accept 'admin', 'member', 'viewer' (enforce with CHECK constraint)
- No new dependencies
- No HTTP logic in models (models are data, not business logic)

### INTERFACE CONTRACT (What Downstream Tasks Expect):

```python
from app.models import Team, TeamMember
from sqlalchemy.orm import Session

# Downstream will import and use:
team = Team(name="My Team", owner_id="user_123")
# Team has: id, name, owner_id, created_at, updated_at

member = TeamMember(team_id=1, user_id="user_456", role="member")
# TeamMember has: id, team_id, user_id, role, joined_at

# Relationships work:
team.team_members  # returns list[TeamMember]
member.team  # returns Team

# Queries work:
db_session.query(Team).filter(Team.owner_id == "user_123").all()
db_session.query(TeamMember).filter(TeamMember.team_id == 1).all()
```

**CRITICAL: These tables must exist in the database (migration must run) before any downstream tasks query them.**

---

## Task 3: Team Service Layer Functions

**Description:** Implement team CRUD operations in app/services/teams_service.py

**Why This Task:** Services encapsulate business logic. Routes will call these functions.

### FILES TO READ (with justification):

**1. app/services/links_service.py**
- **Reason:** Shows service pattern (how functions are structured, error handling, query patterns). Team service must follow the same pattern.
- **If omitted:** Agent might write services differently (e.g., class-based instead of functional).

**2. app/models.py (current, after Task 2)**
- **Reason:** Shows Team and TeamMember models that will be queried. Service functions need to know the model structure.
- **If omitted:** Agent might query non-existent columns or use wrong field names.

**3. app/logging_config.py**
- **Reason:** Shows log_event pattern. Team operations should log similarly to link operations.
- **If omitted:** Agent might log inconsistently or use print/logging.warning instead.

**4. app/models.py (Role enum from Task 1)**
- **Reason:** Services will validate permissions using can_perform(). Need access to Role and can_perform.
- **If omitted:** Agent might re-implement permission checks instead of reusing Task 1's function.

### FILES TO MODIFY:

- `app/services/teams_service.py` (NEW file)

### EXPECTED OUTPUT:

- File: `app/services/teams_service.py` (new)
  - Function: `create_team(db_session: Session, user_id: str, team_name: str) -> Team`
    - Creates team with given owner
    - Automatically adds owner to team_members with role "admin"
    - Returns Team object
    - Logs: "team created"
  
  - Function: `add_team_member(db_session: Session, team_id: int, user_id: str, role: str) -> TeamMember`
    - Adds user to team with given role
    - Validates role using can_perform (or direct check: role in ['admin', 'member', 'viewer'])
    - Returns TeamMember object
    - Logs: "team member added"
    - Raises: HTTPException(404) if team not found
    - Raises: HTTPException(400) if user already in team
  
  - Function: `remove_team_member(db_session: Session, team_id: int, user_id: str) -> None`
    - Removes user from team
    - Prevents removing the last admin (raises HTTPException 400)
    - Logs: "team member removed"
    - Raises: HTTPException(404) if team or member not found
  
  - Function: `get_team(db_session: Session, team_id: int) -> Team`
    - Returns team or raises HTTPException(404)
  
  - Function: `list_team_members(db_session: Session, team_id: int) -> list[TeamMember]`
    - Returns all members of team
    - Raises: HTTPException(404) if team not found

### CONSTRAINTS (From System Context):

- Must follow service pattern from links_service.py
- Error handling: use HTTPException, not custom exceptions
- All queries go through db_session parameter
- Use log_event for all significant operations
- Validate input (role must be one of ADMIN/MEMBER/VIEWER)
- Prevent impossible states (can't remove last admin)
- No HTTP routing logic (that's routes' job)

### INTERFACE CONTRACT (What Downstream Tasks Expect):

```python
from app.services.teams_service import create_team, add_team_member, remove_team_member, get_team, list_team_members
from sqlalchemy.orm import Session

# Downstream routes will call:
team = create_team(db_session, "user_123", "Engineering")
member = add_team_member(db_session, team.id, "user_456", "member")
remove_team_member(db_session, team.id, "user_456")
team = get_team(db_session, team_id)
members = list_team_members(db_session, team_id)

# All functions raise HTTPException on error, so routes don't need to handle exceptions
```

---

## Summary: Context Packages

Each task receives:
1. **System Context Document** (always included) — describes framework, conventions, constraints
2. **Files to Read** — specific existing files that show patterns to follow
3. **Files to Modify** — which files the agent needs to edit or create
4. **Expected Output** — exact deliverables with file names and content structure
5. **Interface Contract** — what downstream tasks depend on (imports, function signatures, data structures)

The combination ensures:
- ✅ Consistency: all code follows the same patterns
- ✅ Precision: agent only sees files that matter for this task
- ✅ Correctness: interface contracts lock down integration points
- ✅ Safety: constraints prevent common mistakes

---

## Next Step

Run all 3 tasks with their context packages:
1. Task 1: `system-context + task1-context`
2. Task 2: `system-context + task2-context` (after Task 1 completes)
3. Task 3: `system-context + task3-context` (after Task 2 completes, needs output from Tasks 1 & 2)

Save all outputs without reviewing or modifying them. Then compare in the VERIFY step to see how well context engineering worked.
