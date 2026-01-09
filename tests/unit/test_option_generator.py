"""Unit tests for OptionGenerator service."""

import pytest

from cards.models import DifficultyLevel, Topic, VocabularyCard


@pytest.mark.django_db
class TestOptionGenerator:
    """Tests for the OptionGenerator service."""

    @pytest.fixture
    def topic(self):
        """Create a test topic."""
        return Topic.objects.create(name="Greetings")

    @pytest.fixture
    def beginner_card(self, topic):
        """Create a beginner vocabulary card."""
        card = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        card.topics.add(topic)
        return card

    @pytest.fixture
    def additional_beginner_cards(self, topic):
        """Create additional beginner cards for wrong options."""
        cards = []
        for lux, eng in [("Äddi", "Goodbye"), ("Merci", "Thank you"), ("Pardon", "Sorry")]:
            card = VocabularyCard.objects.create(
                luxembourgish=lux,
                english=eng,
                difficulty_level=DifficultyLevel.BEGINNER,
            )
            card.topics.add(topic)
            cards.append(card)
        return cards

    def test_get_options_returns_three_options(self, beginner_card, additional_beginner_cards):
        """Test that get_options returns exactly 3 options."""
        from learning.services.option_generator import OptionGenerator

        generator = OptionGenerator(beginner_card, "lux_to_eng")
        result = generator.get_options()

        assert len(result["options"]) == 3

    def test_get_options_includes_correct_answer(self, beginner_card, additional_beginner_cards):
        """Test that options include the correct answer."""
        from learning.services.option_generator import OptionGenerator

        generator = OptionGenerator(beginner_card, "lux_to_eng")
        result = generator.get_options()

        assert result["correct_answer"] in result["options"]
        assert result["options"][result["correct_index"]] == result["correct_answer"]

    def test_get_options_lux_to_eng_direction(self, beginner_card, additional_beginner_cards):
        """Test lux_to_eng direction returns English options."""
        from learning.services.option_generator import OptionGenerator

        generator = OptionGenerator(beginner_card, "lux_to_eng")
        result = generator.get_options()

        assert result["correct_answer"] == "Hello"

    def test_get_options_eng_to_lux_direction(self, beginner_card, additional_beginner_cards):
        """Test eng_to_lux direction returns Luxembourgish options."""
        from learning.services.option_generator import OptionGenerator

        generator = OptionGenerator(beginner_card, "eng_to_lux")
        result = generator.get_options()

        assert result["correct_answer"] == "Moien"

    def test_options_are_unique(self, beginner_card, additional_beginner_cards):
        """Test that all options are unique."""
        from learning.services.option_generator import OptionGenerator

        generator = OptionGenerator(beginner_card, "lux_to_eng")
        result = generator.get_options()

        assert len(result["options"]) == len(set(result["options"]))

    def test_correct_index_is_valid(self, beginner_card, additional_beginner_cards):
        """Test that correct_index points to correct answer."""
        from learning.services.option_generator import OptionGenerator

        generator = OptionGenerator(beginner_card, "lux_to_eng")
        result = generator.get_options()

        assert 0 <= result["correct_index"] < 3
        assert result["options"][result["correct_index"]] == result["correct_answer"]

    def test_insufficient_options_raises_error(self, beginner_card):
        """Test that InsufficientOptionsError is raised when not enough cards."""
        from learning.services.option_generator import (
            InsufficientOptionsError,
            OptionGenerator,
        )

        generator = OptionGenerator(beginner_card, "lux_to_eng")

        with pytest.raises(InsufficientOptionsError):
            generator.get_options()

    def test_options_shuffled(self, beginner_card, additional_beginner_cards):
        """Test that options are shuffled (correct not always first)."""
        from learning.services.option_generator import OptionGenerator

        positions = set()
        for _ in range(20):
            generator = OptionGenerator(beginner_card, "lux_to_eng")
            result = generator.get_options()
            positions.add(result["correct_index"])
            if len(positions) > 1:
                break

        # With shuffling, we should see multiple positions over 20 tries
        assert len(positions) > 1


@pytest.mark.django_db
class TestOptionGeneratorPriorityCascade:
    """Tests for OptionGenerator priority cascade fallback."""

    def test_priority_same_topic_same_difficulty(self):
        """Test that same topic + same difficulty cards are preferred."""
        from learning.services.option_generator import OptionGenerator

        # Create target card
        topic = Topic.objects.create(name="Greetings")
        target = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        target.topics.add(topic)

        # Create same topic same difficulty cards
        for lux, eng in [("Äddi", "Goodbye"), ("Merci", "Thank you")]:
            card = VocabularyCard.objects.create(
                luxembourgish=lux,
                english=eng,
                difficulty_level=DifficultyLevel.BEGINNER,
            )
            card.topics.add(topic)

        # Create other topic card (should not be used if same topic has enough)
        other_topic = Topic.objects.create(name="Numbers")
        other_card = VocabularyCard.objects.create(
            luxembourgish="Eent",
            english="One",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        other_card.topics.add(other_topic)

        generator = OptionGenerator(target, "lux_to_eng")
        result = generator.get_options()

        # Should include cards from same topic (Goodbye, Thank you), not "One"
        assert "Goodbye" in result["options"]
        assert "Thank you" in result["options"]
        assert "One" not in result["options"]

    def test_fallback_to_any_difficulty_in_same_topic(self):
        """Test fallback when same difficulty cards insufficient in same topic."""
        from learning.services.option_generator import OptionGenerator

        topic = Topic.objects.create(name="Test")

        # Target: beginner card
        target = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        target.topics.add(topic)

        # Only one other beginner card - not enough for 2 wrong options
        VocabularyCard.objects.create(
            luxembourgish="Äddi",
            english="Goodbye",
            difficulty_level=DifficultyLevel.BEGINNER,
        ).topics.add(topic)

        # Add intermediate card in same topic for fallback
        VocabularyCard.objects.create(
            luxembourgish="Merci",
            english="Thank you",
            difficulty_level=DifficultyLevel.INTERMEDIATE,
        ).topics.add(topic)

        generator = OptionGenerator(target, "lux_to_eng")
        result = generator.get_options()

        assert len(result["options"]) == 3
        assert "Thank you" in result["options"]

    def test_fallback_to_any_topic_same_difficulty(self):
        """Test fallback to other topics when same topic has insufficient cards."""
        from learning.services.option_generator import OptionGenerator

        topic1 = Topic.objects.create(name="Topic1")
        topic2 = Topic.objects.create(name="Topic2")

        # Target: only card in topic1
        target = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        target.topics.add(topic1)

        # Cards in topic2 (same difficulty)
        for lux, eng in [("Äddi", "Goodbye"), ("Merci", "Thank you")]:
            card = VocabularyCard.objects.create(
                luxembourgish=lux,
                english=eng,
                difficulty_level=DifficultyLevel.BEGINNER,
            )
            card.topics.add(topic2)

        generator = OptionGenerator(target, "lux_to_eng")
        result = generator.get_options()

        assert len(result["options"]) == 3
        # Should use cards from topic2
        assert "Goodbye" in result["options"]
        assert "Thank you" in result["options"]


@pytest.mark.django_db
class TestOptionGeneratorEdgeCases:
    """Edge case tests for OptionGenerator."""

    def test_handles_duplicate_answers(self):
        """Test deduplication when multiple cards have same answer."""
        from learning.services.option_generator import OptionGenerator

        topic = Topic.objects.create(name="Test")

        target = VocabularyCard.objects.create(
            luxembourgish="Dag",
            english="Day",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        target.topics.add(topic)

        # Create cards with unique answers
        VocabularyCard.objects.create(
            luxembourgish="Nuecht",
            english="Night",
            difficulty_level=DifficultyLevel.BEGINNER,
        ).topics.add(topic)
        VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Morning",
            difficulty_level=DifficultyLevel.BEGINNER,
        ).topics.add(topic)

        generator = OptionGenerator(target, "lux_to_eng")
        result = generator.get_options()

        # All options should be unique
        assert len(result["options"]) == len(set(result["options"]))

    def test_excludes_correct_answer_from_wrong_options(self):
        """Test that correct answer is not duplicated in wrong options."""
        from learning.services.option_generator import OptionGenerator

        topic = Topic.objects.create(name="Test")

        target = VocabularyCard.objects.create(
            luxembourgish="Moien",
            english="Hello",
            difficulty_level=DifficultyLevel.BEGINNER,
        )
        target.topics.add(topic)

        # Create enough other cards
        for lux, eng in [("Äddi", "Goodbye"), ("Merci", "Thank you"), ("Pardon", "Sorry")]:
            VocabularyCard.objects.create(
                luxembourgish=lux,
                english=eng,
                difficulty_level=DifficultyLevel.BEGINNER,
            ).topics.add(topic)

        generator = OptionGenerator(target, "lux_to_eng")
        result = generator.get_options()

        # "Hello" should appear exactly once
        assert result["options"].count("Hello") == 1
