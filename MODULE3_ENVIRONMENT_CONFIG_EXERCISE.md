# Module 3: Environment Management - Micro-Exercise Analysis

## Current Configuration Status

### Existing Environment Variables

From `api/.env` and `api/.env.example`:

| Variable | Current Value | Dev | Staging | Production | Notes |
|----------|---------------|-----|---------|------------|-------|
| PORT | 8000 | ✓ Same | ? Different | ? Different | Service listening port |
| DATABASE_URL | localhost:55432 | ✓ Same | ✗ Different | ✗ Different | Database connection - changes per environment |
| LOG_LEVEL | info | ✓ Same | ? Same | ✗ Different | Logging verbosity - prod needs less verbose |
| MONGODB_URI | (empty) | ✓ Same | ✓ Same | ✓ Same | Not currently used |
| REDIS_URL | (empty) | ✓ Same | ✓ Same | ✓ Same | Not currently used |
| JWT_SECRET | replace-me-locally | ✗ BROKEN | ✗ BROKEN | ✗ BROKEN | Security: needs real secrets per environment |
| API_KEY_A | replace-me-locally | ✗ BROKEN | ✗ BROKEN | ✗ BROKEN | Security: needs real secrets per environment |
| API_KEY_B | replace-me-locally | ✗ BROKEN | ✗ BROKEN | ✗ BROKEN | Security: needs real secrets per environment |

### Analysis

**Variables that change per environment:**
- DATABASE_URL (localhost dev → staging RDS → production RDS with different credentials)
- LOG_LEVEL (verbose in dev → minimal in production to reduce noise)
- JWT_SECRET (secrets never hardcoded; must come from secrets manager)
- API_KEY_A, API_KEY_B (secrets never hardcoded)

**Variables that stay the same:**
- PORT (always 8000 - service-level concern, not infrastructure)
- MONGODB_URI, REDIS_URL (not used yet; when used, may vary)

---

## Current Problems

### Problem 1: Secrets in Code
**Issue:** `.env.example` shows "replace-me-locally" but actual `.env` also has it. If this `.env` file were committed to git (it should NOT be, but mistakes happen), production secrets would be exposed.

**Risk:** One `git add .` → one `git commit` → secrets leaked to GitHub permanently.

**Current state:** 
- ✓ `.env` is in `.gitignore` (good)
- ✗ Local "replace-me-locally" is not a real secret (will break in staging/prod)

---

### Problem 2: Localhost Hardcoded
**Issue:** `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:55432/upsk_sdf`

When this Docker image runs on staging or production, it still tries to connect to localhost. The service crashes with "connection refused" — a generic error that tells you nothing about which environment or which database you should be using.

**Example failure sequence:**
1. Developer pushes code → GitHub Actions builds image
2. Image pushed to ghcr.io
3. Staging team deploys the image
4. Service starts and immediately fails: `connection refused on localhost:5432`
5. Staging team sees this error and has no idea what's wrong
6. They check config files, they are missing from the container
7. They re-read the Dockerfile and realize the image has no environment variable setup

**Why:** Docker image should contain NO hardcoded environment configuration. The image itself is environment-agnostic.

---

### Problem 3: Teammate Onboarding
**Scenario:** New teammate clones the repo tomorrow.

```bash
git clone https://github.com/lakshsharda/caw_assignment.git
cd caw_assignment/api
python -m uvicorn app.main:app --reload
```

**What happens:**
- No `.env` file exists (it's in .gitignore)
- Config loader tries to read `.env` 
- PORT is not set → validation error: "PORT must be an integer between 1 and 65535"
- DATABASE_URL is not set → validation error: "DATABASE_URL must be set"
- Service crashes with an error message
- Teammate is confused: "The README says to just run this command!"

**Why this is bad:** The error message is *correct* but the *setup process* is missing. There should be a clear onboarding path: copy `.env.example` to `.env`, fill in values, then run.

---

## What Module 3 Solves

We will implement proper environment configuration by:

1. **Separating configuration from code**
   - No database URLs in Docker image
   - Configuration injected at runtime via environment variables

2. **Environment-specific defaults**
   - Dev: localhost defaults for fast iteration
   - Staging: RDS credentials from config
   - Production: Secrets from GitHub secrets or environment

3. **Clear onboarding path**
   - `.env.example` → clear template
   - Documentation explaining which values are required vs optional
   - Service fails FAST and CLEARLY if critical config is missing

4. **Secret handling**
   - Never commit `.env` to git
   - Use GitHub Secrets for CI/CD
   - Use environment variables for runtime config
   - Validate that required secrets are present

---

## Next Steps

1. **Update config.py** to support environment-specific defaults
2. **Create .env.local** (dev-only) with clear documentation
3. **Update Dockerfile** to inject configuration at runtime (not build time)
4. **Document** the setup flow for new developers
5. **Test** that the service fails clearly when config is missing
6. **Update CI/CD** to pass environment variables during container runs

---

**Status:** Exercise complete - identified configuration gaps and risks
**Next:** Proceed to CONTEXT → BUILD section to implement these fixes
