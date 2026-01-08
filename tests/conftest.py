"""
Pytest configuration and fixtures for LearnLux tests.
"""

import pytest
from django.test import Client


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Return a Django test client logged in as the test user."""
    client.force_login(user)
    return client


@pytest.fixture
def user(db):
    """Create and return a test user."""
    from accounts.models import User

    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
        display_name="Test User",
    )


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    from accounts.models import User

    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        display_name="Admin User",
    )
