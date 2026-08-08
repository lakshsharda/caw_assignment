# Module 3 BREAK - Silent Data Corruption Race Condition

## Problem Statement
After fixing the first race (duplicate key on INSERT), a second race condition exists that causes **silent data corruption**: the `last_accessed_at` timestamp in the database does not match the actual timestamp of the last request that hit the server.

## Root Cause

### The Vulnerable Pattern
```python
# Step 1: Insert new click event (or skip if exists)
INSERT INTO click_events (link_id, clicked_at)
VALUES (:link_id, :clicked_at)
ON CONFLICT DO NOTHING

# RACE WINDOW: Between INSERT and UPDATE, multiple requests can execute concurrently

# Step 2: Update the last_accessed_at timestamp
UPDATE click_events 
SET last_accessed_at = :now
WHERE link_id = :link_id
```

### Why This Is a Race Condition

Timeline with 10 concurrent requests hitting the same link at nearly the same time:

```
Request A: now_utc = 14:05:32.100 (captured by Python datetime.now())
Request B: now_utc = 14:05:32.050 (captured earlier due to scheduling)
Request C: now_utc = 14:05:32.075

Request A: INSERT click_events ... → Success or conflict
Request B: INSERT click_events ... → Success or conflict
Request C: INSERT click_events ... → Success or conflict

REQUEST B: UPDATE click_events SET last_accessed_at = 14:05:32.050
REQUEST C: UPDATE click_events SET last_accessed_at = 14:05:32.075
REQUEST A: UPDATE click_events SET last_accessed_at = 14:05:32.100

Final value in DB: last_accessed_at = 14:05:32.100 (whichever UPDATE ran last)
But the ACTUAL last request to hit the server might have been Request C at 14:05:32.075
```

The problem: **each request captures its own timestamp when it starts processing (via `datetime.now()`), not when the database actually records it**. Under concurrency, the request that captures the earliest timestamp but executes the UPDATE last will overwrite the truly-last value.

## Data Corruption Signature

**Symptom:** `last_accessed_at` in database does not match the actual last request timestamp from logs

- The count field is correct (10 requests = count incremented 10 times)
- But the timestamp field is wrong or corresponds to an earlier request, not the last one
- No errors in logs
- No 500 responses
- Silent corruption that only becomes obvious when querying the database

This is worse than the first race because:
- First race: obvious error (500) that gets caught immediately
- Second race: silent corruption that corrupts analytics and goes unnoticed

## The Fix

Replace the separate INSERT + UPDATE with a single atomic operation that ensures the latest timestamp always wins:

```python
INSERT INTO click_events (link_id, clicked_at)
VALUES (:link_id, :clicked_at)
ON CONFLICT (link_id)
DO UPDATE SET 
    last_accessed_at = EXCLUDED.clicked_at
```

Or even better, use the database's `now()` function (server time) instead of Python's `datetime.now()` (client time):

```python
INSERT INTO click_events (link_id, clicked_at)
VALUES (:link_id, now())
ON CONFLICT (link_id)
DO UPDATE SET 
    last_accessed_at = now()
```

This ensures:
1. No Python-to-database timing differences
2. The database timestamp is atomic — there's no window where one request can overwrite another's update
3. `last_accessed_at` is guaranteed to be the actual last database write, not whichever application request finishes last

## Evidence

When you run 10 concurrent requests:
- **Before fix:** Logs show 10 requests arriving, each with their own timestamp (14:05:32.100, 14:05:32.050, etc.)
- **After fix:** Query the database for the click_events row, and `last_accessed_at` will match the highest/latest timestamp from the request logs, guaranteed

The minimal repro that demonstrates this:
```python
# Send 10 concurrent requests with known delays
Request 1: arrives at T1 = 14:05:32.001
Request 2: arrives at T2 = 14:05:32.002
...
Request 10: arrives at T10 = 14:05:32.010

# With vulnerable code, last_accessed_at in DB might be T3 (not T10)
# Because Request 3 captured T3 early but its UPDATE executed last
```
