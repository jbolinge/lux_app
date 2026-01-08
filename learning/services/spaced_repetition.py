"""
Spaced Repetition implementation using the SM-2 algorithm.

The SM-2 algorithm calculates optimal review intervals based on user performance.
Quality scores range from 0-5:
    0 - Complete blackout, no memory
    1 - Incorrect, but recognized after seeing answer
    2 - Incorrect, but answer seemed easy to recall
    3 - Correct with serious difficulty
    4 - Correct with some hesitation
    5 - Perfect response
"""

from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone


@dataclass
class SM2Result:
    """Result of SM-2 calculation."""

    ease_factor: float
    interval: int  # Days until next review
    repetitions: int
    next_review: timezone.datetime


class SpacedRepetition:
    """Implements the SM-2 spaced repetition algorithm."""

    MIN_EASE_FACTOR = 1.3
    INITIAL_EASE_FACTOR = 2.5

    def calculate(
        self,
        quality: int,
        ease_factor: float,
        interval: int,
        repetitions: int,
    ) -> SM2Result:
        """
        Calculate new SM-2 values based on response quality.

        Args:
            quality: Quality of response (0-5)
            ease_factor: Current ease factor
            interval: Current interval in days
            repetitions: Number of successful repetitions

        Returns:
            SM2Result with updated values
        """
        # Clamp quality to valid range
        quality = max(0, min(5, quality))

        # Calculate new ease factor
        new_ease_factor = ease_factor + (
            0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        )
        new_ease_factor = max(self.MIN_EASE_FACTOR, new_ease_factor)

        # Calculate new interval and repetitions
        if quality < 3:
            # Failed - reset repetitions, short interval
            new_repetitions = 0
            new_interval = 1
        else:
            # Success - increase repetitions
            new_repetitions = repetitions + 1

            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = round(interval * new_ease_factor)

        # Calculate next review date
        next_review = timezone.now() + timedelta(days=new_interval)

        return SM2Result(
            ease_factor=new_ease_factor,
            interval=new_interval,
            repetitions=new_repetitions,
            next_review=next_review,
        )

    def quality_from_correct(self, was_correct: bool, response_time_ms: int = 0) -> int:
        """
        Convert a simple correct/incorrect to SM-2 quality score.

        For simplicity, we use:
        - Correct: quality 4 (correct with some hesitation)
        - Incorrect: quality 1 (incorrect but recognized)

        Args:
            was_correct: Whether the answer was correct
            response_time_ms: Optional response time in milliseconds

        Returns:
            Quality score (0-5)
        """
        if was_correct:
            # Could adjust based on response time in future
            return 4
        else:
            return 1
