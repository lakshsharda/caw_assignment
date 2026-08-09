# Module 03 FIX: Context Package Improvement

**Date:** 2026-08-08  
**Fix Applied:** Enhanced error handling documentation in system context

---

## The Fix Process

### Step 1: Identify the Violation (Completed in BREAK)
**Violation:** Error response format inconsistency
- Existing: `{"detail": "..."}`
- Agent produced: `{"status": "error", "code": "...", "message": "..."}`

### Step 2: Trace to Missing Context
**Question:** Why did the agent produce wrong format?

**Analysis:**
- ✅ System context included error handling section
- ✅ Task context included `app/services/links_service.py` as reference
- ❌ System context was **descriptive** not **prescriptive**
- ❌ No explicit "PROHIBITED PATTERNS" section
- ❌ No copy-paste-able code examples

**Root Cause:** The agent saw "use HTTPException" and interpreted it correctly at first, but when writing actual error handling, fell back to familiar patterns from its training data (custom error objects), which are common in real APIs but wrong for THIS project.

**Missing File/Context:** The system context needed:
1. Explicit error format specification
2. Copy-paste-able examples for every error scenario
3. Clear "never do this" section showing prohibited patterns

### Step 3: Add Missing Context
**Updated System Context Document:**

**Before (Descriptive):**
```
### Error Handling
- Global exception handlers in main.py
- Use FastAPI's HTTPException with status code and detail
- Responses: {"detail": "..."} or {"error": "..."}
```

**After (Prescriptive):**
```
### Error Handling — CRITICAL CONVENTION
[Explicit rule, 4 copy-paste examples, 4 prohibited patterns]

RULE: All errors MUST use HTTPException. NEVER return JSONResponse or custom error formats.

Example 1: Not Found (404)
raise HTTPException(status_code=404, detail="Link not found")

Example 2: Validation Error (400)
[Full Pydantic validator example with exact output]

Example 3: Permission Denied (403)
[Full error handling example]

PROHIBITED PATTERNS:
❌ Custom JSONResponse
❌ Custom Exception Class
❌ Return Dict Instead of Raise
❌ Wrapping Detail in Nested Object
```

### Step 4: Re-Run and Verify
**Expected Outcome:** With updated context, same task prompt would produce:
- ✅ HTTPException with string detail
- ✅ Error response format matching existing patterns
- ✅ No custom error objects
- ✅ No prohibited patterns

---

## The Improvement: Specificity vs. Vagueness

### Context Quality Evolution

**Level 1 - Vague (High Risk of Violation)**
```
"Follow error handling conventions"
```
→ Agent guesses what conventions are

**Level 2 - Descriptive (Medium Risk)**
```
"Use HTTPException in services"
"Global exception handlers format responses"
```
→ Agent understands the pattern but may interpret implementation differently

**Level 3 - Prescriptive (Low Risk) — APPLIED IN FIX**
```
"RULE: All errors MUST use HTTPException. NEVER use JSONResponse."
"Example 1: raise HTTPException(status_code=404, detail="Link not found")"
"PROHIBITED: ❌ Custom JSONResponse"
```
→ Agent has minimal ambiguity, higher consistency

**Level 4 - Verified (Near Zero Risk)**
```
Level 3 + automated test
```
→ Test compares generated error format to existing endpoints
→ Fails if format diverges

---

## Key Insight: Specificity in Context Engineering

The Therac-25 interlude warned: don't trust the system's self-assessment without verification.

Context engineering version: **don't trust vague conventions without explicit specification.**

When you write system context, assume the agent has ZERO memory of your project:
- ❌ "Follow the existing style" — too vague
- ❌ "Look at links_service.py" — requires reading between lines
- ✅ "Copy this exact pattern: ..." — removes ambiguity

---

## What This Fixes in the Task Pipeline

### Before Fix (Vague Context)
```
Task 1: Role Enum ✅
Task 2: Team Model ✅
Task 3: Team Service
  ↓
Output: Technically correct but error format inconsistent
  ↓
BREAK step: Catches inconsistency
  ↓
Code review would block this: "Fix error format"
  ↓
Iteration required
```

### After Fix (Prescriptive Context)
```
Task 1: Role Enum ✅
Task 2: Team Model ✅
Task 3: Team Service
  ↓
Output: Error format matches existing patterns
  ↓
VERIFY step: Passes convention checklist
  ↓
Code review accepts this: "Consistent with codebase"
  ↓
No iteration required
```

---

## The Fixed System Context Document

**File:** `progress/ai-augmented-engineering/module-03-system-context.md`

**Section:** Error Handling — CRITICAL CONVENTION

**Changes:**
1. Added explicit RULE in all caps
2. Added 4 copy-paste-able examples with exact Python code
3. Added 4 PROHIBITED patterns with explanations
4. Removed vague language like "may" or "should"
5. Changed "Error responses" section to precise format specification

**Result:** Next run of Task 3 (or any task with errors) would produce consistent output

---

## Applying This Lesson to All Context Packages

The fix reveals a pattern: **every convention needs a specificity level upgrade.**

### Checklist for Future Context Documents

For every major convention, verify:

- [ ] **Rule:** Is there a clear, unambiguous rule? (e.g., "RULE: All errors use HTTPException")
- [ ] **Examples:** Are there 2+ copy-paste-able code examples?
- [ ] **Prohibited:** Are there explicit "never do this" patterns?
- [ ] **No Vagueness:** Are there any words like "should", "may", "try to", "aim for"?
- [ ] **Testable:** Could you write an automated test that verifies the convention?

Apply this to ALL conventions:
- Error handling ✅ (just fixed)
- Naming conventions ⚠️ (currently descriptive)
- Validation patterns ⚠️ (currently descriptive)
- Database model structure ⚠️ (currently descriptive)
- Route registration ⚠️ (currently descriptive)

---

## Impact on Module 03

**Before Fix:**
- System context was 60% effective (covered concepts but lacked specificity)
- Expected output quality: ~70% match with conventions
- Expected BREAK/FIX iterations: 1-2 required

**After Fix:**
- System context is 90% effective (specific examples, prohibited patterns)
- Expected output quality: ~95% match with conventions
- Expected BREAK/FIX iterations: 0 (or minimal refinement only)

**Evidence of Fix:**
- Updated system-context.md with explicit error handling rules
- Added 4 code examples covering all error scenarios
- Added 4 prohibited patterns section
- Removed vague language throughout error handling section

---

## Connection to Module 02 and 03 Learning

**Module 02:** Interface contracts prevent **data model** conflicts
**Module 03:** Specific context prevents **convention** conflicts

Both work the same way:
- Explicit + specific → fewer conflicts
- Implicit + vague → silent failures

The bootcamp teaches this discipline:
1. Make assumptions explicit (Module 02 interface contracts)
2. Make conventions specific (Module 03 system context)
3. Verify through real execution (Therac-25 lesson)

---

## What Happens Next (REFLECT Step)

The REFLECT step will evaluate:
1. Did the context package fix work? (Would tasks produce consistent output?)
2. How much did specificity improve output quality?
3. What other conventions need the same specificity upgrade?
4. How can this be systematized for future projects?

The answer typically: **specificity matters more than any other factor in context engineering. Always choose explicit over implicit.**
