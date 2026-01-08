"""End-to-end tests for authentication flow.

These tests use pytest-playwright with Django's StaticLiveServerTestCase approach.
"""

import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright

# Allow synchronous database operations in async context created by Playwright
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class TestRegistrationFlow(StaticLiveServerTestCase):
    """Test user registration flow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def test_registration_page_loads(self):
        """Test that registration page loads correctly."""
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/accounts/register/")

        # Check page title
        assert "Sign Up" in page.title() or "LearnLux" in page.title()

        # Check form elements exist
        assert page.locator("#id_username").is_visible()
        assert page.locator("#id_email").is_visible()
        assert page.locator("#id_password1").is_visible()
        assert page.locator("#id_password2").is_visible()

        page.close()

    def test_registration_creates_account(self):
        """Test that registration creates a new account."""
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/accounts/register/")

        # Fill out form
        page.fill("#id_username", "e2etestuser")
        page.fill("#id_email", "e2e@example.com")
        page.fill("#id_display_name", "E2E Test User")
        page.fill("#id_password1", "testpass123!")
        page.fill("#id_password2", "testpass123!")

        # Submit form
        page.click('button[type="submit"]')

        # Should redirect to dashboard after successful registration
        page.wait_for_url(f"{self.live_server_url}/")
        assert "Dashboard" in page.title() or "LearnLux" in page.title()

        page.close()


class TestLoginFlow(StaticLiveServerTestCase):
    """Test user login flow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def test_login_page_loads(self):
        """Test that login page loads correctly."""
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/accounts/login/")

        # Check page title
        assert "Login" in page.title() or "LearnLux" in page.title()

        # Check form elements
        assert page.locator("#id_username").is_visible()
        assert page.locator("#id_password").is_visible()

        page.close()


class TestDashboard(StaticLiveServerTestCase):
    """Test dashboard functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def test_dashboard_shows_stats_after_login(self):
        """Test that dashboard shows user stats after login."""
        page = self.browser.new_page()

        # Register first
        page.goto(f"{self.live_server_url}/accounts/register/")
        page.fill("#id_username", "dashuser")
        page.fill("#id_email", "dash@example.com")
        page.fill("#id_password1", "testpass123!")
        page.fill("#id_password2", "testpass123!")
        page.click('button[type="submit"]')
        page.wait_for_url(f"{self.live_server_url}/")

        # Check dashboard elements
        content = page.content()
        assert "Cards Studied" in content or "cards" in content.lower()

        page.close()


class TestTopicsPage(StaticLiveServerTestCase):
    """Test topics page."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def test_topics_page_loads(self):
        """Test that topics page loads after login."""
        page = self.browser.new_page()

        # Register first
        page.goto(f"{self.live_server_url}/accounts/register/")
        page.fill("#id_username", "topicuser")
        page.fill("#id_email", "topic@example.com")
        page.fill("#id_password1", "testpass123!")
        page.fill("#id_password2", "testpass123!")
        page.click('button[type="submit"]')
        page.wait_for_url(f"{self.live_server_url}/")

        # Go to topics
        page.goto(f"{self.live_server_url}/topics/")

        # Check for topic elements
        assert "Topics" in page.title() or "LearnLux" in page.title()

        page.close()
