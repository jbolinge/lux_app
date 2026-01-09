"""
Option Generator for multiple choice questions.

Generates wrong answer options for Easy (Beginner) difficulty cards,
following a priority cascade for selecting distractor options.
"""

import random

from cards.models import VocabularyCard


class InsufficientOptionsError(Exception):
    """Raised when not enough unique options can be generated."""

    pass


class OptionGenerator:
    """
    Generates wrong answer options for multiple choice questions.

    Selection priority for wrong options:
    1. Same topic + same difficulty (BEGINNER)
    2. Same topic + any difficulty
    3. Any topic + same difficulty (BEGINNER)
    4. Any card (fallback)
    """

    def __init__(self, card: VocabularyCard, direction: str, count: int = 2):
        """
        Initialize the generator.

        Args:
            card: The correct card (VocabularyCard for Easy mode)
            direction: 'lux_to_eng' or 'eng_to_lux'
            count: Number of wrong options to generate (default 2)
        """
        self.card = card
        self.direction = direction
        self.count = count

    def get_options(self) -> dict:
        """
        Generate multiple choice options.

        Returns:
            dict with:
                - correct_answer: The correct answer string
                - options: List of 3 strings (shuffled)
                - correct_index: Position of correct answer (0, 1, or 2)

        Raises:
            InsufficientOptionsError: If cannot generate enough unique options
        """
        correct = self._get_answer_field(self.card)
        wrong = self._get_wrong_options()

        if len(wrong) < self.count:
            raise InsufficientOptionsError(
                f"Need {self.count} wrong options, but only found {len(wrong)}"
            )

        # Take only the number we need and shuffle
        options = [correct] + wrong[: self.count]
        random.shuffle(options)

        return {
            "correct_answer": correct,
            "options": options,
            "correct_index": options.index(correct),
        }

    def _get_answer_field(self, card) -> str:
        """Get the answer text based on direction."""
        if self.direction == "lux_to_eng":
            return card.english
        else:
            return card.luxembourgish

    def _get_wrong_options(self) -> list[str]:
        """
        Get wrong options using priority cascade.

        Returns list of unique wrong answer strings.
        """
        correct_answer = self._get_answer_field(self.card)
        wrong_options: set[str] = set()

        # Priority 1: Same topic, same difficulty
        options = self._get_candidates_same_topic_same_difficulty()
        for card in options:
            answer = self._get_answer_field(card)
            if answer != correct_answer:
                wrong_options.add(answer)

        if len(wrong_options) >= self.count:
            return list(wrong_options)

        # Priority 2: Same topic, any difficulty
        options = self._get_candidates_same_topic_any_difficulty()
        for card in options:
            answer = self._get_answer_field(card)
            if answer != correct_answer:
                wrong_options.add(answer)

        if len(wrong_options) >= self.count:
            return list(wrong_options)

        # Priority 3: Any topic, same difficulty
        options = self._get_candidates_any_topic_same_difficulty()
        for card in options:
            answer = self._get_answer_field(card)
            if answer != correct_answer:
                wrong_options.add(answer)

        if len(wrong_options) >= self.count:
            return list(wrong_options)

        # Priority 4: Any card (fallback)
        options = self._get_candidates_any_card()
        for card in options:
            answer = self._get_answer_field(card)
            if answer != correct_answer:
                wrong_options.add(answer)

        return list(wrong_options)

    def _get_candidates_same_topic_same_difficulty(self) -> list:
        """Priority 1: Same topic, same difficulty."""
        topics = self.card.topics.all()
        if not topics.exists():
            return []

        return list(
            VocabularyCard.objects.filter(
                topics__in=topics,
                difficulty_level=self.card.difficulty_level,
                is_active=True,
            )
            .exclude(pk=self.card.pk)
            .distinct()
        )

    def _get_candidates_same_topic_any_difficulty(self) -> list:
        """Priority 2: Same topic, any difficulty."""
        topics = self.card.topics.all()
        if not topics.exists():
            return []

        return list(
            VocabularyCard.objects.filter(
                topics__in=topics,
                is_active=True,
            )
            .exclude(pk=self.card.pk)
            .exclude(difficulty_level=self.card.difficulty_level)
            .distinct()
        )

    def _get_candidates_any_topic_same_difficulty(self) -> list:
        """Priority 3: Any topic, same difficulty."""
        # Exclude cards from same topics
        topics = self.card.topics.all()

        queryset = VocabularyCard.objects.filter(
            difficulty_level=self.card.difficulty_level,
            is_active=True,
        ).exclude(pk=self.card.pk)

        if topics.exists():
            queryset = queryset.exclude(topics__in=topics)

        return list(queryset.distinct())

    def _get_candidates_any_card(self) -> list:
        """Priority 4: Fallback to any card."""
        return list(
            VocabularyCard.objects.filter(is_active=True)
            .exclude(pk=self.card.pk)
            .distinct()[:20]  # Limit for performance
        )
