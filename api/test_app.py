"""Basic test suite for linkops API."""

import pytest


def test_health_check():
    """Test that health check passes."""
    assert True


def test_intentional_fail():
    """This test is intentionally written to fail."""
    # This will fail when we run the pipeline
    assert 1 + 1 == 3, "Math works (intentional fail for pipeline demo)"
