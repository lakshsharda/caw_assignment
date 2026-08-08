# Module 02 BUILD: Team Collaboration Task Tree

**Planning Strategy:** Top-Down with cross-cutting concerns first  
**Task Granularity:** Medium (8-12 tasks, 50-150 lines each)  
**Date:** 2026-08-08

---

## Cross-Cutting Concerns (Planned Upfront)

These patterns apply to all tasks and must be established before Task 1:

### 1. Authentication & Authorization Pattern
- All team endpoints require JWT authentication (not yet implemented)
- New `get_current_user()` dependency must be added to extract user from request
- Authorization: role-based (admin > member > viewer)
- Scope: users can only access teams they're members of

### 2. Activity Logging Pattern
- Every significant action logs to activity_feed table
- Pattern: `log_activity(team_id, actor_id, action, resource_type, metadata)`
- Applied to: team creation, invitations, role changes, member removal

### 3. Audit Logging Pattern
- Sensitive actions log to audit_log table (immutable)
- Pattern: `log_audit(team_id, actor_id, action, resource, old_value, new_value, timestamp)`
- Applied to: permission changes, user removal, invitation revocation

### 4. Error Handling Pattern
- Follow existing HTTPException pattern from links_service.py
- 404 for not found: `HTTPException(status_code=404, detail="Team not found")`
- 403 for permission denied: `HTTPException(status_code=403, detail="Insufficient permissions")`
- 400 for validation: `HTTPException(status_code=400, detail="Team name is required")`

### 5. ORM Pattern
- Follow Link/ClickEvent pattern: Mapped types, relationships, cascade delete
- All timestamps: DateTime(timezone=True), server_default=func.now()
- All IDs: mapped_column(primary_key=True)
- Foreign keys: ondelete="CASCADE" where orphaning is acceptable

---

## Task Tree (9 Tasks, Top-Down Dependencies)

### Task 1: Create Role Enum & Permission Model
**Foundational: Required before any other task**

**Task Name:** Define roles and permission matrix

**Input Context Needed:**
- Read: app/config.py (environment-aware patterns)
- Reference: How HTTPException is used in links_service.py

**Expected Output:**
- New file: app/models.py (append to existing) with Role enum and Permission model
- Enum: Role with values: ADMIN, MEMBER, VIEWER (in-memory, not DB)
- Function: `def can_perform(role: Role, action: str) -> bool` for permission checks
- Function: `def requires_role(min_role: Role)` decorator for route protection

**Acceptance Criteria:**
- ✅ Can instantiate Role.ADMIN, Role.MEMBER, Role.VIEWER
- ✅ `can_perform(Role.ADMIN, "delete_team")` returns True
- ✅ `can_perform(Role.VIEWER, "delete_team")` returns False
- ✅ `can_perform(Role.MEMBER, "add_member")` returns True

**Dependencies:** None (foundational)

**Risk:** Low (no DB changes, logic only)

---

### Task 2: Create Team ORM Model & Migration
**Foundational: Establishes data model for all other team tasks**

**Task Name:** Create teams table and Team ORM model

**Input Context Needed:**
- Read: app/models.py (see Link/ClickEvent pattern)
- Read: alembic/versions/ (migration pattern)
- Reference: app/db.py (database setup)

**Expected Output:**
- Modified: app/models.py — append Team class
- New migration: alembic/versions/XXX_create_teams.py
- Team model fields:
  - id: Mapped[int], primary_key
  - name: Mapped[str], String(255), unique=False, index=True
  - description: Mapped[str | None], String(1000), nullable=True
  - owner_id: Mapped[str], String(255), index=True (NOT FK, follows created_by pattern)
  - created_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now()
  - updated_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  - members: relationship to TeamMember
  - invitations: relationship to Invitation
  - activity_feed: relationship to ActivityFeed
  - audit_logs: relationship to AuditLog

**Acceptance Criteria:**
- ✅ Can run `alembic upgrade head` without errors
- ✅ Table `teams` exists with correct columns
- ✅ Can create Team object: `Team(name="Acme", owner_id="user123")`
- ✅ Team object has relationships (members, invitations, activity_feed, audit_logs) [not yet populated]

**Dependencies:** None (but Task 1 established Role enum)

**Risk:** Low-Medium (new table, but straightforward pattern)

---

### Task 3: Create TeamMember ORM Model & Migration
**Foundational: User-team relationship with roles**

**Task Name:** Create team_members table and TeamMember ORM model

**Input Context Needed:**
- Read: app/models.py, specifically Team model just created
- Read: existing Link model for relationship pattern
- Reference: Role enum from Task 1

**Expected Output:**
- Modified: app/models.py — append TeamMember class
- New migration: alembic/versions/XXX_create_team_members.py
- TeamMember model fields:
  - id: Mapped[int], primary_key
  - team_id: Mapped[int], ForeignKey("teams.id", ondelete="CASCADE"), index=True
  - user_id: Mapped[str], String(255), index=True (NOT FK, follows pattern)
  - role: Mapped[str], String(50), default="member" (store as string: "admin", "member", "viewer")
  - joined_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now()
  - team: relationship to Team, back_populates="members"

**Acceptance Criteria:**
- ✅ Can run migration, table team_members exists
- ✅ Unique constraint on (team_id, user_id): user cannot have multiple roles in same team
- ✅ Can create: `TeamMember(team_id=1, user_id="user123", role="admin")`
- ✅ TeamMember.team accesses parent Team object
- ✅ Team.members accesses list of TeamMember objects

**Dependencies:** Task 2 (Team model must exist first)

**Risk:** Low-Medium (straightforward relationship, but sets up permission model)

---

### Task 4: Create GET /teams and POST /teams Endpoints
**User-facing: Basic team CRUD**

**Task Name:** Create team listing and creation endpoints

**Input Context Needed:**
- Read: app/routers/links.py (route pattern, status codes, error handling)
- Read: app/schemas/link.py (schema pattern for request/response)
- Read: Team, TeamMember models
- Reference: Role enum and can_perform() permission logic

**Expected Output:**
- New file: app/routers/teams.py with router
- New file: app/schemas/teams.py with TeamCreate, TeamResponse schemas
- Routes:
  - GET /teams: List teams for current user (filter by TeamMember.user_id), return paginated TeamResponse
  - POST /teams: Create new team (user becomes owner+admin), return TeamResponse
- Schemas:
  - TeamCreate: name (str, required, 1-255 chars)
  - TeamResponse: id, name, description, owner_id, created_at, member_count

**Acceptance Criteria:**
- ✅ POST /teams with valid name returns 201 with team object
- ✅ POST /teams without name returns 400
- ✅ POST /teams creator becomes owner_id and added to TeamMember with role=admin
- ✅ GET /teams returns only teams where current user is a member
- ✅ Both endpoints log action via log_activity(team_id, actor_id, action, ...)
- ✅ Unprotected requests (no Bearer token) return 401

**Dependencies:** Task 2, Task 3 (models), Task 1 (permission logic)

**Risk:** Medium (first real endpoint, auth integration)

---

### Task 5: Create Activity Feed ORM Model & Migration
**Foundational: Audit trail for all team actions**

**Task Name:** Create activity_feed table and ActivityFeed ORM model

**Input Context Needed:**
- Read: Team model
- Reference: ClickEvent pattern (detailed event tracking)

**Expected Output:**
- Modified: app/models.py — append ActivityFeed class
- New migration: alembic/versions/XXX_create_activity_feed.py
- ActivityFeed model fields:
  - id: Mapped[int], primary_key
  - team_id: Mapped[int], ForeignKey("teams.id", ondelete="CASCADE"), index=True
  - actor_id: Mapped[str], String(255) (NOT FK, follows pattern)
  - action: Mapped[str], String(50) (enum: "team_created", "member_added", "member_removed", "role_changed", "invitation_sent", "invitation_accepted")
  - resource_type: Mapped[str], String(50) (e.g., "team", "member", "invitation")
  - resource_id: Mapped[int | None], nullable=True
  - metadata: Mapped[dict], JSON, default=dict (store action-specific data)
  - created_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now()
  - team: relationship to Team, back_populates="activity_feed"

**Acceptance Criteria:**
- ✅ Can run migration, table activity_feed exists
- ✅ Can create: `ActivityFeed(team_id=1, actor_id="user123", action="member_added", resource_type="member", metadata={"new_member_id": "user456"})`
- ✅ Index on (team_id, created_at) for efficient range queries

**Dependencies:** Task 2 (Team model)

**Risk:** Low (straightforward event model)

---

### Task 6: Create Invitation ORM Model & Migration
**Foundational: Tracks pending team invites**

**Task Name:** Create invitations table and Invitation ORM model

**Input Context Needed:**
- Read: Team model
- Reference: Expiry pattern (Link model has expires_at)

**Expected Output:**
- Modified: app/models.py — append Invitation class
- New migration: alembic/versions/XXX_create_invitations.py
- Invitation model fields:
  - id: Mapped[int], primary_key
  - team_id: Mapped[int], ForeignKey("teams.id", ondelete="CASCADE"), index=True
  - email: Mapped[str], String(255), index=True (invitee email)
  - token: Mapped[str], String(255), unique=True (secure random token)
  - role: Mapped[str], String(50), default="member"
  - status: Mapped[str], String(50), default="pending" (enum: pending, accepted, declined, revoked)
  - created_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now()
  - expires_at: Mapped[datetime], DateTime(timezone=True) (7 days from created_at)
  - accepted_at: Mapped[datetime | None], nullable=True
  - team: relationship to Team, back_populates="invitations"

**Acceptance Criteria:**
- ✅ Can run migration, table invitations exists
- ✅ Unique token for each invitation
- ✅ expires_at calculated 7 days from created_at
- ✅ Status transitions: pending → accepted or pending → revoked

**Dependencies:** Task 2 (Team model)

**Risk:** Low (straightforward model)

---

### Task 7: Create Audit Log ORM Model & Migration
**Foundational: Compliance audit trail (immutable)**

**Task Name:** Create audit_logs table and AuditLog ORM model

**Input Context Needed:**
- Read: Team model
- Reference: ActivityFeed model (similar but immutable)

**Expected Output:**
- Modified: app/models.py — append AuditLog class
- New migration: alembic/versions/XXX_create_audit_logs.py
- AuditLog model fields:
  - id: Mapped[int], primary_key
  - team_id: Mapped[int], ForeignKey("teams.id", ondelete="CASCADE"), index=True
  - actor_id: Mapped[str], String(255)
  - action: Mapped[str], String(50) (sensitive actions: "member_removed", "role_changed", "invitation_revoked")
  - resource: Mapped[str], String(255) (what was changed: "member", "role", "invitation")
  - old_value: Mapped[str | None], String(1000), nullable=True
  - new_value: Mapped[str | None], String(1000), nullable=True
  - created_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now()
  - team: relationship to Team, back_populates="audit_logs"

**Acceptance Criteria:**
- ✅ Can run migration, table audit_logs exists
- ✅ No UPDATE/DELETE capability (append-only)
- ✅ Can create: `AuditLog(team_id=1, actor_id="user123", action="member_removed", resource="member", old_value="user456", new_value=None)`

**Dependencies:** Task 2 (Team model)

**Risk:** Low (straightforward immutable log)

---

### Task 8: Create POST /teams/:id/members Endpoint (Add Member)
**User-facing: Add existing user to team**

**Task Name:** Create endpoint to add member to team

**Input Context Needed:**
- Read: Task 4 route pattern
- Read: TeamMember, Team models
- Reference: Role enum, can_perform() permission logic
- Reference: log_activity() pattern from Task 4

**Expected Output:**
- Modified: app/routers/teams.py — add POST /teams/{team_id}/members route
- Schema: AddMemberRequest (user_id: str, role: str)
- Route should:
  1. Verify current user is ADMIN on team
  2. Verify user not already member
  3. Create TeamMember(team_id, user_id, role)
  4. Log activity: "member_added"
  5. Return 201 with member object

**Acceptance Criteria:**
- ✅ POST /teams/1/members with valid user_id and role="member" returns 201
- ✅ Same endpoint called twice returns 400 (member already in team)
- ✅ Non-admin calling endpoint returns 403
- ✅ Added member appears in GET /teams/{id}/members list
- ✅ Activity logged for this action

**Dependencies:** Task 4 (endpoints established), Task 3 (TeamMember model), Task 1 (permissions)

**Risk:** Medium-High (first permission-check integration)

---

### Task 9: Create POST /teams/:id/invitations Endpoint (Send Invite)
**User-facing: Invite new user to team (email required)**

**Task Name:** Create endpoint to send invitation

**Input Context Needed:**
- Read: Task 4, Task 8 route patterns
- Read: Invitation model
- Reference: Role enum, can_perform()
- Reference: log_activity(), log_audit() patterns

**Expected Output:**
- Modified: app/routers/teams.py — add POST /teams/{team_id}/invitations route
- Schema: SendInvitationRequest (email: str, role: str)
- Route should:
  1. Verify current user is ADMIN on team
  2. Check email not already member
  3. Generate secure random token (secrets.token_urlsafe(32))
  4. Create Invitation(team_id, email, token, role, expires_at=now+7d)
  5. Log activity: "invitation_sent"
  6. Return 201 with invitation object (include acceptance_url with token)
  7. [Future: send email with acceptance_url]

**Acceptance Criteria:**
- ✅ POST /teams/1/invitations with valid email and role returns 201
- ✅ Invitation has unique token
- ✅ Response includes acceptance_url like /invitations/{token}/accept [not yet functional]
- ✅ Inviting same email twice returns 400
- ✅ Non-admin returns 403
- ✅ Activity logged for this action

**Dependencies:** Task 4, Task 6 (Invitation model), Task 1 (permissions)

**Risk:** Medium-High (external consideration: email sending deferred but structure must support it)

---

## Dependency Graph

```
Task 1: Role Enum [foundational]
         ↓
    ┌────┴────┐
    ↓         ↓
Task 2:    Task 1 (no further deps)
Team Model
    │
    ├─→ Task 3: TeamMember
    │   │
    │   └─→ Task 8: Add Member
    │       ↑
    │       └─→ Task 4: CRUD endpoints
    │
    ├─→ Task 5: Activity Feed
    │   └─→ Task 4 & 8: logging
    │
    ├─→ Task 6: Invitation
    │   └─→ Task 9: Send Invite
    │
    └─→ Task 7: Audit Log
        └─→ Task 9: sensitive action logging

Task 4: GET/POST /teams [endpoints, depends on Task 2, 3]
Task 8: Add Member [depends on Task 4]
Task 9: Send Invite [depends on Task 4, 6]
```

**Critical Path:** Task 1 → Task 2 → Task 4 → Task 8 (4 sequential tasks)

---

## Riskiest Tasks

### Risk Ranking (High to Low):

1. **Task 8 (Add Member) — HIGHEST RISK**
   - First permission-check integration
   - Risk: User ID validation, duplicate member handling, permission enforcement
   - Mitigation: Write specific test cases upfront, verify permission denied returns 403

2. **Task 9 (Send Invite) — HIGH RISK**
   - Complex state management (token generation, expiry, status)
   - Risk: Insecure token generation, expiry validation, email pattern not thought through
   - Mitigation: Use secrets.token_urlsafe (not predictable), verify token is unique, plan email structure upfront (defer actual sending)

3. **Task 4 (CRUD Endpoints) — MEDIUM RISK**
   - First real route integration with auth
   - Risk: Status codes, error messages, schema validation
   - Mitigation: Follow links.py pattern exactly, verify each response code

4. **Task 1-3, 5-7 (Models) — LOW RISK**
   - Straightforward ORM patterns
   - Risk: Field types, relationships
   - Mitigation: Verify migrations run without error

---

## First Three Prompts (for execution)

### Prompt 1: Create Role Enum & Permission Model

```
Create a Role enum and permission checking system in app/models.py for the TaskFlow Team Collaboration feature.

CONTEXT:
- Read the existing HTTPException pattern in app/services/links_service.py
- Study the config.py environment-aware error handling pattern

DELIVERABLE:
Create or append to app/models.py:

1. A Role enum with three values:
   - Role.ADMIN = "admin"
   - Role.MEMBER = "member"
   - Role.VIEWER = "viewer"

2. A permission matrix function:
   def can_perform(role: Role, action: str) -> bool:
       """Check if role can perform action. Actions: 'create_team', 'add_member', 'remove_member', 'delete_team', 'change_role', 'send_invite', 'revoke_invite'"""
       # ADMIN can perform all actions
       # MEMBER can: add_member, send_invite
       # VIEWER can: (none of these actions)
       # Return True/False based on role and action

3. A route protection decorator:
   from functools import wraps
   def requires_role(min_role: Role):
       """Decorator to protect routes requiring minimum role. Returns 403 if user doesn't have required role."""
       # Decorator implementation

CONSTRAINTS:
- No database changes
- No new dependencies
- Follow the same import style as app/models.py
- Return exact dict/bool, not exceptions

VERIFICATION:
- Can instantiate Role.ADMIN, Role.MEMBER, Role.VIEWER
- can_perform(Role.ADMIN, "delete_team") returns True
- can_perform(Role.VIEWER, "delete_team") returns False
```

---

### Prompt 2: Create Team ORM Model & Migration

```
Create the Team ORM model and Alembic migration for the TaskFlow Team Collaboration feature.

CONTEXT:
- Study the Link and ClickEvent relationship pattern in app/models.py for ORM structure
- Review the migration pattern in alembic/versions/fce59a06c84a_init.py
- Examine app/db.py for database setup

DELIVERABLE:
1. In app/models.py, create Team class:
   - id: Mapped[int], primary_key
   - name: Mapped[str], String(255), not null, indexed
   - description: Mapped[str | None], String(1000), nullable
   - owner_id: Mapped[str], String(255), not null, indexed (this is a user ID string, NOT a foreign key — follow the created_by pattern from Link model)
   - created_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now()
   - updated_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
   - members: relationship to TeamMember (back_populates="team", cascade="all, delete-orphan")
   - invitations: relationship to Invitation (back_populates="team", cascade="all, delete-orphan")
   - activity_feed: relationship to ActivityFeed (back_populates="team", cascade="all, delete-orphan")
   - audit_logs: relationship to AuditLog (back_populates="team", cascade="all, delete-orphan")

2. Create migration file alembic/versions/XXXXXXX_create_teams.py:
   - Create teams table with columns matching Team model
   - Add index on name and owner_id for query performance
   - Use the exact migration syntax from the existing migrations

CONSTRAINTS:
- No new Python dependencies
- Follow exact naming: table name "teams", column names as listed
- Use CASCADE delete for relationships to prevent orphaned data

VERIFICATION:
- Run: alembic upgrade head (no errors)
- Run: SELECT * FROM teams; (table exists with correct columns)
- No errors in app startup when models are loaded
```

---

### Prompt 3: Create TeamMember ORM Model & Migration

```
Create the TeamMember ORM model and Alembic migration. TeamMember represents the join table between users and teams with role enforcement.

CONTEXT:
- Read the Team model you just created (check app/models.py for the exact relationship definition)
- Study how relationships work in the Link/ClickEvent pattern
- Examine the migration format again

DELIVERABLE:
1. In app/models.py, create TeamMember class:
   - id: Mapped[int], primary_key
   - team_id: Mapped[int], ForeignKey("teams.id", ondelete="CASCADE"), indexed
   - user_id: Mapped[str], String(255), indexed (NOT a foreign key, just string ID)
   - role: Mapped[str], String(50), default="member" (values: "admin", "member", "viewer")
   - joined_at: Mapped[datetime], DateTime(timezone=True), server_default=func.now()
   - team: Mapped["Team"] = relationship("Team", back_populates="members")

2. Create migration file:
   - Create team_members table
   - Add UNIQUE constraint on (team_id, user_id): a user can only have one role per team
   - Add indices on team_id and user_id for query performance

CONSTRAINTS:
- No new dependencies
- Use CASCADE DELETE for team_id foreign key
- Role values must be string, not enum

VERIFICATION:
- Run: alembic upgrade head (no errors)
- Run: SELECT * FROM team_members; (table exists)
- Test: INSERT INTO team_members(team_id, user_id, role) VALUES(1, 'user1', 'admin'); (succeeds)
- Test: INSERT same user into same team again (fails with unique constraint)
```

---

## Summary

**9 tasks across 3 phases:**

**Phase 1: Foundations (Tasks 1-3)**
- Task 1: Role enum & permissions
- Task 2: Team model
- Task 3: TeamMember model

**Phase 2: Audit & Tracking (Tasks 5-7)**
- Task 5: Activity feed
- Task 6: Invitations
- Task 7: Audit log

**Phase 3: Endpoints (Tasks 4, 8-9)**
- Task 4: GET/POST /teams
- Task 8: Add member
- Task 9: Send invitation

**Critical Path Length:** 4 tasks (Task 1 → 2 → 4 → 8)  
**Total Estimated Lines:** 450-600 (50-75 lines per task)  
**Riskiest Tasks:** Task 8 (permissions), Task 9 (state management)
