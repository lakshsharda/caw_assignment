#!/usr/bin/env python3
"""
Reproduction script for race condition in redirect analytics logging.
Minimal concurrent requests to trigger duplicate key constraint violation.
"""
import asyncio
import aiohttp
import sys

# Configuration
SHORT_CODE = "abc123"  # A link that should exist in the DB
CONCURRENCY = 10
BASE_URL = f"http://localhost:8000/r/{SHORT_CODE}"

async def make_request(session, request_num):
    """Make a single GET request and return status code."""
    try:
        async with session.get(BASE_URL, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            return resp.status, request_num, None
    except Exception as e:
        return None, request_num, str(e)

async def main():
    """Fire concurrent requests and report results."""
    print(f"Reproduction Script: Race Condition in Analytics Logging")
    print(f"Sending {CONCURRENCY} concurrent requests to {BASE_URL}")
    print("-" * 60)
    
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
    
    if errors:
        print(f"\n✗ BUG REPRODUCED: Race condition triggered!")
        print(f"  {len(errors)} concurrent requests caused duplicate key constraint violation")
        return 1
    else:
        print(f"\n✓ No errors this run.")
        print(f"  Try running the script multiple times to trigger the race.")
        print(f"  Increase CONCURRENCY if the bug doesn't appear after 3-4 runs.")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
