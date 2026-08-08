# Module 1-2 Verification Checklist

## ✓ Module 1: Containerization - COMPLETE

### Local Verification (Already Completed)
- [x] Docker Desktop running successfully
- [x] `docker build -t linkops-api:latest .` succeeds
- [x] Image size: 283MB (passes <300MB threshold)
- [x] `docker run` starts container on port 8000
- [x] Health check endpoint responds: `curl http://localhost:8000/health` → `{"ok":true,"port":8000}`
- [x] Container runs as non-root user: `docker exec linkops-test whoami` → `appuser`
- [x] Dockerfile uses multi-stage build (security + optimization)
- [x] `.dockerignore` properly configured

**Module 1 Evidence:** See `REAL_VERIFICATION_EVIDENCE.md` section 1

---

## ⏳ Module 2: CI/CD Pipeline - IN PROGRESS

### GitHub Push - COMPLETE
- [x] Repository created: https://github.com/lakshsharda/caw_assignment
- [x] All files committed and pushed to `main` branch
- [x] 3 commits pushed:
  1. Initial commit (Module 1-2 code)
  2. Test file with intentional failure (test demo)
  3. Documentation update

### Workflow Configuration - COMPLETE
- [x] `.github/workflows/ci.yml` created with 110+ lines
- [x] Triggers on: `push` to `main` branch with changes in `api/**`
- [x] Two jobs:
  1. **lint-and-test**: Python linting + pytest
  2. **build-and-push**: Docker build, size check, push to ghcr.io

### Watch Pipeline Execution - ACTION NEEDED
**Visit:** https://github.com/lakshsharda/caw_assignment/actions

**What to check:**
1. **Most recent workflow run** (should be "docs: update verification evidence...")
2. **Job status:**
   - `lint-and-test` should show pytest failure (intentional)
   - `build-and-push` should still run (because `continue-on-error: true`)
3. **Build logs:**
   - Docker image build output
   - Image pushed to ghcr.io with SHA tag + latest tag
4. **Image verification:**
   - Visit: https://github.com/lakshsharda/caw_assignment/pkgs/container/caw_assignment%2Flinkops-api
   - Should see image tagged with commit SHA and `latest`

### Next: Fix and Re-verify (Optional Demonstration)

To show full pipeline success without test failures:

```bash
# Edit the test file
# Change: assert 1 + 1 == 3
# To:     assert 1 + 1 == 2

# Or simply:
git checkout api/test_app.py  # Remove the test file

# Commit and push
git add api/test_app.py
git commit -m "test: remove intentional failure demo"
git push origin main
```

**Expected result:**
- All tests pass
- Docker image builds
- Image pushed to ghcr.io
- No build failures

---

## Verification Summary

### Module 1 Status: ✓ VERIFIED
- Real docker build successful
- Real container runs with healthcheck
- Non-root user confirmed
- Image size within limits
- All security hardening in place

### Module 2 Status: ⏳ PIPELINE EXECUTING
- GitHub Actions workflow configured correctly
- Code pushed to GitHub
- Pipeline should be running now
- Check GitHub Actions tab for real-time execution

### Evidence Location
- **Module 1:** `REAL_VERIFICATION_EVIDENCE.md` (Section 1)
- **Module 2:** GitHub Actions runs: https://github.com/lakshsharda/caw_assignment/actions
- **Code:** https://github.com/lakshsharda/caw_assignment

---

**Generated:** August 7, 2026
**Status:** Real verification in progress - Docker Desktop confirmed working, GitHub pipeline executing
