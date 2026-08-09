# Module 02 VERIFY: Actual Codebase Inspection

**Date:** 2026-08-08  
**Goal:** Verify 3 critical assumptions from AI-generated Prompt 1 output against actual codebase

---

## Finding 1: Route Definition Pattern (Sync vs Async)

### Question
Are existing routes defined as plain `def` or `async def`? Will the async decorator work?

### What I Found

**File: api/app/routers/links.py**

```python
@router.post("", response_model=LinkCreateResponse, status_code=status.HTTP_201_CREATED)
def create_link_route(                                     # ← PLAIN def, NOT async def
    payload: LinkCreate,
    request: Request,
    db_session: Session = Depends(get_db_session),
) -> LinkCreateResponse:
    ...

@router.get("")
def list_links_route(                                      # ← PLAIN def
    ...

@router.get("/{link_id}", response_model=LinkRead)
def get_link_by_id_route(                                  # ← PLAIN def
    ...
```

**File: api/app/routers/redirect.py**

```python
@router.get("/r/{code}", status_code=307)
def redirect_by_code(code: str, db_session: Session = Depends(get_db_session)) -> RedirectResponse:  # ← PLAIN def
    ...
```

### ⚠️ CRITICAL ISSUE FOUND

**All existing routes are defined as plain `def`, not `async def`.**

The AI-generated `requires_role` decorator is:
```python
async def wrapper(*args, **kwargs):
    current_user = kwargs.get("current_user")
    if current_user is None or role_order.get(current_user.role, -1) < role_order[min_role]:
        raise HTTPException(...)
    return await func(*args, **kwargs)
```

**Problem:** If you apply this decorator to a plain `def` route:
```python
@requires_role(Role.ADMIN)
def create_team_route(...):  # ← PLAIN def
    ...
```

**What happens:**
1. Decorator wraps it with `async def wrapper`
2. Route handler is now async
3. But the actual function body is still synchronous
4. FastAPI expects either fully async or fully sync
5. **Result: TypeError or unexpected behavior at runtime**

### Impact: 🚨 **HIGH RISK**

The decorator MUST be refactored to support sync functions, or ALL team routes must be declared as `async def`.

---

## Finding 2: Current User Auth Pattern

### Question
Does the actual auth pattern pass `current_user` as a kwarg with a `.role` attribute?

### What I Found

**File: api/app/main.py** — Complete inspection

```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Service starting", ...)
    yield
    logger.info("Service shutting down")

app = FastAPI(title="URL Shortener", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)

# Routes registered:
app.include_router(links.router)
app.include_router(redirect.router)
```

**File: api/app/middleware/request_logging.py** — Middleware inspection

```python
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        req_id = new_request_id()
        token = request_id_ctx.set(req_id)
        ...
        response = await call_next(request)
        ...
        return response
```

### ⚠️ **NO AUTHENTICATION MIDDLEWARE EXISTS**

**Finding:**
- ✅ RequestLoggingMiddleware exists (only middleware in system)
- ❌ **NO JWT validation middleware**
- ❌ **NO current_user context injection**
- ❌ **NO dependency for get_current_user()**
- ❌ **NO User model in models.py**

**Evidence:**
- main.py registers only RequestLoggingMiddleware
- No other middleware defined anywhere
- Links routes use only `db_session: Session = Depends(get_db_session)` as dependency
- No routes pass `current_user` to handlers

### Impact: 🚨 **BLOCKING**

The AI-generated decorator assumes:
```python
current_user = kwargs.get("current_user")
if current_user is None or role_order.get(current_user.role, -1) < role_order[min_role]:
```

**But in reality:**
- There is NO `current_user` in kwargs
- There is NO way to get current_user (auth middleware not built yet)
- The decorator will ALWAYS fail because `current_user` is None

**This decorator cannot work until:**
1. A get_current_user() dependency is created
2. JWT middleware is implemented
3. Current user context is established in the request
4. User/Team relationship is defined

---

## Finding 3: Constraint Violation - "Return exact dict/bool, not exceptions"

### Question
The prompt said "Return exact dict/bool, not exceptions" — does the AI-generated output violate this?

### What I Found

**Prompt constraint:**
```
CONSTRAINTS:
- No database changes
- No new dependencies
- Follow the same import style as app/models.py
- Return exact dict/bool, not exceptions
```

**AI-generated code:**
```python
def can_perform(role: Role, action: str) -> bool:
    """..."""
    return action in _PERMISSIONS.get(role, set())
    # ✅ Returns bool — COMPLIES

def requires_role(min_role: Role):
    """..."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None or role_order.get(current_user.role, -1) < role_order[min_role]:
                raise HTTPException(  # ← VIOLATES CONSTRAINT
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### ⚠️ **CONSTRAINT VIOLATION**

**Problem:** The constraint "Return exact dict/bool, not exceptions" was meant for the permission functions:
- ✅ `can_perform()` correctly returns bool
- ❌ `requires_role()` raises HTTPException instead

**Was this the right interpretation?**
- The constraint was ambiguous — it was meant for `can_perform()` (return bool, not raise)
- But `requires_role()` is a route decorator, so raising HTTPException is actually the CORRECT pattern for routes
- However, the prompt didn't clarify this distinction

**Impact: ⚠️ **MEDIUM**

This is ambiguous prompt language, not an AI error. The decorator is correct for routes. But the prompt needed to say: "The permission check functions should return bool/dict. The route decorator can raise HTTPException."

---

## Summary: Actual Codebase vs AI Output

| Assumption | What Prompt Expected | What Code Actually Is | Impact |
|------------|---------------------|----------------------|--------|
| **Route pattern** | Async-compatible decorator | All routes are plain `def` | 🚨 BLOCKING — decorator broken |
| **Auth pattern** | current_user kwarg with .role | No auth middleware, no current_user | 🚨 BLOCKING — decorator non-functional |
| **Exception handling** | Return dict/bool not exceptions | HTTPException pattern used | ⚠️ AMBIGUOUS — prompt unclear |

---

## Root Cause: Decomposition Assumptions

This is exactly the BREAK step pattern: **Task 1 output assumes Task X is already done.**

The AI-generated `requires_role` decorator assumes:
1. ✅ FastAPI middleware will inject `current_user` into kwargs
2. ✅ `current_user` will have a `.role` attribute
3. ✅ All routes are async or decorator is sync-compatible

**But Task 1's job was ONLY:** "Create Role enum and permission matrix"

**What Task 1 accidentally did:** Designed a decorator that depends on infrastructure (auth middleware) and route patterns (async) that don't exist yet and aren't Task 1's responsibility.

**The bug:** Prompt 1 was too broad. It asked for 3 things:
1. Role enum ✅ (pure data, correct)
2. can_perform() function ✅ (pure logic, correct)
3. requires_role() decorator ❌ (assumes Task X is done, assumes route pattern)

**Should have been:** Split into Task 1 (enum + function) and Task 4-modified (decorator that's integrated with actual routes).

---

## What Agent Should Have Done

If the agent had inspected the actual codebase (which Module 01 taught us to do):

1. Read app/routers/links.py → "All routes are def, not async def"
2. Read main.py → "No auth middleware"
3. Recognized the conflict → Said something like:
   ```
   "CONFLICT DETECTED: I'm generating an async decorator, but all existing 
   routes are def (sync). This will cause TypeError. Should I:
   (a) Make decorator support sync functions too, or
   (b) Flag that all team routes must be async?"
   ```

But the prompt didn't ask the agent to verify — so it assumed.

---

## Verdict: Prompt 1 Quality

**Acceptance Criteria:**
- ✅ Role.ADMIN, Role.MEMBER, Role.VIEWER instantiate
- ✅ can_perform(Role.ADMIN, "delete_team") returns True
- ✅ can_perform(Role.VIEWER, "delete_team") returns False

**Grade:** 
- **Role enum + can_perform()**: 100/100 (perfect)
- **requires_role() decorator**: 20/100 (assumes infrastructure that doesn't exist, sync/async mismatch, assumes auth pattern)
- **Overall Prompt 1**: 60/100 (should have been split into two tasks or been more specific about route patterns)

**Action:**
- ✅ ACCEPT: Role enum and can_perform() function (use as-is)
- ❌ REJECT: requires_role() decorator (conflicts with actual system)
- → Need Task 1b or Task 4-modified for decorator that integrates with real auth pattern

---

## Lesson for Module 02

**This is the core skill:** Not just "does the code compile" but "does this code assume something that doesn't exist yet?"

The AI's decorator is technically well-written. It just assumes:
- Auth middleware exists (Task 5 or later, not Task 1)
- Routes are async (they're not)
- current_user is in kwargs (it's not set up yet)

These are **dependency conflicts**, not code quality issues.

**Better Prompt 1 would have included:**
```
CONTEXT:
- All existing routes are defined as plain def, not async def (see app/routers/links.py)
- There is no auth middleware yet (see app/main.py - only RequestLoggingMiddleware)
- Do NOT create a route decorator in Task 1 (that's Task X responsibility)
- Just create: Role enum and can_perform() function
```

But our prompt was written from the task tree plan, not from inspecting the actual code.

**Module 01 taught us:** Inspect actual code, don't assume.  
**Module 02 is teaching us:** Plan decomposition, then verify assumptions against reality before the AI generates.
