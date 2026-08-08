# Module 3: FIX - Implementation Plan

## Precedence Test Results ✓
**Environment variable precedence IS correct:**
- Local: OS environment variables > .env file ✓
- Docker: `-e` flag values > .env file (if .env exists) ✓

**Confirmed:** This is NOT the bug. pydantic-settings correctly prioritizes environment variables.

---

## Bugs to Fix

### Bug #1: APP_ENV has implicit default (CRITICAL)
**File:** `api/app/config.py`

**Problem:**
```python
app_env: Environment  # No explicit default, but defaults to first enum value
```

**Why it's a bug:**
- `Environment` enum has `development` as first value
- pydantic creates a default from the first enum value
- Settings() without APP_ENV succeeds and defaults to development
- **Production impact:** Production server forgets APP_ENV → runs in development mode → security vulnerability

**Fix:**
Make APP_ENV explicitly required by adding `...` (ellipsis) to mark it as required, or use pydantic's Field with no default:

```python
from pydantic import Field

class Settings(BaseSettings):
    app_env: Environment = Field(...)  # Explicitly required, no default
    # OR just ensure there's no default at all
```

But actually, looking at the code, `app_env: Environment` should already be required. The issue is that pydantic-settings reads from environment, and if APP_ENV is in .env, it gets the value. If APP_ENV is NOT in .env AND not in the environment, it... defaults to development.

**Real fix:** Add a validator that explicitly checks APP_ENV is set:

```python
@field_validator("app_env", mode="before")
@classmethod
def validate_app_env(cls, v):
    if v is None:
        raise ValueError("APP_ENV must be set to one of: development, staging, production")
    return v
```

Or better: update .env.example and ensure documentation is clear that APP_ENV is required.

---

### Bug #2: Dockerfile healthcheck uses /live endpoint (MEDIUM)
**File:** `api/Dockerfile`

**Problem:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/live || exit 1
```

**Why it's a bug:**
- App only defines `@app.get("/health")`
- `/live` endpoint doesn't exist
- Healthcheck returns 404
- Docker thinks container is unhealthy even though app is working
- Orchestrator (Kubernetes, Compose) thinks container is dead

**Fix:**
Change endpoint to `/health`:
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

### Bug #3: Dockerfile hardcodes port 8000 (MEDIUM)
**File:** `api/Dockerfile`

**Problem:**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Why it's a bug:**
- PORT is hardcoded to 8000
- If deployment sets `PORT=9000` via environment, uvicorn listens on 8000, not 9000
- Traffic doesn't reach service
- Looks like infrastructure/networking problem, but it's a config problem

**Fix:**
Pass PORT from environment. In Alpine/Debian containers, shell expansion works:
```dockerfile
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

Or use a script that passes it dynamically (but shell expansion is simpler).

---

## Fix Implementation Order

1. **APP_ENV validation** (most critical - security)
2. **Healthcheck endpoint** (important - affects orchestration)
3. **Dockerfile PORT** (important - affects deployment)

---

## After Fixes: Verification Plan

1. ✓ Remove APP_ENV from environment → service crashes with "APP_ENV is required"
2. ✓ Set all variables correctly → service starts, /health responds 200
3. ✓ Docker with -e PORT=9001 → uvicorn listens on 9001, not 8000
4. ✓ Healthcheck succeeds → curl -f http://localhost:8000/health returns 200
