# Module 3 BUILD - Reproduction Science

## Problem Statement
Intermittent 500 errors on popular short links, appearing unpredictably a few times per hour.

## Root Cause Analysis

### Hypothesis Formation (Phase 1)
**Candidate 3: Concurrency** — Selected as most likely
- Errors cluster on popular links
- Popular links = more traffic = more concurrent requests
- Evidence: single-request links almost never error
- Strong, falsifiable hypothesis pointing to race condition

### Attack Pattern
Classic **check-then-act race condition** in the redirect analytics logging:

```
Request A: SELECT (check if click event exists for this link+minute bucket)
           → No row found
Request B: SELECT (check if click event exists for this link+minute bucket)  
           → No row found
Request A: INSERT (new click event)
           → Success
Request B: INSERT (same click event)
           → CONSTRAINT VIOLATION: duplicate key on (link_id, clicked_at)
```

Both requests checked independently, found nothing, and attempted to insert the same row. The second INSERT fails because the first one already claimed the row.

## Implementation

### Vulnerable Code (Before)
File: `api/app/routers/redirect.py`

```python
# Step 1: Check if analytics row exists
existing = db_session.execute(
    text("SELECT id FROM click_events WHERE link_id = :link_id AND ..."),
    {"link_id": link.id, ...}
).first()

# Step 2: Window of vulnerability — two requests can execute between check and act
if not existing:
    db_session.execute(
        text("INSERT INTO click_events (link_id, clicked_at) VALUES (:link_id, :clicked_at)"),
        {"link_id": link.id, "clicked_at": now_utc}
    )
```

**Problem:** The two operations (SELECT then INSERT) are not atomic. Two concurrent requests can both execute the SELECT, both see no row, and both attempt the INSERT.

### Fixed Code (After)
```python
# Atomic upsert: insert + conflict handling in single operation
db_session.execute(
    text("""
        INSERT INTO click_events (link_id, clicked_at)
        VALUES (:link_id, :clicked_at)
        ON CONFLICT DO NOTHING
    """),
    {"link_id": link.id, "clicked_at": now_utc}
)
```

**Solution:** PostgreSQL's `INSERT ... ON CONFLICT` is atomic. The database handles the entire operation (check + insert or skip) as a single indivisible step. No race condition window.

## Reproduction Script
File: `repro_race.py`

Minimal concurrent test that sends 10 simultaneous requests to the same short code:
- Triggers the race condition reliably (usually within first 1-2 runs)
- Returns status codes to identify 500 errors
- Clearly reports when bug is reproduced vs. when no errors occurred

Usage:
```bash
python repro_race.py
```

Expected output (before fix):
```
Results:
  Successful redirects (3xx):  7
  Server errors (500):         3
  Connection exceptions:       0

✗ BUG REPRODUCED: Race condition triggered!
  3 concurrent requests caused duplicate key constraint violation
```

Expected output (after fix):
```
Results:
  Successful redirects (3xx):  10
  Server errors (500):         0
  Connection exceptions:       0

✓ No errors this run.
```

## Key Principle
Almost every "flaky" bug is actually **deterministic**  — it just has a trigger you haven't found yet. The concurrency trigger here was discoverable from the symptom alone (errors on popular links = high concurrent traffic). The reproduction script turned "sometimes breaks" into "breaks every time I run this script under the right conditions."

## Next Steps
1. Verify the fix prevents race condition (run `repro_race.py` 10 times with 0 errors)
2. Ensure analytics data integrity (check click_event count after concurrent requests)
3. Deploy both the fix AND the reproduction script to permanent CI regression checks
