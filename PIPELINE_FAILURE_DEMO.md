# Pipeline Failure Demonstration

## Scenario 1: Test Failure → Build Blocked (Just Pushed)

**Commit:** `ci: remove continue-on-error to properly gate build on test failures`

**What's happening NOW:**
1. Workflow runs with `continue-on-error: true` **REMOVED**
2. Test file still contains intentional failure: `assert 1 + 1 == 3`
3. Pipeline executes in this order:
   - **lint-and-test job**: Runs linter → runs pytest
   - pytest finds the failing test
   - Job status: ❌ FAILED
   - **build-and-push job**: Blocked (needs: lint-and-test failed)
   - Build step: ⏭️ SKIPPED
   - No Docker image pushed

**Expected GitHub Actions Output:**
```
✓ Checkout code
✓ Set up Python 3.12
✓ Install dependencies
✓ Run linter (ruff) - PASS
✗ Run tests - FAIL

Failed test output:
  def test_intentional_fail():
>       assert 1 + 1 == 3
E       AssertionError: Math works (intentional fail for pipeline demo)

⏭️ Build and Push job: SKIPPED (previous job failed)
```

**Watch it:** https://github.com/lakshsharda/caw_assignment/actions

---

## Scenario 2: Fix Test → Build Succeeds (Next Step)

After you see the failed run, we'll:

1. Fix the test: `assert 1 + 1 == 2`
2. Commit and push
3. Pipeline runs again:
   - **lint-and-test job**: ✓ PASS (all tests pass)
   - **build-and-push job**: ✓ EXECUTES (needs condition satisfied)
   - Docker image builds
   - Image pushed to ghcr.io with SHA + latest tags

---

## Key Differences from Previous Run

### Before (continue-on-error: true)
```
Job status: ✓ PASSED (despite test failing)
Build-and-push: ✓ EXECUTED (incorrectly)
Image: ✓ Pushed to registry (shouldn't have)
```
❌ **Wrong behavior** - Pipeline should catch failures

### Now (continue-on-error removed)
```
Job status: ✗ FAILED (correctly identifies test failure)
Build-and-push: ⏭️ SKIPPED (correctly blocked)
Image: ❌ NOT pushed (correct behavior)
```
✓ **Correct behavior** - Pipeline gates properly

---

## Next Actions

1. **Check GitHub Actions:** https://github.com/lakshsharda/caw_assignment/actions
   - Look for the most recent run (should be ~1-2 minutes old)
   - Confirm lint-and-test shows RED X (failed)
   - Confirm build-and-push shows SKIPPED

2. **View detailed logs:**
   - Click the failed run
   - Expand "Run tests" step
   - See the actual pytest failure output

3. **Then fix the test:**
   ```bash
   # Edit api/test_app.py
   # Change: assert 1 + 1 == 3
   # To:     assert 1 + 1 == 2
   
   git add api/test_app.py
   git commit -m "test: fix assertion to 1 + 1 == 2"
   git push origin main
   ```

4. **Watch the second run succeed:**
   - All tests pass
   - Docker image builds
   - Image pushed to ghcr.io
   - Full green checkmarks

---

**Generated:** August 7, 2026
**Status:** Waiting for pipeline execution
**Monitor:** https://github.com/lakshsharda/caw_assignment/actions
