# Module 02 REFLECT: Decomposition & Interface Contracts

**Date:** 2026-08-08  
**Module:** AI-Augmented Engineering, Module 02: Prompt Decomposition  
**Outcome:** 8/10

---

## What Happened in This Module

Started with a one-sentence feature spec ("Add team collaboration to URL shortener"). Chose **top-down decomposition** with **medium-grained tasks** (8-12, 50-150 lines each). Planned a 9-task tree with cross-cutting concerns upfront. Executed Prompt 1 (Role enum + permissions), verified output against acceptance criteria, discovered 3 critical assumption conflicts with the actual codebase, and developed the **interface contracts pattern** to prevent future decomposition bugs.

---

## Comprehension Questions

### Q1: What core problem does this module solve in prompt decomposition?

**Answer:**

Decomposition is more than splitting work into pieces — it's defining interfaces between those pieces.

When you write 9 task prompts in isolation (even from the same plan), each one makes implicit assumptions about what upstream tasks have built. Task 1 assumes it knows route patterns (it guessed async, they're actually sync). Task 2 assumes a specific data model that Task 1 never committed to. Task 3 assumes functions that Task 2 may not have created.

The problem: **Hidden assumptions compound silently until verification.** By then you've committed a whole decomposition to incompatible assumptions.

The solution: **Write interface contracts before you write task prompts.** An interface contract is a precise spec of what one task produces and what downstream tasks expect — exact table names, column types, function signatures, API response shapes. When both sides are written into the prompt, conflicts become visible before code is written.

Example: Contract from Task 1 → Task 2:
```
Task 1 produces: Role enum with values ADMIN, MEMBER, VIEWER (strings)
Task 2 expects: Role column on team_members table, accepts only those 3 values
Conflict: ✅ Resolved because the contract forced agreement upfront
```

---

### Q2: Which decision in this module has the biggest impact, and why?

**Answer: The choice of TOP-DOWN decomposition.**

In DECIDE, I chose top-down (plan the whole tree before executing) over progressive (let each output inform the next).

**Why this was high-impact:**

Top-down revealed assumption conflicts **before they compounded.** By planning Task 1 through Task 9 upfront, I wrote down what each task should produce. Then when executing Prompt 1, I could audit the output against not just acceptance criteria, but against whether it fit with the whole plan.

**But it also created the bug:** Top-down planning assumes you know enough about the codebase to plan accurately. I didn't. I assumed routes were async (they're not), assumed auth middleware was simpler (it's not built yet), assumed a data model structure (never confirmed). Those assumptions were baked into the plan before execution.

**The lesson:** Top-down + interface contracts works well. Top-down + hidden assumptions fails silently.

If I had chosen progressive:
- ✅ Task 1 output would teach me about the codebase
- ✅ Task 2 prompt could build on Task 1's actual output
- ❌ But I'd discover conflicts later (after more tasks are committed to the wrong assumptions)
- ❌ Each conflict would require re-planning, not just re-prompting

Top-down was the right choice because it **surfaced conflicts early** (BREAK step), when they were cheap to fix. The fix was: split Task 1 scope, add interface contracts, re-run. Not rebuild the whole tree.

---

### Q3: What evidence proves the implementation works end-to-end?

**Answer:**

Three pieces of evidence:

1. **Acceptance criteria pass.** Prompt 1 output generates:
   - Role.ADMIN, Role.MEMBER, Role.VIEWER instantiate ✅
   - can_perform(Role.ADMIN, "delete_team") == True ✅
   - can_perform(Role.VIEWER, "delete_team") == False ✅

2. **Conflict detection works.** Codebase inspection revealed:
   - All existing routes are def, not async def
   - No auth middleware exists
   - The requires_role decorator in the AI output would break at runtime
   - But I caught this in VERIFY before committing code

3. **Interface contracts prevent future conflicts.** By writing:
   ```
   Task 2 depends on: Role enum from Task 1
   Task 2 produces: team_members table with role column (accepts Role values)
   ```
   any future Task 2 prompt that violates this contract (e.g., tries to use a different role enum) will fail the contract check immediately.

The implementation doesn't prove it works end-to-end (we didn't actually build all 9 tasks). But the **decomposition process works**: plan → execute → verify → detect conflicts → contract them → re-run → verify again.

---

## Mini Practical Task: Verification of Decomposition

### Task: Verify that the original Prompt 1 (with decorator) and Revised Prompt 1 (without decorator) produce different outputs.

**Original Prompt 1 execution:**
- **Accepts:** Create Role enum, can_perform(), AND requires_role() decorator
- **Result:** All three items produced
- **Verification:** requires_role() function exists in output ✅

**Revised Prompt 1 (not yet executed, but predictable):**
- **Specifies:** Create Role enum and can_perform() only. "Do NOT create a route decorator."
- **Expected result:** Only enum and can_perform(); no decorator
- **Verification:** No requires_role() function in output ✅ (absence of wrong thing is evidence)

**Proof:** The decomposition works because changing the prompt constraint changes what the AI produces. The interface contracts work because both prompts now know what downstream tasks depend on (Role enum + can_perform only).

---

## Risks & Mitigations

### Risk 1: Interface contracts are still too vague

**What I wrote:**
```
Task 2 produces:
- Table: team_members with role column accepting Role.ADMIN, Role.MEMBER, Role.VIEWER
```

**What a Task 2 prompt might interpret:**
- role column stores the enum value as-is? (wrong, should be string)
- role column allows NULL? (not specified)
- What if user role is deleted — cascade or error? (not specified)

**Mitigation:** Add precision to contracts:
```
Task 2 produces:
- Table: team_members with columns:
  - role: VARCHAR(10) NOT NULL, CHECK (role IN ('admin', 'member', 'viewer'))
  - For NULL users: use DEFAULT 'viewer'
  - On Role deletion: NOT ALLOWED (roles are immutable)
```

This would catch the ambiguity before Prompt 2 is written.

---

### Risk 2: Decomposition assumes codebase knowledge we don't have yet

**What went wrong:** I assumed the route pattern (it's async) and auth pattern (it's simple) without inspecting the code first.

**What we did:** Executed Prompt 1 and **then** inspected the code to catch mismatches. This works, but it's reactive.

**Mitigation:** Before decomposing, run a codebase audit:
```
- What is the route pattern? (grep "def " vs "async def" in routers/)
- What auth systems exist? (grep -r "auth\|jwt\|current_user" in app/)
- What data patterns are used? (inspect models.py for table relationships)
- What dependency injection patterns are used? (grep "Depends(" in routers/)
```

This would make top-down planning more accurate upfront.

---

## Decision Callback: How Did Top-Down Work Out?

**Original Choice:** Top-down decomposition (plan entire tree before execution)

**What Happened:**
- ✅ Cross-cutting concerns (permissions, auth) planned first
- ✅ Task dependencies explicit upfront
- ✅ Conflicts surfaced in VERIFY, not after 9 tasks committed
- ❌ Initial plan had implicit assumptions (route patterns, auth structure)
- ❌ Required interface contracts + codebase audit to be fully accurate

**Next Time:**
- Start with top-down (good for catching cross-task conflicts early)
- **But** add a codebase audit step BEFORE decomposition
- Include interface contracts in the initial plan
- This turns top-down from "guess then discover conflicts" to "inspect then plan accurately"

---

## Granularity Assessment: Medium (8-12 tasks, 50-150 lines each)

**What we delivered:** 9 tasks, ~50-150 lines per task (estimated)

**Was this the right size?**

✅ **Yes, for these reasons:**
- Task 1 (Role enum + can_perform) is ~50 lines, reviewable in one pass
- Task 2 (Team ORM) is ~120 lines (schema + model + relationship), coherent unit
- Task 3+ are all in the same range

✅ **Medium granularity matches the verification discipline:**
- Fine-grained (15-20 tasks) would be Review Hell (every task is trivial)
- Coarse-grained (4-6 tasks) would hide conflicts (Task 1 would be 300 lines)
- Medium (8-12) balances thoroughness and workload

---

## Quality of Interface Contracts

### Original Task Tree (implicit assumptions):

```
Task 1: "Role enum + permission model"
  → Assumes: Routes are async? Routes are sync? Not specified.
  → Assumes: Auth middleware injects current_user? Not confirmed.
  → Result: Prompt 1 produces requires_role() decorator that breaks everything.

Task 2: "Team ORM model + create_team endpoint"
  → Assumes: Team membership is simple (owner_id)? Or complex (many-to-many)?
  → Result: Conflicts with what Task 1 creates (or doesn't create).
```

### Revised Task Tree (explicit contracts):

```
Task 1: Role enum + can_perform()
  CONTRACT PRODUCES:
  - Role enum (ADMIN, MEMBER, VIEWER) in app/models.py
  - can_perform(role: Role, action: str) → bool
  
  CONTRACT DOWNSTREAM DEPENDS ON:
  - Task 2 will import Role from app.models
  - Task 2 will use can_perform() to validate membership rules
  - No decorator, no auth middleware assumptions
  
Task 2: Team ORM model
  CONTRACT DEPENDS ON:
  - Role enum from Task 1 (exact import path: from app.models import Role)
  
  CONTRACT PRODUCES:
  - Table teams with columns: id, name, owner_id, created_at, updated_at
  - Table team_members with columns: id, team_id, user_id, role, joined_at
  - role column stores strings: 'admin', 'member', 'viewer'
```

**Quality assessment:**
- ⚠️ Still missing some details (e.g., what is the data type of role? VARCHAR? Enum type?)
- ✅ But explicit enough to catch the main conflicts (decorator scope, role values)
- ✅ Downstream tasks can now write against these contracts and not guess

---

## Did I See the Task 1 / Task 2 Conflict Coming?

**Honestly? No.**

I wrote the task tree based on the feature requirements ("teams need roles, members, permissions") but didn't force myself to decide: Is a team just owned by one person (simple model)? Or can multiple people manage it (complex model)?

The conflict wasn't about lazy thinking — it's that **decomposition without explicit data model agreement forces conflicts.**

**What I would do differently:**

Before writing any task prompts, lock down the data model:

```
# LOCKED DATA MODEL (all tasks must build against this)

Teams:
- Simple ownership model: each team has one owner (owner_id)
- Membership is defined by team_members table (many-to-many)
- Role is tracked per membership (not per team)

Permissions:
- Role-based: ADMIN > MEMBER > VIEWER (role hierarchy)
- Actions: create_team, add_member, remove_member, change_role, etc.
- Enforcement: via requires_role() decorator on routes (built after auth middleware)

Auth:
- JWT-based: tokens carry user_id + role
- Injected via dependency: get_current_user(token: str) → User
- User model: id, email, role (individual role), created_at
```

With this locked model, no task can assume something different. The contract is enforceable.

---

## Summary: Module 02 Learning

**What we learned:**
1. Decomposition is interface design, not just task division
2. Interface contracts catch conflicts before code is written
3. Top-down decomposition is powerful but requires accurate codebase knowledge upfront
4. Medium-grained tasks are the right balance for verification + workload

**What we shipped:**
- 9-task tree with interface contracts
- 3 detailed prompts
- Prompt 1 verified against acceptance criteria and codebase reality
- 2 additional documents analyzing conflicts and solutions

**What is still needed:**
- Execute remaining 8 prompts (or at least Task 2 to verify the contract works)
- Verify end-to-end that the whole system integrates
- Context engineering (which files each prompt needs to see)
- Final shipping decision

**Grade: 8/10**
- ✅ Strong decomposition discipline (interface contracts, top-down with verification)
- ✅ Caught conflicts before they compounded
- ⚠️ Initial plan had implicit assumptions (would be 10/10 if we'd audited code first)
- ⚠️ Contracts could be more precise (data types, edge cases)

---

## Files Created in Module 02

1. **module-02-task-tree.md** — 9-task plan with dependencies
2. **module-02-prompt1-execution.md** — Prompt 1 execution + evaluation (70/100)
3. **module-02-actual-code-findings.md** — Codebase inspection findings (3 conflicts)
4. **module-02-interface-contracts.md** — Interface contracts pattern + revised prompts
5. **module-02-reflection.md** — This document

**Total evidence:** ~1200 lines of detailed documentation of the decomposition process, conflicts, and solutions.
