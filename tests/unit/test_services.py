"""Unit tests for learning services."""

from django.utils import timezone

from learning.services.answer_checker import AnswerChecker, MatchQuality
from learning.services.spaced_repetition import SpacedRepetition


class TestAnswerChecker:
    """Tests for the AnswerChecker service."""

    def test_exact_match(self):
        """Test exact match checking."""
        checker = AnswerChecker()
        result = checker.check("Hello", "Hello")

        assert result["is_correct"] is True
        assert result["match_quality"] == MatchQuality.EXACT.value

    def test_case_insensitive_match(self):
        """Test case insensitive matching (default)."""
        checker = AnswerChecker()
        result = checker.check("hello", "Hello")

        assert result["is_correct"] is True
        assert result["match_quality"] == MatchQuality.EXACT.value

    def test_case_sensitive_match(self):
        """Test case sensitive matching."""
        checker = AnswerChecker(case_sensitive=True, typo_tolerance=0)
        result = checker.check("hello", "Hello")

        assert result["is_correct"] is False

    def test_whitespace_normalization(self):
        """Test that extra whitespace is normalized."""
        checker = AnswerChecker()
        result = checker.check("  Hello   World  ", "Hello World")

        assert result["is_correct"] is True

    def test_typo_tolerance(self):
        """Test typo tolerance."""
        checker = AnswerChecker(typo_tolerance=1)
        result = checker.check("Helo", "Hello")  # One character missing

        assert result["is_correct"] is True
        assert result["match_quality"] == MatchQuality.CLOSE.value

    def test_incorrect_answer(self):
        """Test incorrect answer."""
        checker = AnswerChecker()
        result = checker.check("Goodbye", "Hello")

        assert result["is_correct"] is False
        assert result["match_quality"] == MatchQuality.INCORRECT.value

    def test_punctuation_ignored(self):
        """Test that trailing punctuation is ignored."""
        checker = AnswerChecker()
        result = checker.check("Hello!", "Hello")

        assert result["is_correct"] is True


class TestSpacedRepetition:
    """Tests for the SpacedRepetition service."""

    def test_initial_correct_answer(self):
        """Test SM-2 calculation for first correct answer."""
        sr = SpacedRepetition()
        result = sr.calculate(
            quality=4,  # Correct
            ease_factor=2.5,
            interval=0,
            repetitions=0,
        )

        assert result.repetitions == 1
        assert result.interval == 1  # First interval is 1 day
        assert result.ease_factor >= 2.5

    def test_second_correct_answer(self):
        """Test SM-2 calculation for second correct answer."""
        sr = SpacedRepetition()
        result = sr.calculate(
            quality=4,
            ease_factor=2.5,
            interval=1,
            repetitions=1,
        )

        assert result.repetitions == 2
        assert result.interval == 6  # Second interval is 6 days

    def test_third_correct_answer(self):
        """Test SM-2 calculation for third+ correct answer."""
        sr = SpacedRepetition()
        result = sr.calculate(
            quality=4,
            ease_factor=2.5,
            interval=6,
            repetitions=2,
        )

        assert result.repetitions == 3
        # Third interval is previous * ease_factor
        assert result.interval == round(6 * result.ease_factor)

    def test_incorrect_answer_resets(self):
        """Test that incorrect answer resets progress."""
        sr = SpacedRepetition()
        result = sr.calculate(
            quality=1,  # Incorrect
            ease_factor=2.5,
            interval=30,
            repetitions=5,
        )

        assert result.repetitions == 0
        assert result.interval == 1

    def test_ease_factor_minimum(self):
        """Test that ease factor doesn't go below minimum."""
        sr = SpacedRepetition()
        # Multiple poor answers should lower ease factor
        result = sr.calculate(
            quality=0,  # Very poor
            ease_factor=1.3,  # Already at minimum
            interval=1,
            repetitions=0,
        )

        assert result.ease_factor >= sr.MIN_EASE_FACTOR

    def test_quality_from_correct(self):
        """Test quality score conversion."""
        sr = SpacedRepetition()

        assert sr.quality_from_correct(True) == 4
        assert sr.quality_from_correct(False) == 1

    def test_next_review_date_set(self):
        """Test that next review date is properly set."""
        sr = SpacedRepetition()
        result = sr.calculate(
            quality=4,
            ease_factor=2.5,
            interval=1,
            repetitions=1,
        )

        assert result.next_review > timezone.now()
