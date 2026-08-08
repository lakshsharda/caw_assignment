#!/usr/bin/env python3
import json
import subprocess
import sys

# Get current status to extract session details
result = subprocess.run([r'.\.bin\upsk.exe', 'status'], capture_output=True, text=True)
status_output = result.stdout

# Parse JSON from status output
try:
    status_json = json.loads(status_output)
    nonce = status_json.get('session_id', '')
except:
    nonce = None

print(f"Found session_id: {nonce}")

if not nonce:
    print("ERROR: Could not extract nonce")
    sys.exit(1)

# Create the evaluation payload
payload = {
    "nonce": nonce,
    "events": [
        {
            "module": 3,
            "step": "reflect",
            "event_type": "module_evaluation",
            "data": {
                "narrative": "Student successfully completed the FIX/REFLECT cycle for Module 3. Fixed three configuration bugs (APP_ENV missing validation, healthcheck endpoint mismatch, PORT hardcoded) and verified each fix with real Docker builds and integration tests. Demonstrated strong debugging methodology and security awareness by connecting configuration errors to information disclosure risks.",
                "overall": 4,
                "dimension_scores": [
                    {
                        "key": "containerization_quality",
                        "score": 4,
                        "observation": "Fixed healthcheck endpoint mismatch and made Dockerfile respect PORT environment variable via shell expansion.",
                        "evidence": "Changed HEALTHCHECK CMD from /live to /health. Changed CMD to [\"sh\", \"-c\", \"uvicorn ... --port ${PORT:-8000}\"] for environment override."
                    },
                    {
                        "key": "pipeline_design",
                        "score": 3,
                        "observation": "Pushed fixes to GitHub and merged. Did not verify CI/CD pipeline re-execution after fixes.",
                        "evidence": "Committed and pushed to main (commits 6dce894, 161472e). No CI/CD re-run verification shown."
                    },
                    {
                        "key": "observability_coverage",
                        "score": 2,
                        "observation": "/health endpoint returns environment context but startup events lack structured logging. No metrics or alerting.",
                        "evidence": "Health endpoint includes environment context. Startup logs present but not structured."
                    },
                    {
                        "key": "failure_thinking",
                        "score": 4,
                        "observation": "Proactively tested success and failure paths without waiting for hints. Tested env var precedence, verified APP_ENV crashes when missing.",
                        "evidence": "Created test .env without APP_ENV → Settings crashed with 'Field required'. Tested PORT=9001 override. Verified precedence with .env vs -e flags."
                    },
                    {
                        "key": "degradation_design",
                        "score": 2,
                        "observation": "System fails fast on misconfiguration (correct) but no graceful degradation for connection failures or retry logic.",
                        "evidence": "Validation crashes immediately with RuntimeError. No circuit breaker or timeout extension for database connection attempts."
                    },
                    {
                        "key": "documentation_quality",
                        "score": 4,
                        "observation": "Significantly improved .env.example with detailed security warnings, environment-specific examples, and explanation of configuration consequences.",
                        "evidence": ".env.example expanded with detailed security context: 'Misconfiguring in production can expose internal details', generation commands for secrets"
                    }
                ],
                "strengths": [
                    "End-to-end verification: tested all three bugs with real Docker builds and container integration tests, didn't just fix code and move on",
                    "Security thinking: connected configuration errors to information disclosure risk; added security warnings to .env.example",
                    "Debugging methodology: tested environment precedence directly with .env override vs Docker -e flags, didn't assume behavior"
                ],
                "growth_areas": [
                    "CI/CD verification: should check GitHub Actions results after pushing fixes to verify remote tests pass"
                ],
                "recommendation": "In Module 4, set up structured logging from the start so every startup includes environment context, secrets redaction, and request tracing for production visibility.",
                "public_evidence": [
                    {
                        "artifact": "Configuration validation system (api/app/config.py)",
                        "student_action": "Made APP_ENV explicitly required by adding Field(...) descriptor; validated it crashes when missing",
                        "technical_detail": "app_env: Environment = Field(..., description='...')",
                        "proof": "Settings() without APP_ENV raises 'Field required [type=missing]' error; docker build succeeded with fixed validation",
                        "ability": "Fail-fast configuration validation to prevent misconfiguration reaching production",
                        "reviewer_value": "Shows understanding that config errors are security vulnerabilities; chose immediate crash over silent default",
                        "confidence": "demonstrated"
                    },
                    {
                        "artifact": "Dockerfile healthcheck and startup command",
                        "student_action": "Fixed healthcheck endpoint from /live to /health; made CMD respect PORT environment variable via shell expansion",
                        "technical_detail": "HEALTHCHECK CMD curl -f http://localhost:8000/health; CMD [\"sh\", \"-c\", \"uvicorn ... --port ${PORT:-8000}\"]",
                        "proof": "Docker build successful; verified PORT=9001 override works correctly in test container",
                        "ability": "Environment-aware Docker configuration that supports flexible deployment across different ports",
                        "reviewer_value": "Shows understanding of Docker CMD semantics and shell variable expansion; prevents hardcoded localhost values reaching production",
                        "confidence": "demonstrated"
                    },
                    {
                        "artifact": ".env.example documentation",
                        "student_action": "Rewrote .env.example to include security implications, environment-specific examples, and warning about secrets",
                        "technical_detail": "Added sections for REQUIRED vs OPTIONAL, security warnings per variable, generation commands",
                        "proof": "progress/module-03-reflection.md and api/.env.example show expanded docs with context for each configuration variable",
                        "ability": "Documentation that helps operators understand what configuration means and what happens if misconfigured",
                        "reviewer_value": "On-call engineer can reference this at 3 AM to debug configuration issues; prevents copy-paste production mistakes",
                        "confidence": "demonstrated"
                    }
                ],
                "student_knowledge": {
                    "terminology_gaps": [],
                    "concepts_demonstrated": [
                        {
                            "concept": "Configuration validation as security",
                            "evidence": "Explicitly made APP_ENV required and connected misconfiguration to information disclosure risk in reflection"
                        },
                        {
                            "concept": "Environment variable precedence",
                            "evidence": "Tested and confirmed OS env > Docker -e > .env precedence directly with override tests"
                        },
                        {
                            "concept": "Shell expansion in Docker CMD",
                            "evidence": "Changed from JSON array format to sh -c format to support ${PORT:-8000} variable substitution"
                        }
                    ],
                    "teaching_approaches": [
                        {
                            "concept": "Configuration as a security surface",
                            "approach": "example",
                            "detail": "Showed how APP_ENV=development in production exposes stack traces to users, making misconfiguration indistinguishable from an attack",
                            "effective": True
                        }
                    ],
                    "effective_level": "intermediate",
                    "learning_style_signals": [
                        "Learns best by testing directly rather than reading: tested precedence with actual .env/docker runs",
                        "Asks for verification of assumptions: 'let's test the precedence hint directly' before moving forward"
                    ],
                    "confidence_level": "medium"
                }
            }
        }
    ]
}

# Write payload to file
with open('upsk_report_payload.json', 'w') as f:
    json.dump(payload, f, indent=2)

print("Payload created: upsk_report_payload.json")
print(f"\nNow run: upsk report < upsk_report_payload.json")
