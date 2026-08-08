# Module 3: Environment Management - BUILD Complete

## What We Built

A production-ready configuration system that implements the three key principles:

### Chunk 1: Config Validation Module ✓

**File:** `api/app/config.py`

**Key features:**
- `Environment` enum: development, staging, production (no defaults - must be set)
- `Settings` class with pydantic-settings for automatic validation
- Required fields (crash if missing):
  - `app_env`: Environment enum
  - `port`: 1-65535
  - `database_url`: non-empty string
  - `jwt_secret`: min 32 characters
- Optional fields (safe defaults):
  - `log_level`: default="info"

**Validation approach:** Fail-fast
- If any required config is missing, service crashes at startup
- Error message names the exact missing field
- Alternative (silent defaults) would hide configuration errors until runtime failures

**Properties for environment checks:**
```python
settings.is_production  # True if app_env == "production"
settings.is_development # True if app_env == "development"
settings.is_staging     # True if app_env == "staging"
```

### Chunk 2: Environment-Aware Behavior ✓

**File:** `api/app/main.py`

**Startup logging:**
```python
logger.info("Service starting", extra={
    "environment": settings.app_env.value,
    "port": settings.port,
    "log_level": settings.log_level,
})
# NOTE: Does NOT log database_url, jwt_secret
```

**Exception handling - environment-aware:**
```python
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    show_details = settings.app_env in (
        Environment.development,
        Environment.staging,
    )
    
    body = {"error": "Internal Server Error"}
    if show_details:
        body["details"] = str(exc)  # Full error in dev/staging
        body["environment"] = settings.app_env.value
    # In production: generic error only (security)
    
    return JSONResponse(status_code=500, content=body)
```

**Why this matters:**
- Development: verbose errors help you debug
- Staging: full errors for testing before production
- Production: generic errors prevent information leakage (attacker can't see your stack traces)

**Health endpoint:**
```python
@app.get("/health")
def health():
    return {
        "ok": True,
        "port": settings.port,
        "environment": settings.app_env.value,
    }
```

### Chunk 3: Secrets Separation ✓

**Rule 1: .env never in git**
- ✓ `.env` is in `.gitignore`
- ✓ Local developers have `.env` but it's git-ignored

**Rule 2: .env.example always in git**
- ✓ `api/.env.example` is committed
- ✓ Documents every variable, its purpose, required/optional, and constraints

**Rule 3: Docker images contain zero environment-specific values**
- ✓ `.dockerignore` excludes `.env`
- ✓ Verified: `docker run` shows no `.env` in container
- ✓ Configuration injected at runtime via environment variables

**Updated `.env.example`:**
```bash
# --- Application ---
APP_ENV=                     # REQUIRED. One of: development, staging, production
PORT=                        # REQUIRED. Integer. The port the server listens on.

# --- Database ---
DATABASE_URL=                # REQUIRED. Full PostgreSQL connection string

# --- Authentication ---
JWT_SECRET=                  # REQUIRED. Min 32 characters. Used to sign auth tokens.

# --- Logging ---
LOG_LEVEL=                   # OPTIONAL. Default: info. One of: debug, info, warn, error
```

**Local `.env` for development:**
```bash
APP_ENV=development
PORT=8000
LOG_LEVEL=debug
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:55432/upsk_sdf
JWT_SECRET=dev-secret-key-min-32-chars-long-xxxxxxx
```

## Testing & Validation

**Test file:** `api/test_config_validation_direct.py`

All tests pass ✓:
1. ✓ Empty DATABASE_URL rejected with clear error
2. ✓ Empty JWT_SECRET rejected with clear error
3. ✓ JWT_SECRET < 32 chars rejected with clear error
4. ✓ Invalid APP_ENV (banana) rejected, shows valid values
5. ✓ Invalid PORT (99999) rejected with range error
6. ✓ Valid configuration accepted with all properties

**Docker verification:**
- Image builds successfully
- .env file is NOT in container
- Configuration must be injected at runtime
- Startup logs show environment info without secrets

## Error Prevention Pattern

This configuration design prevents the GitLab incident:

**Without this system:**
```bash
# Developer forgets to set DATABASE_URL in staging
# Service starts, seems healthy
# First query fails with "connection refused"
# At 2 AM, takes 30 minutes to debug
```

**With this system:**
```bash
# Developer forgets to set DATABASE_URL in staging
# Service crashes at startup
# Error: "Missing required configuration: database_url"
# Fixed in 30 seconds
```

Fail-fast > Silent failure

## Environment Configuration Strategy

### Development (local laptop)
```
APP_ENV=development
DATABASE_URL=localhost:5432
LOG_LEVEL=debug
JWT_SECRET=dev-only-key
Error responses: Full stack traces
```

### Staging (testing environment)
```
APP_ENV=staging
DATABASE_URL=staging-db.example.com:5432
LOG_LEVEL=info
JWT_SECRET=<from GitHub Secrets>
Error responses: Full stack traces (for debugging)
```

### Production
```
APP_ENV=production
DATABASE_URL=prod-db.example.com:5432
LOG_LEVEL=warn
JWT_SECRET=<from GitHub Secrets>
Error responses: Generic "Internal Server Error" only
```

## What Happens When...

### New Developer Joins
1. Clone repo
2. Copy `.env.example` to `.env` and fill in values
3. Run service → starts with clear error if required config is missing
4. No confusion about what values are needed

### Adding New Configuration Value
1. Update `config.py` (single place)
2. Add to `.env.example` with documentation
3. Update CI/CD env vars for testing
4. Update deployment platform (Render/Railway) for each environment
5. Validation automatically enforces it everywhere

### Configuration Drift
- ✗ Hard to happen: config is code + validated at startup
- ✗ If missing in one environment: startup crash (loud, obvious)
- ✓ If developer forgets: test will catch it before production

### Secrets Compromise
- If `.env` is accidentally committed to git:
  - All secrets are compromised and must be rotated
  - Secret is in git history forever (even if deleted)
  - Prevention: .env always in .gitignore
  - Remedy: Use GitHub to rotate secrets immediately

## CI/CD Integration

**GitHub Actions needs environment variables:**
```yaml
jobs:
  lint-and-test:
    env:
      APP_ENV: development
      PORT: 8000
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      JWT_SECRET: test-secret-that-is-longer-than-32-chars
```

**Build-and-push job for Docker:**
- Code is the same
- CI provides test environment variables
- Production image contains zero environment-specific values
- Image runs anywhere: Docker Desktop, staging server, production cluster

## Next Steps: Production Deployment

When deploying to Render/Railway/Heroku:
1. Create new environment variables in the platform UI
2. Copy values from GitHub Secrets (never commit production secrets)
3. Deploy image (same image used everywhere)
4. Platform injects environment variables at runtime
5. Service starts with correct configuration

---

**Status:** BUILD COMPLETE ✓
- Chunk 1: Config validation ✓
- Chunk 2: Environment-aware behavior ✓
- Chunk 3: Secrets separation ✓
- All validation tests passing ✓
- Docker image clean (no secrets) ✓
- Ready for production deployment ✓

**Next:** REFLECT step - answer design questions about configuration strategy
