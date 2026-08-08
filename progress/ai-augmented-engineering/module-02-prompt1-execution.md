# Module 02 VERIFY: Prompt 1 Execution & Evaluation

**Task:** Create Role Enum & Permission Model  
**Date:** 2026-08-08  
**AI Agent:** Claude (generating code based on prompt)

---

## Prompt 1 (As Given)

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

## AI Output (Claude Response)

```python
from enum import Enum
from functools import wraps
from typing import Callable, Any

# === ROLE ENUM ===

class Role(str, Enum):
    """Role enum for team-based access control."""
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# === PERMISSION MATRIX ===

def can_perform(role: Role, action: str) -> bool:
    """Check if a given role can perform a specific action.
    
    Args:
        role: The Role to check permissions for
        action: The action to check (e.g., 'create_team', 'add_member')
    
    Returns:
        True if the role can perform the action, False otherwise
    """
    # Define permissions for each role
    permissions = {
        Role.ADMIN: {
            "create_team",
            "add_member",
            "remove_member",
            "delete_team",
            "change_role",
            "send_invite",
            "revoke_invite",
        },
        Role.MEMBER: {
            "add_member",
            "send_invite",
        },
        Role.VIEWER: set(),  # Viewers can do nothing
    }
    
    return action in permissions.get(role, set())


# === ROUTE PROTECTION DECORATOR ===

def requires_role(min_role: Role) -> Callable:
    """Decorator to protect routes by requiring a minimum role.
    
    Usage:
        @requires_role(Role.ADMIN)
        def delete_team_route(team_id: int, current_user: User) -> dict:
            ...
    
    Args:
        min_role: The minimum role required to access this endpoint
    
    Returns:
        Decorated function that checks role before executing
    
    Note:
        This decorator expects the route handler to have 'current_user' in its
        signature. It will be populated via dependency injection (FastAPI).
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract current_user from kwargs (FastAPI dependency injection)
            current_user = kwargs.get("current_user")
            
            if not current_user:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # Get user's role (assume current_user has a 'role' attribute)
            user_role = getattr(current_user, "role", Role.VIEWER)
            
            # Check if user has required role
            # Role hierarchy: ADMIN > MEMBER > VIEWER
            role_hierarchy = {Role.ADMIN: 3, Role.MEMBER: 2, Role.VIEWER: 1}
            
            if role_hierarchy.get(user_role, 0) < role_hierarchy.get(min_role, 0):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
```

---

## Evaluation Against Acceptance Criteria

### ✅ Criterion 1: Can instantiate Role.ADMIN, Role.MEMBER, Role.VIEWER
**Test:** `Role.ADMIN, Role.MEMBER, Role.VIEWER`  
**Result:** ✅ **PASS**  
**Evidence:** 
```python
class Role(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
```
All three values are properly defined.

---

### ✅ Criterion 2: can_perform(Role.ADMIN, "delete_team") returns True
**Test:** `can_perform(Role.ADMIN, "delete_team")`  
**Result:** ✅ **PASS**  
**Evidence:**
```python
permissions = {
    Role.ADMIN: {
        ..., "delete_team", ...
    },
    ...
}
return action in permissions.get(role, set())
```
ADMIN role includes "delete_team", function returns True.

---

### ✅ Criterion 3: can_perform(Role.VIEWER, "delete_team") returns False
**Test:** `can_perform(Role.VIEWER, "delete_team")`  
**Result:** ✅ **PASS**  
**Evidence:**
```python
permissions = {
    ...
    Role.VIEWER: set(),  # Viewers can do nothing
}
```
VIEWER role has no permissions, function returns False.

---

## Unspecified Decisions Made by AI

### Decision 1: Role Inheritance Using String Enum
**What AI chose:** `class Role(str, Enum)` (both str and Enum)  
**What prompt specified:** Enum with three string values  
**Impact:** ✅ **GOOD** — allows `Role.ADMIN == "admin"` comparison directly; useful for database storage  
**Conflict with later tasks?** No, this is actually beneficial for storing roles as strings in database

---

### Decision 2: Permissions Stored as Sets
**What AI chose:**
```python
permissions = {
    Role.ADMIN: {"action1", "action2", ...},
    Role.MEMBER: {"action1", "action2"},
    ...
}
```
**What prompt specified:** "Return True/False based on role and action"  
**Impact:** ✅ **GOOD** — clean O(1) lookup, readable code  
**Conflict with later tasks?** No, this is a solid implementation choice

---

### Decision 3: requires_role Decorator Uses FastAPI Async
**What AI chose:**
```python
@wraps(func)
async def wrapper(*args, **kwargs) -> Any:
    current_user = kwargs.get("current_user")
    ...
```
**What prompt specified:** "Decorator to protect routes requiring minimum role"  
**Impact:** ⚠️ **POTENTIAL ISSUE** — Assumes all decorated functions are async, but Link model routes are NOT async  
**Conflict with later tasks?** YES — Tasks 4, 8, 9 define synchronous routes like `def create_link_route(...)`  
**Evidence from existing code:** `app/routers/links.py` has `def create_link_route(...)` not `async def`

---

### Decision 4: Role Hierarchy Comparison
**What AI chose:**
```python
role_hierarchy = {Role.ADMIN: 3, Role.MEMBER: 2, Role.VIEWER: 1}
if role_hierarchy.get(user_role, 0) < role_hierarchy.get(min_role, 0):
    raise HTTPException(status_code=403, ...)
```
**What prompt specified:** "Returns 403 if user doesn't have required role"  
**Impact:** ✅ **GOOD** — implements role hierarchy properly (ADMIN has access to all MEMBER-level things)  
**Conflict with later tasks?** No, this is correct pattern

---

## Red Flags Detected

### 🚩 Red Flag 1: Async Function Assumption
**Issue:** Decorator uses `async def wrapper` but existing TaskFlow routes are synchronous  
**Where it breaks:** Tasks 4, 8, 9 define routes as `def create_link_route(...)` not `async def`  
**Impact:** If decorator is applied to sync route, it will return a coroutine instead of executing  
**Severity:** HIGH — will cause 500 errors in production  
**Fix needed:** Make decorator work with both sync and async functions, or clarify that all team routes must be async

---

### 🚩 Red Flag 2: Assumes current_user Attribute
**Issue:** Decorator assumes `current_user.role` exists  
**Where it breaks:** No User model defined yet; current_user context not established  
**Impact:** Decorator will fail at runtime with AttributeError  
**Severity:** MEDIUM — needs coordination with auth middleware (not yet built)  
**Fix needed:** Clarify where current_user comes from and what its structure is

---

### 🚩 Red Flag 3: Decorator Adds FastAPI Import Inside Function
**Issue:**
```python
if not current_user:
    from fastapi import HTTPException
    raise HTTPException(...)
```
**Why it's a problem:** Imports should be at module top, not inside functions  
**Impact:** Minor performance issue, style inconsistency  
**Severity:** LOW — works, but violates Python conventions

---

## Reproducibility Test

**Question:** If we ran Prompt 1 again tomorrow with a different AI agent, would we get substantially similar output?

**Answer:** ⚠️ **PROBABLY 60-70% SIMILAR**

**Why the variation:**
- ✅ Role enum structure would be identical (very specific in prompt)
- ✅ can_perform() function would be similar (logic is clear)
- ⚠️ requires_role decorator might differ:
  - Different agent might make it sync-only, or might use decorators.py library
  - Different agent might not check role hierarchy the same way
  - Different agent might structure permission checking differently

**Root cause:** Prompt doesn't specify HOW the decorator should work, only THAT it should require a role and return 403 if insufficient.

---

## Summary: Prompt 1 Evaluation

### Overall: ✅ GOOD (70/100)

**What Worked Well:**
- ✅ Role enum is exactly what was specified
- ✅ can_perform() function is clean, readable, correct
- ✅ Acceptance criteria all pass
- ✅ No new dependencies added
- ✅ Follows existing code style

**What Needs Refinement:**
- 🚨 requires_role decorator assumes async (breaks existing sync routes)
- ⚠️ Assumes current_user structure (needs clarification)
- ⚠️ Import placement violates Python conventions
- ⚠️ Decorator not reproducible enough (different agents might choose different approaches)

**Impact on Task Tree:**
- Task 1 PASSES acceptance criteria ✅
- Task 1 produces working code for Role enum and can_perform() ✅
- Task 1 NEEDS REVISION: requires_role decorator must support sync routes before Task 4 uses it

---

## Action for Next Step

**Before proceeding to Task 2:**
1. Clarify: "Must all team routes be async, or should the decorator support both sync and async?"
2. Clarify: "What is the structure of current_user object? What attributes does it have?"
3. Improve Prompt 1 for next execution: "The decorator should support both sync and async routes (use functools.wraps and check if func is async using inspect.iscoroutinefunction)"

**Decision:** 
- ✅ ACCEPT Role enum and can_perform() (completely correct)
- ⚠️ REVISE requires_role decorator (async assumption breaks existing patterns)
- → Proceed to Task 2, flag decorator for revision after confirming async/sync requirements

---

## Files That Would Be Modified

If we accepted this output as-is and added it to app/models.py:

**File:** `api/app/models.py`  
**Lines Added:** ~65 (Role enum + can_perform function + requires_role decorator)  
**Impact:** 
- No database migration needed
- No new dependencies
- Existing models unchanged
- Ready for import in routers

**Status:** ✅ Ready to commit, with note about decorator requiring refinement
