# Module 3: BREAK - Issues Found

## Break #1: APP_ENV has implicit default ✓ FOUND

**Issue:**
```python
app_env: Environment  # No explicit default, but Environment enum has 'development' as first value
```

**Symptom:**
```python
# Missing APP_ENV, Settings() still succeeds
s = Settings(port=8000, database_url='...', jwt_secret='...')
# app_env defaults to Environment.development
print(s.app_env)  # Output: Environment.development
```

**Why this is dangerous:**
- Production server forgets to set APP_ENV
- Service silently defaults to development
- Error handling shows stack traces (security leak)
- Logging is verbose (noise in production)
- CORS is permissive (if we had CORS configured)
- Service looks fine from outside, but configuration is wrong

**Fix:**
APP_ENV must be explicitly required with no default.

---

## Break #2: Dockerfile Healthcheck uses wrong endpoint ✓ FOUND

**Issue:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/live || exit 1
```

**Problem:**
- App defines `@app.get("/health")` not `/live`
- Healthcheck fails because `/live` doesn't exist
- Docker marks container as unhealthy
- Orchestrator (Kubernetes, Docker Compose) thinks container is broken

**Symptom:**
- Container logs show no errors
- Service is actually running correctly
- But healthcheck returns 404
- Docker/orchestrator thinks it's dead

**Fix:**
Change healthcheck to use `/health` endpoint

---

## Break #3: Dockerfile hardcodes PORT ✓ FOUND

**Issue:**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Problem:**
- PORT is hardcoded to 8000
- Environment variable PORT is ignored
- If production sets `PORT=9000` via environment, app still listens on 8000
- Loadbalancer expects 9000, can't reach service

**Symptom:**
- Service starts successfully
- But on wrong port
- Traffic doesn't reach it
- Looks like infrastructure problem, but it's configuration problem

**Fix:**
Use environment variable in CMD: `--port", "${PORT}"]` or pass PORT as env var at runtime

---

## Summary: Three Breaks Found

1. ✓ APP_ENV silently defaults to development (should be required)
2. ✓ Healthcheck uses non-existent `/live` endpoint
3. ✓ Dockerfile hardcodes PORT instead of using environment variable

All three are silent failures: service looks OK from the outside, but configuration is wrong.

**Next Step:** Document fixes and proceed to FIX step.
