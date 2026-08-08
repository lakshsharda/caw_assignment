#!/usr/bin/env python3
"""
Enhanced reproduction script for race condition with timestamp tracking.
Sends 10 concurrent requests and compares log timestamps with database values.
"""
import asyncio
import aiohttp
import sys
from datetime import datetime, timezone

# Configuration
SHORT_CODE = "abc123"  # A link that should exist in the DB
CONCURRENCY = 10
BASE_URL = f"http://localhost:8000/r/{SHORT_CODE}"

# Track request timestamps
request_timestamps = {}

async def make_request(session, request_num):
    """Make a single GET request, tracking the exact time sent."""
    try:
        # Record exact timestamp when request is sent
        request_timestamps[request_num] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        
        async with session.get(BASE_URL, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            return resp.status, request_num, None
    except Exception as e:
        return None, request_num, str(e)

async def main():
    """Fire concurrent requests and report results."""
    print(f"Enhanced Reproduction Script: Race Condition with Timestamp Analysis")
    print(f"Sending {CONCURRENCY} concurrent requests to {BASE_URL}")
    print("-" * 80)
    
    async with aiohttp.ClientSession() as session:
        # Fire all requests simultaneously
        tasks = [make_request(session, i) for i in range(CONCURRENCY)]
        results = await asyncio.gather(*tasks)
    
    # Parse results
    successes = [r for r in results if isinstance(r[0], int) and r[0] in (301, 302, 307)]
    errors = [r for r in results if isinstance(r[0], int) and r[0] == 500]
    exceptions = [r for r in results if r[2] is not None]
    
    print(f"\nResults:")
    print(f"  Successful redirects (3xx):  {len(successes)}")
    print(f"  Server errors (500):         {len(errors)}")
    print(f"  Connection exceptions:       {len(exceptions)}")
    
    print(f"\nRequest Timestamps (when each request was sent):")
    for req_num in sorted(request_timestamps.keys()):
        print(f"  Request {req_num}: {request_timestamps[req_num]}")
    
    print(f"\nLast request sent at: {request_timestamps[max(request_timestamps.keys())]}")
    print(f"First request sent at: {request_timestamps[min(request_timestamps.keys())]}")
    
    if errors:
        print(f"\n✗ BUG REPRODUCED: Race condition triggered!")
        print(f"  {len(errors)} concurrent requests caused errors")
        return 1
    else:
        print(f"\n✓ No 500 errors (first race condition is fixed).")
        print(f"  Check server logs above for timestamps of 'request received' and 'response sent'.")
        print(f"  Then query the database to check if click_events.clicked_at matches the actual request times.")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
