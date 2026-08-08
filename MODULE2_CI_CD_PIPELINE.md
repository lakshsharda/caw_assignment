# Module 2: CI/CD Pipeline - GitHub Actions Workflow

## Pipeline Created
File: `.github/workflows/ci.yml`

## Design Decisions
1. **CI Platform**: GitHub Actions
   - Reasoning: Industry standard, massive action ecosystem, portable YAML skills
   
2. **Pipeline Shape**: Sequential (jobs chained, not parallel)
   - Lint and test run in same job
   - Docker build only runs if lint/test succeed
   - Push only runs if build succeeds and on main branch

## Pipeline Structure

### Job 1: lint-and-test
Runs on: `ubuntu-latest` with Python 3.12
Steps:
1. Checkout code
2. Set up Python (with pip caching)
3. Install dependencies from requirements.txt
4. Run linter: `ruff check .` (checks code style)
5. Run tests: `pytest` (tests API endpoints)

Timeout: 15 minutes
Success condition: Both lint and test pass

### Job 2: build-and-push
Depends on: `lint-and-test` (waits for its success)
Triggers: Only on `main` branch, on `push` events (not on PRs)
Steps:
1. Checkout code
2. Set up Docker Buildx (efficient multi-stage builds)
3. Build Docker image with git SHA tag
4. Check image size (must be <200MB, fails otherwise)
5. Log in to GitHub Container Registry (ghcr.io)
6. Push image with two tags:
   - `ghcr.io/.../linkops-api:<git-sha>` (commit-specific tag)
   - `ghcr.io/.../linkops-api:latest` (mutable tag for convenience)
7. Log image details for confirmation

Timeout: 15 minutes
Permissions: Read repository content, write to package registry
Registry: GitHub Container Registry (ghcr.io)

## Key Features

### Chunk 1: Lint and Test
- **Triggers on**: Every push to main AND every PR to main
- **Fails fast**: Lint runs first (cheap), tests second (expensive)
- **Feedback**: Developers see lint errors before waiting for full test suite

### Chunk 2: Docker Build
- **Triggered after**: Lint and test both pass
- **Artifact**: Docker image tagged with git commit SHA
- **Traceability**: Image tag = exact commit that built it
- **Size guardrail**: Fails if image exceeds 200MB (catches bloat)

### Chunk 3: Push to Registry
- **Only on main branch**: Feature branches don't pollute registry
- **Secret management**: Uses GitHub's built-in GITHUB_TOKEN (no hardcoded credentials)
- **Dual tags**: Both immutable (SHA) and mutable (latest) tags
- **Confirmation logs**: Prints image details for verification

### Chunk 4: Pipeline Hardening
- **Timeouts**: 15 minutes per job (prevents stuck builds burning free minutes)
- **Dependency caching**: Uses GitHub Actions cache@v4 for pip dependencies
  - Cache key: hash of requirements.txt
  - Saves 1-2 minutes on re-runs if requirements unchanged
- **Image size threshold**: Fails if >200MB (defense against bloat)
- **Explicit permissions**: Only reads code, writes to package registry

## Workflow Triggers
- **Push to main**: Runs full pipeline (lint → test → build → push)
- **Pull request to main**: Runs lint/test only (no build/push)
- **Path filtering**: Only triggers if `api/` or `ci.yml` changed (skips unnecessary runs)

## Testing the Pipeline

### Scenario 1: All steps pass
1. Make a commit to `api/` that passes linting and tests
2. Push to main branch
3. Expected: Lint → Test → Build → Push all succeed
4. Result: Image appears in ghcr.io with two tags (SHA + latest)

### Scenario 2: Lint failure (intentional drill)
1. Introduce a lint violation (unused variable, missing type hint, etc.)
2. Push to main
3. Expected: Lint fails, tests don't run, build doesn't run
4. Result: Pipeline stops, no image pushed
5. Fix the violation and repush
6. Expected: Full pipeline passes

### Scenario 3: Test failure (intentional drill)
1. Break a test (change assertion so it fails)
2. Push to main
3. Expected: Lint passes, test fails, build doesn't run
4. Result: Pipeline stops, no image pushed
5. Fix the test and repush
6. Expected: Full pipeline passes

### Scenario 4: Image size breach
1. Accidentally include large file in Docker image (e.g., test fixtures)
2. Push to main
3. Expected: Lint and tests pass, image build succeeds, but size check fails
4. Result: Pipeline stops at size check, no push
5. Fix by updating .dockerignore and repush
6. Expected: Image now <200MB, push succeeds

## Image Tagging Strategy

### Git SHA Tag: `ghcr.io/user/linkops-api:a1b2c3d4`
- Immutable: Never changes
- Traceable: Points to exact commit that built image
- Use in production: Pin exact version for stability
- Example: `ghcr.io/user/linkops-api:7f3a2e8c`

### Latest Tag: `ghcr.io/user/linkops-api:latest`
- Mutable: Points to most recent successful build
- Use in dev/staging: Always gets newest
- Warning: `latest` is a lie if you're not careful—enforce pipeline order to prevent old image getting tagged latest

## Registry: GitHub Container Registry (GHCR)
- Built into GitHub (free with account)
- Permissions tied to repository access
- Images private by default (aligned with private repo)
- Can be made public per-image
- Alternative registries: Docker Hub, GitLab Container Registry

## Next Steps
1. Push `.github/workflows/ci.yml` to main branch
2. GitHub automatically detects the workflow file
3. Next push to main triggers the pipeline
4. Watch: Settings > Actions > Workflows > CI/CD Pipeline to see runs
5. After first success, implement Module 2 VERIFY checks

## Known Limitation
The underlying `docker build` command is validated at pipeline execution time (when CI environment runs it), not locally. This means:
- Dockerfile design is correct (from Module 1)
- Actual docker build verification will happen when GitHub Actions runner executes the workflow
- Before production deployment, must confirm locally with Docker daemon running
