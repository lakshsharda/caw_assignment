# SkillSwap Contradiction Resolution - Module 01 FIX

**Module:** Decomposition & Execution Planning, Module 01 FIX  
**Date:** 2026-08-09  
**Issue:** Specification contradiction on cancellation policies

---

## The Contradiction

**Original Paragraph 2 (Provider-facing):**
> "Providers should be able to flag no-show users. There's a vetting process for new providers before they go live."
> AND implicitly: Providers can set their own cancellation policies

**Updated Paragraph 1 (User-facing) — Clarification:**
> "All cancellations made within 24 hours of booking receive a full refund, regardless of the reason. Cancellations after 24 hours are non-refundable."

**Conflict:** These two statements cannot both be true as stated.
- Statement A: Providers have autonomy to set their own cancellation policies
- Statement B: Platform enforces universal cancellation rule (full refund if <24h, none after)

**Question:** When they conflict, which takes precedence? Can a provider be MORE generous than the platform rule?

---

## Two Concrete Resolution Options

### Option 1: Platform-First Cancellation (Simplicity over Provider Autonomy)

**Description:**
The platform enforces a universal cancellation policy that applies to ALL bookings, regardless of provider. No provider exceptions.

**Policy Rule:**
- Full refund if canceled within 24 hours of booking time
- No refund if canceled 24+ hours after booking
- Refund initiated automatically by the platform on cancellation
- This policy is displayed to learners at booking time (non-negotiable)

**Who It Affects:**
- Learners: Clear, consistent experience. No surprises.
- Providers: Cannot set their own policies. Lost autonomy but simpler operations.
- Platform: Simpler refund logic, one code path.

**Tradeoffs:**
- ✅ Pros: Single, consistent user experience. Easier to build. Easy to explain.
- ❌ Cons: Removes provider flexibility. Hurts providers of same-day services (24-hour cancellation window may not make sense). Providers who want stricter policies cannot enforce them.

**Implementation Complexity:** Low (one policy, automatic refund on cancellation, no conditional logic)

**Blocked Requirements (if this option chosen):**
- Provider autonomy over cancellation policy (P.F.4) — REMOVED
- Display provider policy to learner before booking — REMOVED
- Requirement L.F.6 becomes: "Cancel bookings with automatic full refund within 24 hours"

---

### Option 2: Provider Policy with Platform Floor (Autonomy + Protection)

**Description:**
Providers set their own cancellation policies (customizable rules per provider), BUT the platform enforces a MINIMUM protection: all users get a full refund if they cancel within 1 hour of booking, regardless of provider policy (a "cooling off" period). Beyond the 1-hour window, the provider's policy applies.

**Policy Rule:**
- Mandatory: Full refund if canceled within 1 hour (platform floor, non-negotiable)
- Provider-set: Refund rules for cancellations after 1 hour (e.g., "50% refund if canceled within 24 hours, no refund after")
- Refund logic: Check if cancellation is within 1 hour (automatic full refund), else check provider policy
- Provider policy must be clearly displayed to learner before booking

**Who It Affects:**
- Learners: Get a safety net (1-hour cooling off period). After that, depend on provider.
- Providers: Keep autonomy over cancellation terms. Can be stricter or more flexible. Must define and communicate their policy.
- Platform: Moderate complexity (two-tier refund logic + provider policy storage/display).

**Tradeoffs:**
- ✅ Pros: Preserves provider autonomy. Gives learners a safety net. Supports providers who need stricter policies (same-day services). Fair to both sides.
- ❌ Cons: More complex to implement and test. Users must read provider policies (not all do). Providers must manage and communicate their policies. More potential for disputes.

**Implementation Complexity:** Medium (two-tier refund logic, provider policy CRUD, display on booking page, provider dashboard for managing policies)

**Blocked Requirements (if this option chosen):**
- None. All original requirements remain. This option integrates provider autonomy (P.F.4) with user protection.

---

## Related Requirements Affected by This Decision

### Payment Flow (L.F.4, P.F.8)
- **Option 1:** Payment captured at booking. On cancellation <24h, automatic full refund. Simple flow.
- **Option 2:** Payment captured at booking. On cancellation, check provider policy. Refund amount varies. Complex flow with conditional logic.

### Provider Earnings Dashboard (P.F.6)
- **Option 1:** Earnings = booking price - 15% commission, always. Predictable for provider.
- **Option 2:** Earnings = booking price - 15% commission - refund amount. Requires refund projection based on when cancellation happened. Trickier to display.

### Dispute Resolution (P.F.9, PL.F.2)
- **Option 1:** Few disputes (policy is universal, clear). Platform owns refund decision.
- **Option 2:** More disputes (provider policies vary). Disputes often about "did the provider's policy apply correctly?" Requires platform to arbitrate provider policy interpretation.

### Provider Onboarding / Vetting (P.C.1)
- **Option 1:** Vetting focuses on provider legitimacy. No cancellation policy to review.
- **Option 2:** Vetting includes reviewing/approving provider's proposed cancellation policy. Adds step to provider approval process.

### Analytics / Reporting (PL.F.4)
- **Option 1:** Simple: refund rate is always 100% for <24h cancellations. Predictable.
- **Option 2:** Complex: refund rate varies by provider. Analytics need to segment by provider policy and compare to platform floor.

---

## My Recommendation (Senior Engineer Perspective)

**Recommend: Option 2 (Provider Policy with Platform Floor)**

**Reasoning:**
1. **Marketplace viability:** Real marketplaces succeed when providers feel they have autonomy (within guardrails). A universal platform policy feels like the platform does not trust providers, which builds resentment.

2. **Same-day services:** SkillSwap will eventually attract same-day services (tutoring, fitness, etc.). A 24-hour cancellation window is unrealistic. Providers need flexibility.

3. **User protection:** The 1-hour cooling-off period protects learners from impulsive bookings while respecting provider autonomy beyond that. It's a fair compromise.

4. **Competitive advantage:** Marketplaces that allow provider customization (within bounds) often outcompete those with one-size-fits-all policies.

5. **Scalability to 5 cities:** Different cities may have different norms (e.g., some cities have strong consumer protection laws requiring longer cooling-off periods). Option 2 scales to regional variation better than Option 1.

**Caveat:** This requires strong provider communication during onboarding. If providers misunderstand or do not communicate their policies clearly, disputes will skyrocket. Mitigate by:
- Provide default policy template
- Require explicit policy review during vetting
- Show provider policy prominently on all booking pages
- Log when learner viewed the policy (for dispute proof)

---

## Next Actions

### For PM (Immediate)
1. Choose Option 1 or Option 2 (or propose a third option based on this framework)
2. If Option 2, define: What is the exact cooling-off period? (1 hour? 30 minutes? 1 day?) More generous = more disputes; too short = fewer bookings.
3. If Option 2, provide default cancellation policy template for providers

### For Engineering (After PM Decision)
1. Update requirements document with the chosen option
2. Flag all affected requirements (payment flow, dashboard display, vetting process, etc.)
3. Design the refund logic state machine
4. Plan provider policy CRUD + validation
5. Plan dispute workflow

### For Requirements Document (Now)
- Mark **P.F.4** (Provider: "Define own cancellation policy") as **BLOCKED - Pending PM Decision**
- Mark **L.F.6** (Learner: "Cancel with refund") as **BLOCKED - Pending PM Decision** (logic depends on chosen policy)
- Cross-reference this contradiction document

---

## Bonus: Other Tensions Found During Analysis

### Tension 1: Scale vs Provider Autonomy

**Requirement:** "Handle at least a few thousand users" (PL.C.3) AND "Providers set their own availability" (P.F.2)

**The Tension:** If a popular provider opens their calendar to 1000 available slots, and 50,000 users try to book the same slot simultaneously, what happens?
- Provider autonomy suggests: "Slots are just slots, first-come-first-served"
- Scale requirement suggests: "We need queue-based booking, optimistic locking, or reserved capacity"

**Why It Matters:** Affects database design (transactions vs event streams), user experience (instant confirmation vs "we'll notify you if this slot opens"), and provider trust ("why can't I see all my bookings instantly?")

**Need to Ask PM:** Should we expect provider calendars to get that hot? Is it even a realistic scenario for SkillSwap, or are we over-engineering?

---

### Tension 2: "Analytics on Everything" vs Observability Simplicity

**Requirement:** "Analytics on everything" (PL.Q.3) AND reasonable system complexity

**The Tension:** "Everything" could mean:
- Light: Page views, bookings, cancellations (a week of work)
- Heavy: Full user funnel, provider performance, revenue cohorts, A/B testing, real-time dashboards (months of work)

**Why It Matters:** Affects infrastructure (logging, event streaming, data warehouse), budget, and time to launch.

**Need to Ask PM:** What are the TOP 3 metrics that matter most for business decisions? Start there, not with "everything."

---

## Summary

- **Contradiction Found:** Provider autonomy vs platform-enforced universal cancellation policy
- **Options Proposed:** Two concrete, buildable choices with tradeoffs
- **Recommendation:** Option 2 (Provider Policy with Platform Floor) for marketplace viability
- **Affected Requirements:** Payment flow, earnings dashboard, dispute resolution, vetting, analytics
- **Other Tensions:** Scale vs autonomy, analytics scope
- **Blocker Status:** P.F.4 and L.F.6 flagged as BLOCKED pending PM decision
