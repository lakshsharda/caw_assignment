# Module 02 FIX: Interface Contracts

**Date:** 2026-08-08  
**Core Learning:** Decomposition is not just splitting work into pieces. It's defining interfaces between those pieces.

---

## The Root Problem

Task 1 included 3 deliverables:
1. Role enum ✅
2. can_perform() function ✅
3. requires_role() decorator ❌

Items 1 and 2 are pure data/logic. Item 3 is a route decorator that depends on:
- Auth middleware (not yet built)
- current_user injection (not yet built)
- Route pattern knowledge (sync vs async)

**The lesson:** Task 1 violated the dependency rule. It created a deliverable that depends on work that hasn't been specified yet.

---

## Step 1: Decide Where the Fix Belongs

### Question: Should Task 1 include the requires_role() decorator?

### Answer: **NO**

**Why:**
- Task 1 is about permissions model (what roles can do)
- Task 1 is NOT about how to enforce permissions in routes
- Enforcing permissions requires auth infrastructure (Task 5+) to be done first
- Decorator depends on: JWT middleware, current_user injection, route patterns
- None of these are Task 1's responsibility

**Better decomposition:**
- **Task 1:** Role enum + can_perform() — pure permissions model
- **Task 4-modified (after Task 5 — auth middleware):** Integrate permissions with routes using a decorator
- The decorator can then assume current_user exists and knows the route pattern

### Decision: Revise Task 1 scope

**Original Task 1 Prompt (buggy):**
```
Create Role enum, permission matrix function, and route protection decorator.
```

**Revised Task 1 Prompt (fixed):**
```
Create Role enum and permission checking function. Do NOT create a route decorator
(that is Task 4's responsibility after auth middleware is built). This task is 
about defining what roles can do, not enforcing it in routes yet.
```

---

## Step 2: Add Interface Contracts

Now I'll define what each task produces and what downstream tasks expect.

### Contract: Task 1 → Tasks 2, 3, 4+

#### What Task 1 Produces

**File:** `app/models.py` (new content added)

**Code exports:**
```python
from enum import Enum

class Role(str, Enum):
    """Enum of valid roles in the system."""
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

def can_perform(role: Role, action: str) -> bool:
    """
    Check if a role can perform an action.
    
    Valid actions: 'create_team', 'add_member', 'remove_member', 
    'delete_team', 'change_role', 'send_invite', 'revoke_invite'
    
    Returns: True if role can perform action, False otherwise
    """
    # Implementation details not specified (consumer only cares about input/output)
    ...
```

**Contract guarantees:**
- ✅ Role enum has exactly 3 values: ADMIN, MEMBER, VIEWER (as strings)
- ✅ can_perform(role: Role, action: str) → bool is available
- ✅ ADMIN can perform all 7 actions: create_team, add_member, remove_member, delete_team, change_role, send_invite, revoke_invite
- ✅ MEMBER can perform: add_member, send_invite
- ✅ VIEWER can perform: (nothing — returns False for all actions)
- ✅ No database changes (pure Python)
- ✅ No new dependencies added

#### What Task 2+ Expect from Task 1

**Task 2 (Team ORM model):**
- Needs to know: What role values are valid when storing team membership?
- Expects: Role.ADMIN, Role.MEMBER, Role.VIEWER to be importable from app.models
- Must ensure: team_members table has a role column that accepts only these 3 string values

**Task 4+ (Route protection decorator):**
- Needs to know: Can I import can_perform() to check permissions?
- Expects: can_perform(user_role: Role, action: str) to be available
- Must ensure: This function is used to enforce route-level access control

---

### Contract: Task 1 ↔ Task 5 (Auth Middleware) — What Task 5 MUST Provide

**Task 5 responsibility:** Build auth middleware that injects current_user.

**What Task 1 assumes about current_user (for eventual use in Task 4-modified decorator):**
- current_user must have a `.role` attribute of type Role
- current_user must be available in FastAPI dependency injection

**Critical note:** Task 1 does NOT depend on Task 5 yet. But Task 4-modified (route decorator) DOES.

**Interface for Task 4-modified to Task 5:**
```python
# Task 5 will provide this:
class User(Base):  # ORM model
    role: Role  # Must be the Role enum from Task 1

# FastAPI dependency:
def get_current_user(token: str = Depends(...)) -> User:
    """Return current user from JWT token."""
    ...
```

---

## Step 3: Revised Task Tree with Contracts

### Original (Buggy) Tasks 1-3:

```
Task 1: Role enum + can_perform() + requires_role decorator
        ❌ PROBLEM: Includes decorator that depends on Task 5

Task 2: Team ORM model (Create teams table)
        ❌ PROBLEM: Assumes team_members structure not yet defined

Task 3: Team membership management
        ❌ PROBLEM: References functions from Task 2 not yet created
```

### Revised (Fixed) Task Tree:

```
Task 1: Role enum + can_perform() function
        ✅ PRODUCES:
           - Role enum (ADMIN, MEMBER, VIEWER)
           - can_perform(role: Role, action: str) → bool
           - No dependencies on other tasks
           
        CONTRACT TO DOWNSTREAM:
        - Role enum is final (values will not change)
        - can_perform() logic is immutable (other tasks build on top of this)

Task 2: Team ORM model (teams table, team_members join table)
        ✅ PRODUCES:
           - Table: teams (id, name, owner_id, created_at, updated_at)
           - Table: team_members (id, team_id, user_id, role, joined_at)
           - role column accepts: Role.ADMIN, Role.MEMBER, Role.VIEWER
           
        DEPENDS ON: Task 1 (imports Role enum)
        
        CONTRACT TO DOWNSTREAM:
        - team_members table exists with (team_id, user_id, role, joined_at)
        - role is validated against Role enum values
        - On team creation, owner is auto-added to team_members with role=ADMIN

Task 3: Team membership CRUD (add_member, remove_member, change_role)
        DEPENDS ON: Task 1 (use can_perform to check permissions)
                    Task 2 (query team_members table)

... (Tasks 4-8 similar pattern)

Task 4-modified: Route protection decorator (created AFTER Task 5)
        DEPENDS ON: Task 1 (import Role, can_perform)
                    Task 5 (assume current_user with .role exists)
```

---

## Step 4: What Went Wrong in the Prompt Design?

### The Mistake

Prompt 1 asked for 3 things without specifying their relationships:

```
DELIVERABLE:
1. A Role enum
2. A permission matrix function
3. A route protection decorator
```

The AI had no way to know:
- Should the decorator assume sync or async routes?
- Should it assume current_user is in kwargs or injected?
- Is the decorator optional (Task 1 responsibility) or mandatory?

**The agent made reasonable choices** but chose wrong because the prompt was ambiguous.

### The Fix

**New Prompt 1 (Clarified):**

```
Create a Role enum and permission checking function for the TaskFlow Team 
Collaboration feature.

SCOPE: This task is ONLY about the permissions model (what roles can do). 
Do NOT create a route decorator (that belongs to a later task after auth 
infrastructure is built).

DELIVERABLE:

1. Role enum (app/models.py):
   - ADMIN = "admin"
   - MEMBER = "member"  
   - VIEWER = "viewer"

2. Permission matrix function (app/models.py):
   def can_perform(role: Role, action: str) -> bool:
       Actions: 'create_team', 'add_member', 'remove_member', 
                'delete_team', 'change_role', 'send_invite', 'revoke_invite'
       ADMIN: can perform all actions
       MEMBER: can perform add_member, send_invite
       VIEWER: can perform no actions
       Return True/False based on role and action.

CONSTRAINTS:
- No database changes
- No new dependencies
- Do NOT create a route decorator (Task 4 responsibility)
- Return bool from can_perform(), not exceptions

INTERFACE CONTRACT (what downstream tasks expect):
- Role enum with exactly 3 values: ADMIN, MEMBER, VIEWER
- can_perform(role: Role, action: str) → bool always returns a bool
- The function is deterministic (same inputs → same output every time)
- Role enum is final (will not change in later tasks)

VERIFICATION:
- Role.ADMIN, Role.MEMBER, Role.VIEWER instantiate
- can_perform(Role.ADMIN, "delete_team") returns True
- can_perform(Role.VIEWER, "delete_team") returns False
- can_perform(Role.MEMBER, "create_team") returns False
```

---

## Step 5: Would This Have Prevented the Bug?

**Yes, because:**

1. **Scope is explicit:** "Do NOT create a route decorator"
2. **Constraints are clear:** "No new dependencies" (decorator would need auth middleware)
3. **Interface contract is documented:** Tasks 2+ know what to import and can rely on
4. **Acceptance criteria don't require the decorator:** Task 1 passes if Role enum and can_perform() work

**The AI's response would now be:**
- ✅ Role enum: same as before
- ✅ can_perform(): same as before
- ✅ No requires_role() decorator (prompt explicitly forbids it)

---

## Step 6: Applying This Lesson to Module 02

**The Principle:**

Before writing Task N's prompt, ask:
1. What does Task N produce? (Be specific: table names, column names, function signatures)
2. What does Task N depend on? (Which prior tasks must be done first?)
3. Write the interface contract: What exactly must Task N consume from dependencies?
4. Include that contract in the prompt

**Example: Before writing Task 2 prompt**

```
INTERFACE CONTRACT (what you depend on):
From Task 1:
- Role enum exists in app/models.py with values: ADMIN, MEMBER, VIEWER
- can_perform(role: Role, action: str) → bool is available

You may assume these exist. If you cannot import them, Task 1 was not done correctly.

INTERFACE CONTRACT (what downstream tasks depend on):
You will produce:
- Table 'teams' with columns: id (UUID), name (str), owner_id (FK to users), 
  created_at, updated_at
- Table 'team_members' with columns: id (UUID), team_id (FK to teams), 
  user_id (FK to users), role (enum: admin/member/viewer), joined_at

Downstream tasks (Task 3+) will import from your output and query these tables.
Do NOT rename or remove these columns — they are locked contracts.
```

This forces the decomposition to be explicit, not assumed.

---

## Summary: Interface Contract Pattern

| Element | Definition | Why It Matters |
|---------|-----------|----------------|
| **Interface contract** | Exact specification of what one task produces and what downstream tasks expect | Catches conflicts before code is written |
| **Upstream deliverable** | Specific table names, columns, data types, function signatures | Downstream tasks know what to import and how to use it |
| **Downstream expectation** | Specific inputs/outputs the upstream task must provide | Upstream task knows exactly what constraints to satisfy |
| **Shared agreement** | Both sides of the contract written explicitly in the prompt | No ambiguity; AI cannot guess wrong |

When both sides of the contract are documented in the prompt, conflicts become visible **before execution**. The contract is the blueprint that keeps decomposition coherent.

---

## Files to Update

**File:** `progress/ai-augmented-engineering/module-02-task-tree.md`

**Update needed:** Add "Interface Contracts" section to each task, specifying:
- What this task produces (with exact names/types)
- What this task depends on (with exact names/types)
- What downstream tasks depend on this task's output

This becomes the reference point for all prompt refinements.

---

## Next Action

Execute the revised Prompt 1 (with scope clarification and without the requires_role decorator). Verify that:
1. Role enum produces correctly
2. can_perform() works for all 3 roles
3. requires_role decorator is NOT present (confirming scope was respected)

Then advance to the REFLECT step.
