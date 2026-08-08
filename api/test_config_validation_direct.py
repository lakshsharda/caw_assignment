"""Direct test of configuration validation without .env file interference."""

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum
import os

print("=" * 70)
print("MODULE 3: Configuration Validation - Direct Tests")
print("=" * 70)

# Test by directly creating Settings with specific values
from app.config import Environment, Settings

# Test 1: Missing required DATABASE_URL
print("\n[TEST 1] Missing required DATABASE_URL")
print("-" * 70)

try:
    settings = Settings(
        app_env=Environment.development,
        port=8000,
        database_url="",  # Empty - should fail
        jwt_secret="this-is-a-secret-key-that-is-longer-than-32-characters-xxx",
    )
    print("❌ FAIL: Empty DATABASE_URL was accepted")
except ValidationError as e:
    error_msg = str(e)
    if "database_url" in error_msg:
        print(f"✓ PASS: Caught invalid empty DATABASE_URL")
        print(f"   Reason: {str(e.errors()[0]['msg'])}")
    else:
        print(f"❌ FAIL: Wrong error - {error_msg}")

# Test 2: Missing required JWT_SECRET
print("\n[TEST 2] Missing required JWT_SECRET (empty)")
print("-" * 70)

try:
    settings = Settings(
        app_env=Environment.development,
        port=8000,
        database_url="postgresql://localhost/test",
        jwt_secret="",  # Empty - should fail
    )
    print("❌ FAIL: Empty JWT_SECRET was accepted")
except ValidationError as e:
    error_msg = str(e)
    if "jwt_secret" in error_msg:
        print(f"✓ PASS: Caught invalid empty JWT_SECRET")
        print(f"   Reason: {str(e.errors()[0]['msg'])}")
    else:
        print(f"❌ FAIL: Wrong error - {error_msg}")

# Test 3: JWT_SECRET too short
print("\n[TEST 3] JWT_SECRET too short (< 32 chars)")
print("-" * 70)

try:
    settings = Settings(
        app_env=Environment.development,
        port=8000,
        database_url="postgresql://localhost/test",
        jwt_secret="too-short",  # Less than 32 chars
    )
    print("❌ FAIL: Short JWT_SECRET was accepted")
except ValidationError as e:
    error_msg = str(e)
    if "jwt_secret" in error_msg and "32" in error_msg:
        print(f"✓ PASS: Caught JWT_SECRET that's too short")
        print(f"   Reason: {str(e.errors()[0]['msg'])}")
    else:
        print(f"❌ FAIL: Wrong error - {error_msg}")

# Test 4: Invalid APP_ENV
print("\n[TEST 4] Invalid APP_ENV (banana)")
print("-" * 70)

try:
    settings = Settings(
        app_env="banana",  # type: ignore  - Invalid enum value
        port=8000,
        database_url="postgresql://localhost/test",
        jwt_secret="this-is-a-secret-key-that-is-longer-than-32-characters-xxx",
    )
    print("❌ FAIL: Invalid APP_ENV=banana was accepted")
except ValidationError as e:
    error_msg = str(e)
    if "app_env" in error_msg and ("development" in error_msg or "staging" in error_msg):
        print(f"✓ PASS: Caught invalid APP_ENV value")
        print(f"   Allowed: development, staging, production")
    else:
        print(f"❌ FAIL: Wrong error - {error_msg}")

# Test 5: Invalid PORT
print("\n[TEST 5] Invalid PORT (99999 - out of range)")
print("-" * 70)

try:
    settings = Settings(
        app_env=Environment.development,
        port=99999,  # Out of TCP port range
        database_url="postgresql://localhost/test",
        jwt_secret="this-is-a-secret-key-that-is-longer-than-32-characters-xxx",
    )
    print("❌ FAIL: Invalid PORT was accepted")
except ValidationError as e:
    error_msg = str(e)
    if "port" in error_msg and ("65535" in error_msg or "1 and" in error_msg):
        print(f"✓ PASS: Caught invalid PORT value")
        print(f"   Reason: {str(e.errors()[0]['msg'])}")
    else:
        print(f"❌ FAIL: Wrong error - {error_msg}")

# Test 6: Valid configuration
print("\n[TEST 6] Valid configuration")
print("-" * 70)

try:
    settings = Settings(
        app_env=Environment.production,
        port=8000,
        database_url="postgresql+psycopg://user:pass@prod-db.example.com:5432/mydb",
        jwt_secret="this-is-a-valid-secret-key-longer-than-32-characters-xxx",
        log_level="warn",
    )
    print(f"✓ PASS: Valid configuration accepted")
    print(f"   - APP_ENV: {settings.app_env.value}")
    print(f"   - PORT: {settings.port}")
    print(f"   - LOG_LEVEL: {settings.log_level}")
    print(f"   - is_production: {settings.is_production}")
except Exception as e:
    print(f"❌ FAIL: Valid configuration rejected - {e}")

print("\n" + "=" * 70)
print("✓ Configuration validation tests complete!")
print("=" * 70)
