"""Basic test suite for linkops API."""

import pytest


def test_health_check():
    """Test that health check passes."""
    assert True


def test_math():
    """Test basic math operations."""
    assert 1 + 1 == 2, "Basic math should work"
