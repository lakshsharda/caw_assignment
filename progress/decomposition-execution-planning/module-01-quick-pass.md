# SkillSwap Requirements - Quick Pass

**Module:** Decomposition & Execution Planning, Module 01 BUILD  
**Date:** 2026-08-09  
**Product:** SkillSwap (two-sided marketplace for skill-based sessions)

---

## 5 Explicit Requirements (One Line Each)

1. **Providers can publish services with description, availability, and pricing** — Functional, Provider-facing
2. **Learners can browse and search services, with results feeling instant** — Functional, Quality Attribute
3. **Time-slot conflicts must prevent double-booking** — Constraint, Platform-critical
4. **Cancellation behavior is explicit with provider-defined policies applied** — Functional, Business Rule
5. **Platform takes 15% commission with consistent calculation across all providers** — Constraint, Business Rule

---

## 2 Major Ambiguities

1. **Booking Payment Model:** Spec says "pay through platform" but is unclear: Does the user pay immediately to confirm the booking, or reserve first and pay later? What happens if payment fails after slot is reserved? Does the platform hold funds and transfer to provider later, or is it pass-through?

2. **Cancellation Policy Flexibility:** Spec says "provider's cancellation policy applied" but is undefined: Is each provider's policy a free-text field? Structured rules (e.g., "full refund if canceled 24+ hours before")? Who defines the default policy if provider doesn't set one? How is it displayed to users before booking?

---

## 1 PM Question Right Now

**If a learner and provider are both in different timezones within the same city (e.g., San Francisco spans US time but SkillSwap expands across 5 cities), how is the time slot rendered to each party? Do we store in UTC and convert on display, or do we ask both parties for their timezone upfront?**

---

## Quick Assessment

- Requirements identified: 5/5
- Major gaps found: 2 (categorization ambiguities)
- PM blockers: 1 (timezone + multi-city coordination)
- Ready to proceed to full extraction: YES
