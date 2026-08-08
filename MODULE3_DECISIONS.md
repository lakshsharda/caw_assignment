# Module 3: Environment Management - Strategic Decisions

## Decision 1: Secret Management Strategy

**CHOICE: A - Platform environment variables**

**Why this choice:**
- GitHub Actions integrates GitHub Secrets directly into CI/CD
- Runtime platforms (Render, Railway, Fly, Heroku) all have built-in environment variable dashboards
- Secrets are automatically masked in logs
- No infrastructure to maintain or babysit
- Perfect fit for a team of 1-2 people with one service

**Tradeoffs accepted:**
- No audit trail of who changed what secret when (fine for now)
- Manual rotation process (fine for this scale)
- No automatic secret rotation policies (can add later if needed)

**When we'd reconsider:**
- Team grows to 50+ engineers
- Need PCI/HIPAA/SOC2 compliance (audit trails required)
- Multiple services and teams accessing shared secrets (Vault makes sense then)

**Implementation:**
- GitHub Secrets: DATABASE_URL_PROD, JWT_SECRET_PROD, API_KEY_A_PROD, API_KEY_B_PROD
- Render/Railway: UI to set environment variables at deploy time
- Local dev: .env file with dev values (never committed)

---

## Decision 2: Configuration Approach

**CHOICE: A - Single config module with environment variable overrides**

**Why this choice:**
- One file to maintain (config.py), not three (dev, staging, prod)
- When adding a new config value, update it once
- Junior developers understand: "one config file, environment variables override"
- Easier to review in code: no hidden config files in deployment

**How it works:**
1. config.py defines ALL possible config values
2. Each value reads from environment variable with fallback to a safe default (or fails)
3. Required values have NO defaults → service fails at startup if missing
4. Optional values have safe dev defaults → service starts in dev without thinking

**Example:**
```python
class Settings(BaseSettings):
    port: int  # No default → must be set, fails if missing
    database_url: str  # No default → must be set
    log_level: str = "info"  # Has default → dev-friendly
    jwt_secret: str  # No default → must be set
```

**Prevents the GitLab incident:**
- If DATABASE_URL is not set, service fails immediately: "DATABASE_URL must be set"
- Cannot accidentally connect to localhost in production
- Clear error message tells you exactly what's wrong

**Tradeoffs managed:**
- Avoid "helpful defaults" that leak between environments
- Service fails FAST and CLEARLY
- No ambiguity about which environment is running

---

## Implementation Strategy

### For Development
```bash
cp api/.env.example api/.env.local
# Edit .env.local with local values:
PORT=8000
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:55432/upsk_sdf
LOG_LEVEL=debug
JWT_SECRET=dev-secret-only-for-local-testing
API_KEY_A=dev-key-only
API_KEY_B=dev-key-only
```

### For Staging/Production
```bash
# Platform (e.g., Render) provides env vars:
PORT=8000
DATABASE_URL=postgresql+psycopg://prod_user:$PROD_PASSWORD@prod-db.render.com/urlshortener
LOG_LEVEL=warn
JWT_SECRET=$JWT_SECRET_PROD  # From Render secrets
API_KEY_A=$API_KEY_A_PROD    # From Render secrets
API_KEY_B=$API_KEY_B_PROD    # From Render secrets
```

### For CI/CD (GitHub Actions)
```yaml
# .github/workflows/ci.yml - during test runs
env:
  DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost:55432/test_db
  JWT_SECRET: test-secret
  API_KEY_A: test-key
  API_KEY_B: test-key
  PORT: 8000
  LOG_LEVEL: debug
```

---

## What's Next

1. **Update config.py** to remove optional defaults from required secrets
2. **Create .env.local template** (git-ignored) with clear documentation
3. **Update Docker entrypoint** to validate config at startup
4. **Document setup flow** for new developers
5. **Update GitHub Actions** to inject test config
6. **Verify** that service fails clearly when config is missing

---

**Decisions recorded:** August 8, 2026
**Status:** Ready to implement (BUILD section next)
