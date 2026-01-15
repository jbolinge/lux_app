"""Unit tests for models."""

import pytest
from django.contrib.contenttypes.models import ContentType

from accounts.models import User
from cards.models import (
    DifficultyLevel,
    PhraseCard,
    RegisterChoice,
    Topic,
    VocabularyCard,
)
from progress.models import CardProgress, TopicProgress, UserStats


@pytest.mark.django_db
class TestUserModel:
    """Tests for the custom User model."""

    def test_create_user(self):
        """Test creating a basic user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")

    def test_user_display_name(self):
        """Test user display name field."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            display_name="Test Display Name",
        )
        assert user.display_name == "Test Display Name"
        assert user.get_display_name() == "Test Display Name"

    def test_user_display_name_fallback(self):
        """Test that get_display_name falls back to username."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        assert user.get_display_name() == "testuser"

    def test_user_stats_created_on_user_creation(self):
        """Test that UserStats is created when a user is created."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        assert hasattr(user, "stats")
        assert isinstance(user.stats, UserStats)


@pytest.mark.django_db
class TestTopicModel:
    """Tests for the Topic model."""

    def test_create_topic(self):
        """Test creating a basic topic."""
        topic = Topic.objects.create(
            name="Greetings",
            description="Basic greetings in Luxembourgish",
        )
        assert topic.name == "Greetings"
        assert topic.slug == "greetings"
        assert topic.difficulty_level == DifficultyLevel.BEGINNER

    def test_topic_hierarchy(self):
        """Test topic parent-child relationship."""
        parent = Topic.objects.create(name="Basics")
        child = Topic.objects.create(name="Numbers", parent=parent)

        assert child.parent == parent
        assert parent.children.count() == 1
        assert str(child) == "Basics > Numbers"

    def test_topic_slug_uniqueness(self):
        """Test that slugs are unique."""
        Topic.objects.create(name="Test Topic")
        topic2 = Topic.objects.create(name="Test Topic")

        assert topic2.slug == "test-topic-1"


@pytest.mark.django_db
class TestVocabularyCardModel:
    """Tests for the VocabularyCard model."""

    def test_create_vocabulary_card(self):
        """Test creating a vocabulary card."""
        card = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
        )
        assert card.luxembourgish == "Moien"
        assert card.english == "Hello"
        assert card.is_active is True

    def test_vocabulary_card_with_topics(self):
        """Test vocabulary card with multiple topics."""
        topic1 = Topic.objects.create(name="Greetings")
        topic2 = Topic.objects.create(name="Basics")

        card = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
        )
        card.topics.add(topic1, topic2)

        assert card.topics.count() == 2


@pytest.mark.django_db
class TestPhraseCardModel:
    """Tests for the PhraseCard model."""

    def test_create_phrase_card(self):
        """Test creating a phrase card."""
        card = PhraseCard.objects.create(
            luxembourgish="Wéi geet et?",
            english="How are you?",
            register=RegisterChoice.INFORMAL,
            difficulty_level=DifficultyLevel.ADVANCED,
        )
        assert card.luxembourgish == "Wéi geet et?"
        assert card.register == RegisterChoice.INFORMAL


@pytest.mark.django_db
class TestCardDifficultyValidation:
    """Tests for card type difficulty validation."""

    def test_vocabulary_card_allows_beginner(self):
        """Test VocabularyCard allows BEGINNER difficulty."""
        card = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        assert card.difficulty_level == DifficultyLevel.BEGINNER

    def test_vocabulary_card_allows_intermediate(self):
        """Test VocabularyCard allows INTERMEDIATE difficulty."""
        card = VocabularyCard.objects.create(
            luxembourgish="Haus",
            english="House",
            difficulty_level=DifficultyLevel.INTERMEDIATE,
        )
        assert card.difficulty_level == DifficultyLevel.INTERMEDIATE

    def test_vocabulary_card_rejects_advanced(self):
        """Test VocabularyCard rejects ADVANCED difficulty."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCard.objects.create(
                luxembourgish="Moien",
                english="Hello",
                difficulty_level=DifficultyLevel.ADVANCED,
            )
        assert "difficulty_level" in str(exc_info.value)

    def test_phrase_card_allows_beginner(self):
        """Test PhraseCard allows BEGINNER difficulty."""
        card = PhraseCard.objects.create(
            luxembourgish="Wéi geet et?",
            english="How are you?",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        assert card.difficulty_level == DifficultyLevel.BEGINNER

    def test_phrase_card_allows_intermediate(self):
        """Test PhraseCard allows INTERMEDIATE difficulty."""
        card = PhraseCard.objects.create(
            luxembourgish="Wéi geet et Iech?",
            english="How are you? (formal)",
            difficulty_level=DifficultyLevel.INTERMEDIATE,
        )
        assert card.difficulty_level == DifficultyLevel.INTERMEDIATE

    def test_phrase_card_allows_advanced(self):
        """Test PhraseCard allows ADVANCED difficulty."""
        card = PhraseCard.objects.create(
            luxembourgish="Ech si frou Iech kennenzeléieren",
            english="Nice to meet you",
            difficulty_level=DifficultyLevel.ADVANCED,
        )
        assert card.difficulty_level == DifficultyLevel.ADVANCED


@pytest.mark.django_db
class TestCardProgressModel:
    """Tests for the CardProgress model."""

    def test_create_card_progress(self):
        """Test creating card progress."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        card = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
        )
        content_type = ContentType.objects.get_for_model(card)

        progress = CardProgress.objects.create(
            user=user,
            card_content_type=content_type,
            card_object_id=card.id,
        )

        assert progress.times_shown == 0
        assert progress.ease_factor == 2.5
        assert progress.card == card

    def test_card_progress_accuracy(self):
        """Test accuracy calculation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        card = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
        )
        content_type = ContentType.objects.get_for_model(card)

        progress = CardProgress.objects.create(
            user=user,
            card_content_type=content_type,
            card_object_id=card.id,
            times_correct=7,
            times_incorrect=3,
        )

        assert progress.accuracy() == 70


@pytest.mark.django_db
class TestTopicProgressModel:
    """Tests for the TopicProgress model."""

    def test_topic_completion_percentage(self):
        """Test topic completion calculation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        topic = Topic.objects.create(name="Greetings")

        # Add some cards to the topic
        for i in range(10):
            card = VocabularyCard.objects.create(
                luxembourgish=f"word{i}",
                english=f"translation{i}",
            )
            card.topics.add(topic)

        progress = TopicProgress.objects.create(
            user=user,
            topic=topic,
            cards_seen=5,
        )

        assert progress.completion_percentage() == 50
