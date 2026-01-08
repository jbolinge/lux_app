"""Integration tests for views."""

import pytest
from django.urls import reverse

from accounts.models import User
from cards.models import Topic, VocabularyCard


@pytest.mark.django_db
class TestAccountViews:
    """Tests for account-related views."""

    def test_register_page_loads(self, client):
        """Test that registration page loads."""
        response = client.get(reverse("accounts:register"))
        assert response.status_code == 200
        assert b"Sign Up" in response.content or b"Create" in response.content

    def test_login_page_loads(self, client):
        """Test that login page loads."""
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200
        assert b"Sign in" in response.content or b"Login" in response.content

    def test_register_creates_user(self, client):
        """Test that registration creates a user."""
        response = client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "testpass123!",
                "password2": "testpass123!",
            },
        )
        # Should redirect after successful registration
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()

    def test_login_works(self, client):
        """Test that login works."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        response = client.post(
            reverse("accounts:login"),
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )
        # Should redirect after successful login
        assert response.status_code == 302

    def test_profile_requires_login(self, client):
        """Test that profile page requires authentication."""
        response = client.get(reverse("accounts:profile"))
        # Should redirect to login
        assert response.status_code == 302
        assert "login" in response.url

    def test_profile_loads_for_authenticated_user(self, client, user):
        """Test that profile page loads for authenticated user."""
        client.force_login(user)
        response = client.get(reverse("accounts:profile"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestLearningViews:
    """Tests for learning-related views."""

    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires authentication."""
        response = client.get(reverse("learning:dashboard"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_dashboard_loads_for_authenticated_user(self, client, user):
        """Test that dashboard loads for authenticated user."""
        client.force_login(user)
        response = client.get(reverse("learning:dashboard"))
        assert response.status_code == 200
        # Check for user's name or common dashboard elements
        assert b"Dashboard" in response.content or b"LearnLux" in response.content

    def test_topics_page_loads(self, client, user):
        """Test that topics page loads."""
        client.force_login(user)
        response = client.get(reverse("learning:topics"))
        assert response.status_code == 200

    def test_topics_page_shows_topics(self, client, user):
        """Test that topics page shows created topics."""
        client.force_login(user)
        Topic.objects.create(name="Test Topic", description="A test topic")

        response = client.get(reverse("learning:topics"))
        assert response.status_code == 200
        assert b"Test Topic" in response.content

    def test_topic_detail_loads(self, client, user):
        """Test that topic detail page loads."""
        client.force_login(user)
        topic = Topic.objects.create(name="Greetings")

        response = client.get(reverse("learning:topic_detail", args=[topic.slug]))
        assert response.status_code == 200
        assert b"Greetings" in response.content

    def test_study_page_loads(self, client, user):
        """Test that study page loads."""
        client.force_login(user)
        response = client.get(reverse("learning:study"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestProgressViews:
    """Tests for progress-related views."""

    def test_statistics_page_loads(self, client, user):
        """Test that statistics page loads."""
        client.force_login(user)
        response = client.get(reverse("progress:statistics"))
        assert response.status_code == 200

    def test_history_page_loads(self, client, user):
        """Test that history page loads."""
        client.force_login(user)
        response = client.get(reverse("progress:history"))
        assert response.status_code == 200

    def test_topic_progress_page_loads(self, client, user):
        """Test that topic progress page loads."""
        client.force_login(user)
        response = client.get(reverse("progress:topic_progress"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestAPIEndpoints:
    """Tests for API endpoints."""

    def test_next_card_requires_login(self, client):
        """Test that next card API requires authentication."""
        response = client.get(reverse("learning:next_card"))
        assert response.status_code == 302  # Redirect to login

    def test_next_card_returns_card(self, client, user):
        """Test that next card API returns a card when available."""
        client.force_login(user)

        # Create a card
        topic = Topic.objects.create(name="Test")
        card = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
        )
        card.topics.add(topic)

        response = client.get(reverse("learning:next_card"))
        assert response.status_code == 200

    def test_check_answer_requires_login(self, client):
        """Test that check answer API requires authentication."""
        response = client.post(
            reverse("learning:check_answer"),
            content_type="application/json",
            data="{}",
        )
        assert response.status_code == 302  # Redirect to login
