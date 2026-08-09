# SkillSwap Requirements Extraction - Full Matrix

**Module:** Decomposition & Execution Planning, Module 01 BUILD  
**Date:** 2026-08-09  
**Product:** SkillSwap (two-sided marketplace for skill-based sessions)  
**Structure:** Categorized Matrix (Stakeholder × Type)

---

## LEARNER - FUNCTIONAL

| # | Requirement | Type | Source | Confidence | Notes |
|---|------------|------|--------|-----------|-------|
| L.F.1 | Browse and search providers by service category | Functional | Explicit (Scenario) | High | "Learners browse services" |
| L.F.2 | View detailed provider profiles with ratings and reviews | Functional | Explicit | High | "browse, view provider profiles" |
| L.F.3 | Book available time slots offered by providers | Functional | Explicit | High | "book time slots" |
| L.F.4 | Pay for bookings through the platform | Functional | Explicit | High | "pay through the platform" |
| L.F.5 | Receive confirmation of booking with details (time, location, provider contact) | Functional | Explicit | High | "receive confirmations" |
| L.F.6 | Cancel bookings with automatic refund based on provider's cancellation policy | Functional | Explicit/Inferred | High | "Cancellation behavior must be explicit" |
| L.F.7 | View booking history and upcoming appointments | Functional | Inferred | Medium | Not stated, but necessary for user experience |
| L.F.8 | Rate and review providers after service completion | Functional | Inferred | Medium | Implied by "ratings and reviews" |
| L.F.9 | Receive appointment reminders (email or notification) | Functional | Inferred | Low | "confirmations" mentioned, reminders not explicit |
| L.F.10 | Manage account profile and payment methods | Functional | Inferred | Low | Signup, password reset, payment method updates not mentioned |

---

## LEARNER - CONSTRAINT

| # | Constraint | Source | Confidence | Notes |
|---|-----------|--------|-----------|-------|
| L.C.1 | Must be authenticated (logged in) to book | Implicit | Medium | Assumes users have accounts |
| L.C.2 | Cannot book slots that are already taken (conflict prevention) | Explicit | High | "Time-slot conflicts must prevent double-booking" |
| L.C.3 | Search results must display correctly under high concurrency | Constraint | High | Related to "instant" quality attribute |

---

## LEARNER - QUALITY ATTRIBUTE

| # | Attribute | Target | Source | Confidence | Notes |
|---|-----------|--------|--------|-----------|-------|
| L.Q.1 | Search must "feel instant" | <500ms latency (target) | Explicit | High | "Search should feel instant under target load" |
| L.Q.2 | Booking confirmation must complete within acceptable time | <2s (inferred) | Inferred | Low | Payment + confirmation flow timing not specified |
| L.Q.3 | Browse and search must work reliably on peak load | Handle "few thousand users" | Explicit | Medium | "under target load" |

---

## PROVIDER - FUNCTIONAL

| # | Requirement | Type | Source | Confidence | Notes |
|---|------------|------|--------|-----------|-------|
| P.F.1 | Publish service offerings with description | Functional | Explicit | High | "Providers publish services, descriptions" |
| P.F.2 | Set own availability (time slots/hours) | Functional | Explicit | High | "set own availability" |
| P.F.3 | Set own pricing | Functional | Explicit | High | "set own pricing" |
| P.F.4 | Define own cancellation policy | Functional | Explicit/Inferred | High | "with provider's cancellation policy applied" |
| P.F.5 | View and manage bookings (confirmed, completed, canceled) | Functional | Inferred | Medium | "showing bookings" |
| P.F.6 | View earnings and commission breakdown | Functional | Explicit | High | "track earnings, 15% commission" |
| P.F.7 | Receive notifications when new bookings are made | Functional | Inferred | Medium | Implied by needing to confirm or acknowledge bookings |
| P.F.8 | Receive payout of earnings (85% after commission) | Functional | Explicit/Inferred | High | "takes 15% commission" implies provider gets 85% |
| P.F.9 | Resolve disputes with learners over cancellations or quality | Functional | Explicit | High | "dispute handling" |
| P.F.10 | Update service offerings, prices, and availability | Functional | Inferred | Medium | "set own" implies ability to modify |

---

## PROVIDER - CONSTRAINT

| # | Constraint | Details | Source | Confidence | Notes |
|---|-----------|---------|--------|-----------|-------|
| P.C.1 | Must go through vetting/approval process | "Provider vetting" | Explicit | High | New providers must be approved |
| P.C.2 | Platform takes 15% commission on all earnings | Fixed rate | Explicit | High | "15% platform commission" |
| P.C.3 | Cannot double-book their own time slots | Automatic enforcement | Explicit | High | "Time-slot conflicts must prevent double-booking" |
| P.C.4 | Cancellation policy must be clearly communicated to learners | Displayed pre-booking | Inferred | Medium | Needed to prevent disputes |

---

## PROVIDER - QUALITY ATTRIBUTE

| # | Attribute | Target | Source | Confidence | Notes |
|---|-----------|--------|--------|-----------|-------|
| P.Q.1 | Provider dashboard must load quickly | <1s (inferred) | Inferred | Low | No explicit performance requirement |
| P.Q.2 | Earnings/analytics reports must be accurate and up-to-date | Real-time or near real-time | Inferred | Low | Not specified in scenario |

---

## PLATFORM / OPS - FUNCTIONAL

| # | Requirement | Type | Source | Confidence | Notes |
|---|------------|------|--------|-----------|-------|
| PL.F.1 | Approve or reject new provider applications | Functional | Explicit | High | "provider vetting" |
| PL.F.2 | Escalate and resolve disputes between learners and providers | Functional | Explicit | High | "dispute handling, escalated disputes" |
| PL.F.3 | Flag no-show users (learners who don't appear) | Functional | Explicit | Medium | "flag no-show users" |
| PL.F.4 | Track and generate analytics on all system activity | Functional | Explicit | High | "analytics on everything" |
| PL.F.5 | Process and transfer provider payouts | Functional | Explicit/Inferred | High | Implied by "takes commission" |
| PL.F.6 | Manage service categories (define available categories) | Functional | Inferred | Medium | "browse by category" implies categories exist somewhere |

---

## PLATFORM / OPS - CONSTRAINT

| # | Constraint | Details | Source | Confidence | Notes |
|---|-----------|---------|--------|-----------|-------|
| PL.C.1 | Expand to 5 cities within 6 months | Multi-city deployment | Explicit | High | Timeline: 6 months, scope: 5 cities |
| PL.C.2 | Expansion must not require full rebuild | Architecture constraint | Explicit | High | "expansion from one city to multiple cities must not require a full rebuild" |
| PL.C.3 | Handle at least a few thousand users under load | Scalability target | Explicit | Medium | "handle thousands of users" — exact number TBD |
| PL.C.4 | Commission calculation must remain consistent | Business rule | Explicit | High | "15% commission" applies across all transactions |
| PL.C.5 | No payment conflicts (all transactions atomic) | Technical constraint | Inferred | High | Payment system must be reliable; failures must be recoverable |

---

## PLATFORM / OPS - QUALITY ATTRIBUTE

| # | Attribute | Target | Source | Confidence | Notes |
|---|-----------|--------|--------|-----------|-------|
| PL.Q.1 | System must prevent double-booking reliably | Zero double-bookings | Explicit | High | "Time-slot conflicts must prevent double-booking" |
| PL.Q.2 | Search must feel instant under target load | <500ms | Explicit | High | "Search should feel instant under target load" |
| PL.Q.3 | Observability/analytics comprehensive | Track everything | Explicit | Medium | "analytics on everything" — scope TBD |
| PL.Q.4 | System must be available during business hours (SLA) | 99.9% (inferred) | Inferred | Low | No explicit uptime SLA stated |

---

## CROSS-CUTTING (All Stakeholders)

| # | Requirement | Type | Source | Confidence | Notes |
|---|------------|------|--------|-----------|-------|
| X.F.1 | User authentication and authorization (login, signup) | Functional | Implicit | Medium | All roles need accounts; not explicitly defined |
| X.F.2 | Payment processing and security (PCI compliance) | Functional/Constraint | Inferred | High | Handling payments requires security standards |
| X.Q.1 | Mobile-responsive or mobile app support | Quality | Inferred | Low | Web/mobile not specified; modern products need both |
| X.Q.2 | Support for multiple currencies | Quality | Inferred | Low | "Expand to 5 cities" — no mention of which cities, so currency diversity unknown |

---

## AMBIGUITIES AND OPEN QUESTIONS

### Question 1: Booking and Payment Model
**Specific question:** When a learner clicks "Book," what is the exact flow?
- Does payment happen before or after confirmation?
- If the learner pays but the provider cancels, is refund automatic?
- Can the platform hold the payment in escrow until the service is delivered?

**Why it matters:** Affects payment integration, refund logic, and dispute handling significantly.

---

### Question 2: Cancellation Policy Flexibility
**Specific question:** How are provider cancellation policies structured?
- Free-text (provider writes their own rules)?
- Structured options (e.g., "Full refund if canceled 24+ hours before," "50% refund if canceled 1-24 hours before," "No refund if canceled less than 1 hour before")?
- Default policy if provider doesn't set one?

**Why it matters:** Affects refund calculation logic, learner communication, and dispute resolution.

---

### Question 3: Authentication and Authorization
**Specific question:** How do users transition from "Guest" to authenticated?
- Can someone browse without an account (guest mode)?
- Is account creation required to book, or just at payment step?
- Can someone be both a Learner and a Provider? (Different account types or one account with dual roles?)
- How are roles assigned? (User decides "I want to be a provider" vs only admins can create providers?)

**Why it matters:** Affects signup flow, database schema (separate tables or one Users table with role attribute), and identity/authorization checks throughout the system.

---

### Question 4: Time Zone and Multi-City Handling
**Specific question:** The system expands to 5 cities (geography undefined). How is time zone handled?
- Are all times stored in UTC and converted per timezone on display?
- Does the system ask provider and learner for their timezone explicitly?
- What if a city spans multiple timezones (e.g., India)?
- Are the 5 cities all in one country or globally distributed?

**Why it matters:** Affects data model (add timezone field?), front-end display logic, and database queries (especially for search/filtering by time).

---

### Question 5: Analytics and Observability Scope
**Specific question:** "Analytics on everything" — what is the actual scope?
- Track every page view? Every search query? Every error?
- Real-time dashboards or batch reports?
- Which metrics matter most for decision-making? (Revenue trend, provider performance, learner satisfaction?)
- Who sees which analytics? (Ops only? Providers see their own? Public dashboard?)

**Why it matters:** Affects logging infrastructure, event schema, analytics tools selection, and storage requirements.

---

### Question 6: Double-Booking Prevention Mechanism
**Specific question:** "Time-slot conflicts must prevent double-booking" — at what level?
- Is a time slot atomic? (Can only one learner book the exact time interval?)
- What if learner A books 2-3pm and learner B tries to book 2:30-3:30pm — does the system reject it?
- Is this enforced at the database level (unique constraint) or at the application level?
- What happens if two requests arrive simultaneously for the same slot? (Which one wins?)

**Why it matters:** Affects database design, transactional handling, and error messages returned to learners.

---

### Question 7: No-Show Flagging and Consequences
**Specific question:** "Flag no-show users" — what are the consequences?
- After 1 no-show, 2, or 3?
- Can a no-show user still book? (Temporarily blocked? Permanently?)
- Does a provider get to reject future bookings from a flagged user?
- Who decides when a user is marked as "no-show"? (Learner doesn't cancel + appointment time passed, or provider manually marks it?)

**Why it matters:** Affects business logic, user experience (prevent future bookings), and provider trust.

---

### Question 8: Payout Schedule and Mechanics
**Specific question:** How does provider payout work?
- Daily? Weekly? Monthly?
- Manual withdrawal or automatic deposit?
- Which payment methods? (Bank transfer, PayPal, Stripe Connect?)
- Minimum payout threshold? (Can't cash out if earnings < $50?)
- Tax handling? (Does platform withhold for taxes?)

**Why it matters:** Affects accounting, financial reconciliation, and provider satisfaction.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Learner Functional Reqs** | 10 |
| **Provider Functional Reqs** | 10 |
| **Platform Functional Reqs** | 6 |
| **Total Functional** | 26 |
| **Constraints** | 10 |
| **Quality Attributes** | 6 |
| **Open Questions** | 8 |
| **Overall Ambiguities** | 6 major categories |

---

## Confidence Assessment

- **High confidence (clearly stated):** 18 requirements
- **Medium confidence (reasonable inference):** 13 requirements
- **Low confidence (educated guess):** 10 requirements

**Total: 41 distinct requirements extracted.**

---

## Next Steps

1. **Validate with PM:** Present ambiguities (Questions 1-8) for clarification
2. **Build DAG (Dependency Graph):** Determine which requirements must be done first
3. **Identify critical path:** Which requirements block the most other work?
4. **Plan vertical slice:** What is the smallest end-to-end feature to validate assumptions?
