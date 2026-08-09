# Module 03 BREAK: Convention Violation Analysis

**Date:** 2026-08-08  
**Learning:** Context packages are good but incomplete without explicit error handling documentation

---

## The Problem: Error Response Inconsistency

The BREAK scenario describes a real problem: AI-generated code that is technically correct but violates project conventions at the integration level.

### What Happens

1. Agent receives Task 3 (create Team endpoint)
2. Agent includes system context + task context
3. Agent generates working code with error handling
4. Code passes verification criteria: handles errors, returns status codes, looks clean
5. **BUT:** Error response format doesn't match existing API endpoints

### Example from Existing Codebase

Looking at actual code from `api/app/main.py`:

```python
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    detail = [
        {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": detail})

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception) -> JSONResponse:
    body: dict = {"error": "Internal Server Error"}
    if show_details:
        body["details"] = str(exc)
        body["environment"] = settings.app_env.value
    return JSONResponse(status_code=500, content=body)
```

So the existing pattern for errors is:
- **Validation errors (400):** `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`
- **Server errors (500):** `{"error": "..."}`

And from `api/app/services/links_service.py`:

```python
if link is None:
    raise HTTPException(status_code=404, detail="Link not found")
```

The pattern is: **use HTTPException, let global exception handler format the response**.

### What an AI Agent Might Produce Instead

Without explicit error format documentation, an agent might write:

```python
# In a route handler
@router.post("/teams")
def create_team_route(payload: TeamCreate) -> TeamCreateResponse:
    if not payload.name:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "code": "TEAM_NAME_REQUIRED",
                "message": "Team name is required."
            }
        )
    ...
```

**Problem:** The error response format is different:
- Existing: `{"detail": "..."}`  or `{"error": "..."}`
- Agent produced: `{"status": "error", "code": "...", "message": "..."}`

Both are valid API patterns, but they're inconsistent.

---

## Root Cause: Incomplete Context Package

### What the System Context Document Should Have Included

The system context document in Module 03 BUILD included a section on error handling, but it was **described** rather than **specified**:

```markdown
### Error Handling
- Global exception handlers in main.py
- Per-service error pattern: Use FastAPI's HTTPException with status code and detail
- Error responses:
  - Validation errors: 400 with {"detail": [{"loc": [...], "msg": "...", "type": "..."}]}
  - Not found: 404 with {"detail": "Link not found"}
  - Generic errors: 500 with {"error": "Internal Server Error"}
```

This is good, but **not specific enough**. A better approach:

```markdown
### Error Handling — EXACT PATTERN

All errors must use HTTPException. Do NOT return JSONResponse directly.

Pattern 1: Not found (404)
    raise HTTPException(status_code=404, detail="Resource not found")
    Becomes: {"detail": "Resource not found"}

Pattern 2: Validation error (400)
    Always raised by Pydantic automatically, never manually.
    Becomes: {"detail": [{"loc": [...], "msg": "...", "type": "..."}]}

Pattern 3: Permission denied (403)
    raise HTTPException(status_code=403, detail="Insufficient permissions")
    Becomes: {"detail": "Insufficient permissions"}

Pattern 4: Business logic error (400)
    raise HTTPException(status_code=400, detail="Team name cannot be empty")
    Becomes: {"detail": "Team name cannot be empty"}

CRITICAL: Do NOT create custom error objects. Do NOT use JSONResponse for errors.
Do NOT wrap errors in status/code/message fields. Let FastAPI's exception handler
format the response.

EXAMPLE OF WRONG PATTERN (do not do this):
    # WRONG
    return JSONResponse(status_code=400, content={
        "status": "error",
        "code": "VALIDATION_ERROR",
        "message": "..."
    })
    
    # RIGHT
    raise HTTPException(status_code=400, detail="...")
```

### Why This Wasn't Caught in Context Packages

The task contexts for Tasks 1-3 included "FILES TO READ" like:
- `app/services/links_service.py` (shows HTTPException pattern)
- `app/main.py` (shows exception handlers)

But they didn't explicitly state: **"Compare your error responses to these exact examples before submitting."**

---

## How to Prevent This: Enhanced Context Package

### Add to System Context Document

Create a new section with **exact, copy-paste-able examples**:

```markdown
## ERROR HANDLING REFERENCE — COPY/PASTE EXAMPLES

Copy these patterns exactly when handling errors:

### Pattern: Not Found (404)
```python
# In service:
if resource is None:
    raise HTTPException(status_code=404, detail="Team not found")

# Client receives:
{
  "detail": "Team not found"
}
```

### Pattern: Validation Error (400)
```python
# In schema:
@field_validator("name")
@classmethod
def validate_name(cls, value: str) -> str:
    if not value or not value.strip():
        raise ValueError("Team name cannot be empty")
    return value

# Client receives (automatic, from Pydantic):
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "Team name cannot be empty",
      "type": "value_error"
    }
  ]
}
```

### Pattern: Permission Denied (403)
```python
# In service:
if user_role != Role.ADMIN:
    raise HTTPException(status_code=403, detail="Only admins can delete teams")

# Client receives:
{
  "detail": "Only admins can delete teams"
}
```

### Prohibited Pattern (NEVER DO THIS)
```python
# WRONG - do not write this:
return JSONResponse(status_code=400, content={
    "error": {
        "code": "CUSTOM_ERROR",
        "message": "Something went wrong"
    }
})

# WRONG - do not write this:
raise CustomException("Something went wrong")

# WRONG - do not write this:
return {"success": False, "message": "..."}
```
```

### Add to Task Context

In each task's context bundle, add:

```markdown
### ERROR HANDLING

For this task, all errors must follow the patterns in the System Context document,
"ERROR HANDLING REFERENCE" section. Do NOT invent new error formats.

When you handle errors, verify:
1. You used HTTPException, not JSONResponse or custom exceptions
2. The response format matches the examples in System Context
3. A client parsing responses from this endpoint would use the same parsing code as existing endpoints
```

---

## Lesson: Context is Not Enough Without Specificity

This is the key insight of Module 03 BREAK:

**Good context document:** "Use HTTPException for errors"  
**Better context document:** Here's the exact error format with copy-paste examples

The difference is **specificity**. An AI agent given vague guidance ("follow conventions") will interpret conventions reasonably but differently than you expected.

An AI agent given exact patterns ("copy this, never do that") will produce consistent output.

---

## How Context Packages Would Improve

### Version 1 (Current)
- ❌ Error handling described in prose
- ❌ "Follow existing patterns" with links to examples
- ✅ But doesn't guarantee consistency

### Version 2 (Better)
- ✅ Error handling specified with exact code examples
- ✅ Prohibited patterns explicitly listed
- ✅ Copy-paste-able reference section in system context
- ✅ Task-specific reminder: "Use the error patterns from System Context"
- ⚠️ Still relies on agent reading and following examples

### Version 3 (Best)
- ✅ All of Version 2
- ✅ PLUS: Post-generation verification hook that checks error format
- ✅ PLUS: Automated test that compares error response format to existing endpoints
- ✅ Would catch inconsistencies immediately

---

## Root Cause of Convention Violations

Context packages prevent violations when they are **specific enough**. Vagueness creates failures:

| Guidance | Outcome |
|----------|---------|
| "Use FastAPI's error handling" | Agent guesses what that means → inconsistency |
| "Raise HTTPException with status and detail" | Still ambiguous → might get wrapped differently |
| "Copy this exact pattern:" `raise HTTPException(status_code=404, detail="...")` | Clear → consistency |

**Module 03 learning:** Context engineering is not just "what files do I include" but also "how specifically do I specify each pattern."

---

## For This Bootcamp

Applying the lesson to Module 03 context packages:

**Current System Context:** Good foundation, but error handling section is descriptive

**Improved System Context:** Would add copy-paste examples for every error scenario

**Expected Result:** AI-generated Tasks 1-3 would produce error handling that exactly matches existing codebase

**If tasks hadn't been generated with improved context:** Would likely see the inconsistency in BREAK step, then refine the system context document, re-run tasks, and see improvement in next iteration

---

## Therac-25 Connection

Remember the Therac-25 interlude: operators didn't trust their observations when the machine said "ready."

Here, we're doing the opposite: **assuming the machine (AI agent) knows what "consistent error handling" means when we haven't been specific enough.**

The fix: **be so specific that ambiguity is impossible.** Copy-paste examples in system context, explicit checking in verification, automated tests to catch drift.

This is context engineering discipline.
