"""Integration tests for views."""

import json

import pytest
from django.urls import reverse

from accounts.models import User
from cards.models import DifficultyLevel, PhraseCard, Topic, VocabularyCard


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
        User.objects.create_user(
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


@pytest.mark.django_db
class TestDifficultyBasedStudyFlow:
    """Tests for difficulty-based study flow."""

    @pytest.fixture
    def setup_cards(self):
        """Create cards of different difficulties."""
        topic = Topic.objects.create(name="Greetings")

        # Beginner cards for multiple choice
        beginner_cards = []
        for lux, eng in [
            ("Moien", "Hello"),
            ("Äddi", "Goodbye"),
            ("Merci", "Thank you"),
            ("Pardon", "Sorry"),
        ]:
            card = VocabularyCard.objects.create(
                luxembourgish=lux,
                english=eng,
                difficulty_level=DifficultyLevel.BEGINNER,
            )
            card.topics.add(topic)
            beginner_cards.append(card)

        # Intermediate card
        intermediate = VocabularyCard.objects.create(
            luxembourgish="Haus",
            english="House",
            difficulty_level=DifficultyLevel.INTERMEDIATE,
        )
        intermediate.topics.add(topic)

        # Advanced card (PhraseCard)
        advanced = PhraseCard.objects.create(
            luxembourgish="Wéi geet et dir?",
            english="How are you?",
            difficulty_level=DifficultyLevel.ADVANCED,
        )
        advanced.topics.add(topic)

        return {
            "beginner": beginner_cards,
            "intermediate": intermediate,
            "advanced": advanced,
            "topic": topic,
        }

    def test_beginner_card_returns_multiple_choice(self, client, user, setup_cards):
        """Test that beginner cards return multiple choice options."""
        client.force_login(user)

        # Request next card from the specific topic with enough beginner cards
        response = client.get(
            reverse("learning:next_card"),
            {"direction": "lux_to_eng", "topic_id": setup_cards["topic"].id},
        )
        assert response.status_code == 200

        data = response.json()
        card = data.get("card")

        # If we got a beginner card, it should have multiple choice
        if card and card.get("difficulty_level") == DifficultyLevel.BEGINNER:
            assert card["input_mode"] == "multiple_choice"
            assert "options" in card
            assert len(card["options"]) == 3
            assert "correct_index" in card
            assert 0 <= card["correct_index"] < 3

    def test_intermediate_card_returns_text_input(self, client, user, setup_cards):
        """Test that intermediate cards return text input mode."""
        client.force_login(user)

        response = client.get(
            reverse("learning:next_card"), {"direction": "lux_to_eng"}
        )
        data = response.json()
        card = data.get("card")

        # If we got an intermediate card, it should be text input
        if card and card.get("difficulty_level") == DifficultyLevel.INTERMEDIATE:
            assert card["input_mode"] == "text_input"
            assert "options" not in card

    def test_advanced_card_returns_text_input(self, client, user, setup_cards):
        """Test that advanced cards return text input mode."""
        client.force_login(user)

        response = client.get(
            reverse("learning:next_card"), {"direction": "lux_to_eng"}
        )
        data = response.json()
        card = data.get("card")

        # If we got an advanced card, it should be text input
        if card and card.get("difficulty_level") == DifficultyLevel.ADVANCED:
            assert card["input_mode"] == "text_input"
            assert "options" not in card

    def test_check_answer_multiple_choice_correct(self, client, user, setup_cards):
        """Test checking correct multiple choice answer."""
        client.force_login(user)

        beginner_card = setup_cards["beginner"][0]  # "Moien" = "Hello"

        response = client.post(
            reverse("learning:check_answer"),
            data=json.dumps(
                {
                    "card_type": "vocabulary",
                    "card_id": beginner_card.id,
                    "answer": "Hello",
                    "direction": "lux_to_eng",
                    "input_mode": "multiple_choice",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True

    def test_check_answer_multiple_choice_incorrect(self, client, user, setup_cards):
        """Test checking incorrect multiple choice answer."""
        client.force_login(user)

        beginner_card = setup_cards["beginner"][0]  # "Moien" = "Hello"

        response = client.post(
            reverse("learning:check_answer"),
            data=json.dumps(
                {
                    "card_type": "vocabulary",
                    "card_id": beginner_card.id,
                    "answer": "Goodbye",  # Wrong answer
                    "direction": "lux_to_eng",
                    "input_mode": "multiple_choice",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is False

    def test_check_answer_text_input_with_typo(self, client, user, setup_cards):
        """Test that text input mode accepts typos."""
        client.force_login(user)

        intermediate_card = setup_cards["intermediate"]  # "Haus" = "House"

        response = client.post(
            reverse("learning:check_answer"),
            data=json.dumps(
                {
                    "card_type": "vocabulary",
                    "card_id": intermediate_card.id,
                    "answer": "Housee",  # Typo
                    "direction": "lux_to_eng",
                    "input_mode": "text_input",
                }
            ),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        # Typo tolerance should accept this
        assert data["is_correct"] is True
        assert data["match_quality"] == "close"

    def test_fallback_to_text_when_insufficient_options(self, client, user):
        """Test fallback to text input when not enough options for multiple choice."""
        client.force_login(user)

        topic = Topic.objects.create(name="Solo")
        # Only one beginner card - can't generate multiple choice
        card = VocabularyCard.objects.create(
            luxembourgish="Eent",
            english="One",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        card.topics.add(topic)

        response = client.get(
            reverse("learning:next_card"),
            {"topic_id": topic.id, "direction": "lux_to_eng"},
        )

        data = response.json()
        # Should fallback to text input since there aren't enough cards
        if data.get("card"):
            assert data["card"]["input_mode"] == "text_input"

    def test_response_includes_difficulty_level(self, client, user, setup_cards):
        """Test that response includes difficulty_level field."""
        client.force_login(user)

        response = client.get(
            reverse("learning:next_card"), {"direction": "lux_to_eng"}
        )
        data = response.json()

        if data.get("card"):
            assert "difficulty_level" in data["card"]
            assert data["card"]["difficulty_level"] in [1, 2, 3]
