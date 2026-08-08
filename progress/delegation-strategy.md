# AI Delegation Strategy Decision: AI-Augmented Engineering Module 01

## Decision: Hybrid Approach (Task-by-Task for complex interconnected work, Autopilot for isolated tasks)

## Reasoning

### The Situation
- **Unfamiliar codebase**: Team Collaboration product is new to me
- **Complex feature**: touches auth, data model, endpoints, notifications, audit logs
- **High interdependency**: each piece depends on decisions from the previous piece
- **Production risk**: invites must be secure (no replay attacks), role enforcement must be explicit everywhere

### Why Hybrid, Not Pure Autopilot or Pure Task-by-Task

**Against Full Autopilot:**
- A bad assumption in the data model (e.g., "invites are tied to user_id, not email") cascades through endpoint design, security logic, and notification handlers
- Discovering this after 500 lines of code means reworking 8 interconnected tasks
- This session has been a live case study in how confident-sounding code can hide wrong assumptions until you test it (Bug #4, fake REFLECT files, hardcoded Docker ports)
- On a completely unfamiliar codebase, autopilot is trading speed for hidden defects

**Against Pure Task-by-Task:**
- Overkill for truly isolated work (e.g., adding a helper utility function once patterns are clear)
- Slows down momentum once we understand the codebase conventions
- After the first 3-4 tasks establish patterns, additional tasks in the same system can move faster

**For Hybrid:**
- **Phase 1 (Task-by-Task):** Data model → invite endpoints → security checks → notification pattern
  - Each decision is small enough to verify (30-50 lines, not 500)
  - Each review catches assumptions before they compound
  - By task 4, we understand the codebase patterns
  
- **Phase 2 (Autopilot for isolated work):** Once patterns are clear, isolated features (new audit event types, helper functions) can be generated and reviewed as complete units

### Applied from This Bootcamp
1. **Verification discipline**: The Dockerfile was treated as correct from reading alone until tested for real (Module 1). The .env precedence was assumed until tested directly (Module 3). Bad assumptions found late are expensive fixes.
2. **Small reviewable chunks**: The entire BUILD phase of this bootcamp used small, reviewable increments — same principle applies to AI output.
3. **Cascading failures**: Module 2 CI/CD taught that one broken step cascades through the pipeline. Data model errors cascade through everything built on top.

### Cost Analysis
- Task-by-Task for 8 pieces of interconnected work: ~10 review cycles, ~8 hours of work total
- Full Autopilot with hidden defect discovered after 4 tasks: 1 review cycle that misses the bug, + ~12 hours rewriting 4 tasks + rework = 13-14 hours total
- Hybrid (4 task-by-task + 4 autopilot): ~6-7 review cycles, ~6-7 hours total

**Hybrid is both faster AND safer than pure autopilot for this scenario.**

## Implementation
- First 4 tasks: Team Collaboration invite feature (data model, endpoints, security, notifications) — Task-by-Task
- Tasks 5+: Audit events, utility functions, isolated additions — Autopilot after patterns established
- Review gate: If any task reveals new system behavior, revert to Task-by-Task for dependent work
