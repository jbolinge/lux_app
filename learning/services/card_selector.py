"""
Card selection service for determining which cards to show users.

Implements a mix of new cards and review cards based on spaced repetition.
"""

import random
from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from cards.models import PhraseCard, Topic, VocabularyCard
from progress.models import CardProgress


class CardSelector:
    """Service for selecting the next card for a user to study."""

    # Ratio of review cards to new cards (e.g., 0.3 = 30% review, 70% new)
    REVIEW_RATIO = 0.3

    def __init__(self, user):
        """
        Initialize the card selector for a specific user.

        Args:
            user: The user to select cards for
        """
        self.user = user

    def get_next_card(
        self,
        topic_id: Optional[int] = None,
        direction: str = "lux_to_eng",
    ):
        """
        Get the next card for the user to study.

        Implements a mix strategy:
        - Review cards that are due (based on spaced repetition)
        - New cards from the current topic or curriculum

        Args:
            topic_id: Optional specific topic to study
            direction: Direction of study (lux_to_eng or eng_to_lux)

        Returns:
            A VocabularyCard or PhraseCard instance, or None if no cards available
        """
        # Decide whether to show a review card or new card
        if random.random() < self.REVIEW_RATIO:
            card = self._get_review_card(topic_id)
            if card:
                return card

        # Try to get a new card
        card = self._get_new_card(topic_id)
        if card:
            return card

        # Fall back to review card if no new cards available
        return self._get_review_card(topic_id)

    def _get_review_card(self, topic_id: Optional[int] = None):
        """
        Get a card that is due for review.

        Args:
            topic_id: Optional topic filter

        Returns:
            A card due for review, or None
        """
        # Get all cards due for review
        due_progress = CardProgress.objects.filter(
            user=self.user,
            next_review__lte=timezone.now(),
        ).order_by("next_review")

        if topic_id:
            # Filter by topic - need to check card's topics
            topic = Topic.objects.get(pk=topic_id)
            due_progress = self._filter_by_topic(due_progress, topic)

        # Get a random due card (to add variety)
        due_list = list(due_progress[:20])  # Limit to prevent loading too many
        if due_list:
            progress = random.choice(due_list)
            return progress.card

        return None

    def _get_new_card(self, topic_id: Optional[int] = None):
        """
        Get a card the user hasn't seen yet.

        Args:
            topic_id: Optional topic filter

        Returns:
            A new card, or None
        """
        # Get all cards the user has seen
        seen_vocab_ids = set(
            CardProgress.objects.filter(
                user=self.user,
                card_content_type=ContentType.objects.get_for_model(VocabularyCard),
            ).values_list("card_object_id", flat=True)
        )

        seen_phrase_ids = set(
            CardProgress.objects.filter(
                user=self.user,
                card_content_type=ContentType.objects.get_for_model(PhraseCard),
            ).values_list("card_object_id", flat=True)
        )

        # Get unseen cards
        vocab_queryset = VocabularyCard.objects.filter(is_active=True).exclude(
            id__in=seen_vocab_ids
        )
        phrase_queryset = PhraseCard.objects.filter(is_active=True).exclude(
            id__in=seen_phrase_ids
        )

        if topic_id:
            topic = Topic.objects.get(pk=topic_id)
            vocab_queryset = vocab_queryset.filter(topics=topic)
            phrase_queryset = phrase_queryset.filter(topics=topic)

        # Order by difficulty (beginner first) then by creation date
        vocab_queryset = vocab_queryset.order_by("difficulty_level", "created_at")
        phrase_queryset = phrase_queryset.order_by("difficulty_level", "created_at")

        # Get the first available card (vocabulary preferred, then phrases)
        vocab_card = vocab_queryset.first()
        phrase_card = phrase_queryset.first()

        if vocab_card and phrase_card:
            # Randomly choose between vocab and phrase
            return random.choice([vocab_card, phrase_card])
        return vocab_card or phrase_card

    def _filter_by_topic(self, progress_queryset, topic: Topic):
        """
        Filter a CardProgress queryset by topic.

        This is more complex because we need to check the card's topics.
        """
        # Get card IDs that belong to the topic
        vocab_ids = set(
            VocabularyCard.objects.filter(topics=topic, is_active=True).values_list(
                "id", flat=True
            )
        )
        phrase_ids = set(
            PhraseCard.objects.filter(topics=topic, is_active=True).values_list(
                "id", flat=True
            )
        )

        vocab_ct = ContentType.objects.get_for_model(VocabularyCard)
        phrase_ct = ContentType.objects.get_for_model(PhraseCard)

        # Filter progress by these card IDs
        from django.db.models import Q

        return progress_queryset.filter(
            Q(card_content_type=vocab_ct, card_object_id__in=vocab_ids)
            | Q(card_content_type=phrase_ct, card_object_id__in=phrase_ids)
        )

    def get_session_cards(
        self,
        topic_id: Optional[int] = None,
        count: int = 10,
    ) -> list:
        """
        Get a batch of cards for a study session.

        Args:
            topic_id: Optional topic filter
            count: Number of cards to return

        Returns:
            List of cards for the session
        """
        cards = []
        seen_ids = set()

        for _ in range(count * 2):  # Try more to account for duplicates
            card = self.get_next_card(topic_id)
            if card and card.id not in seen_ids:
                cards.append(card)
                seen_ids.add(card.id)
            if len(cards) >= count:
                break

        return cards
