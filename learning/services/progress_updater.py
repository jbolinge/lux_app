"""
Progress update service for recording user learning progress.
"""

from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from progress.models import CardProgress, ReviewHistory, TopicProgress, UserStats

from .spaced_repetition import SpacedRepetition


class ProgressUpdater:
    """Service for updating user progress after card reviews."""

    def __init__(self):
        self.sr = SpacedRepetition()

    def update(
        self,
        user,
        card,
        direction: str,
        user_answer: str,
        was_correct: bool,
    ) -> CardProgress:
        """
        Update all progress records after a card review.

        Args:
            user: The user who reviewed the card
            card: The card that was reviewed
            direction: Direction of review (lux_to_eng or eng_to_lux)
            user_answer: The user's answer
            was_correct: Whether the answer was correct

        Returns:
            Updated CardProgress instance
        """
        # Get or create CardProgress
        content_type = ContentType.objects.get_for_model(card)
        progress, created = CardProgress.objects.get_or_create(
            user=user,
            card_content_type=content_type,
            card_object_id=card.id,
        )

        # Calculate new spaced repetition values
        quality = self.sr.quality_from_correct(was_correct)
        sr_result = self.sr.calculate(
            quality=quality,
            ease_factor=progress.ease_factor,
            interval=progress.interval,
            repetitions=progress.repetitions,
        )

        # Update CardProgress
        progress.times_shown += 1
        if was_correct:
            progress.times_correct += 1
        else:
            progress.times_incorrect += 1

        progress.ease_factor = sr_result.ease_factor
        progress.interval = sr_result.interval
        progress.repetitions = sr_result.repetitions
        progress.next_review = sr_result.next_review
        progress.last_shown = timezone.now()
        progress.save()

        # Create ReviewHistory entry
        ReviewHistory.objects.create(
            user=user,
            card_content_type=content_type,
            card_object_id=card.id,
            direction=direction,
            user_answer=user_answer,
            was_correct=was_correct,
        )

        # Update UserStats
        self._update_user_stats(user, was_correct, created)

        # Update TopicProgress for each topic the card belongs to
        for topic in card.topics.all():
            self._update_topic_progress(user, topic, created)

        return progress

    def _update_user_stats(self, user, was_correct: bool, is_new_card: bool):
        """Update the user's aggregate statistics."""
        stats, _ = UserStats.objects.get_or_create(user=user)

        if is_new_card:
            stats.total_cards_studied += 1

        if was_correct:
            stats.total_correct += 1
        else:
            stats.total_incorrect += 1

        # Update streak
        today = date.today()
        if stats.last_study_date:
            days_diff = (today - stats.last_study_date).days
            if days_diff == 1:
                # Consecutive day - increase streak
                stats.current_streak += 1
            elif days_diff > 1:
                # Missed days - reset streak
                stats.current_streak = 1
            # If days_diff == 0, same day - no change to streak
        else:
            # First time studying
            stats.current_streak = 1

        # Update longest streak
        if stats.current_streak > stats.longest_streak:
            stats.longest_streak = stats.current_streak

        stats.last_study_date = today
        stats.save()

    def _update_topic_progress(self, user, topic, is_new_card: bool):
        """Update progress for a specific topic."""
        progress, created = TopicProgress.objects.get_or_create(
            user=user,
            topic=topic,
        )

        if is_new_card:
            progress.cards_seen += 1

            # Check if topic is completed
            total_cards = topic.get_card_count()
            if progress.cards_seen >= total_cards and not progress.completed_at:
                progress.completed_at = timezone.now()

        progress.save()
