# Module 01 Diagnosis Notes

## Bug 1
- Symptom: GET /r/6O0Rfr returned 500 instead of a redirect.
- Hypothesis A: An unhandled exception in the redirect/expiry logic.
  - Command: Run the redirect handler in-process.
  - Observation: Returned 307 correctly, so the app code was not the cause.
- Hypothesis B: A process-lifecycle failure.
  - Command: Check for a listening process on port 8000.
  - Observation: Nothing was listening, confirming the server was not running.
- Fix: Run Uvicorn in an open foreground terminal so its lifetime is not tied to a closing shell session.
- Verification proof: curl -i http://localhost:8000/r/6O0Rfr returned 307 with the correct Location header while the terminal stayed open.

## Bug 2
- Symptom:
- Hypothesis A:
  - Command:
  - Observation:
- Hypothesis B:
  - Command:
  - Observation:
- Fix:
- Verification proof:
