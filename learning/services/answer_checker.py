"""
Answer checking service for validating user responses.
"""

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class MatchQuality(str, Enum):
    """Quality of answer match."""

    EXACT = "exact"
    CLOSE = "close"  # Minor typos or case differences
    INCORRECT = "incorrect"


@dataclass
class CheckResult:
    """Result of answer checking."""

    is_correct: bool
    match_quality: str
    normalized_user: str
    normalized_correct: str


class AnswerChecker:
    """Service for checking user answers against correct answers."""

    def __init__(self, case_sensitive: bool = False, typo_tolerance: int = 1):
        """
        Initialize the answer checker.

        Args:
            case_sensitive: Whether to check case (default False)
            typo_tolerance: Number of character differences to allow (default 1)
        """
        self.case_sensitive = case_sensitive
        self.typo_tolerance = typo_tolerance

    def check(self, user_answer: str, correct_answer: str) -> dict:
        """
        Check a user's answer against the correct answer.

        Args:
            user_answer: The answer provided by the user
            correct_answer: The correct answer

        Returns:
            Dictionary with is_correct, match_quality, etc.
        """
        # Normalize both answers
        normalized_user = self._normalize(user_answer)
        normalized_correct = self._normalize(correct_answer)

        # Check for exact match
        if normalized_user == normalized_correct:
            return {
                "is_correct": True,
                "match_quality": MatchQuality.EXACT.value,
                "normalized_user": normalized_user,
                "normalized_correct": normalized_correct,
            }

        # Check for close match (within typo tolerance)
        distance = self._levenshtein_distance(normalized_user, normalized_correct)
        if distance <= self.typo_tolerance:
            return {
                "is_correct": True,
                "match_quality": MatchQuality.CLOSE.value,
                "normalized_user": normalized_user,
                "normalized_correct": normalized_correct,
            }

        # Check for alternative separators (e.g., "the house" vs "the/house")
        if self._check_alternatives(normalized_user, normalized_correct):
            return {
                "is_correct": True,
                "match_quality": MatchQuality.EXACT.value,
                "normalized_user": normalized_user,
                "normalized_correct": normalized_correct,
            }

        return {
            "is_correct": False,
            "match_quality": MatchQuality.INCORRECT.value,
            "normalized_user": normalized_user,
            "normalized_correct": normalized_correct,
        }

    def _normalize(self, text: str) -> str:
        """
        Normalize text for comparison.

        - Strips whitespace
        - Removes extra spaces
        - Optionally converts to lowercase
        - Normalizes unicode characters
        """
        # Strip and normalize whitespace
        text = " ".join(text.split())

        # Normalize unicode (handle accented characters)
        text = unicodedata.normalize("NFC", text)

        # Convert to lowercase if not case sensitive
        if not self.case_sensitive:
            text = text.lower()

        # Remove common punctuation that doesn't affect meaning
        text = re.sub(r"[.!?]$", "", text)

        return text

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings.

        This is the minimum number of single-character edits
        (insertions, deletions, or substitutions) required to
        change one string into the other.
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # j+1 since previous_row and current_row are one char longer
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _check_alternatives(self, user: str, correct: str) -> bool:
        """
        Check if user's answer matches any alternative in the correct answer.

        Handles cases like "the/a house" where either "the house" or "a house"
        would be correct.
        """
        # Check if correct answer contains alternatives
        if "/" in correct:
            # Try to reconstruct alternatives
            # This handles "the/a house" -> ["the house", "a house"]
            # Simple implementation: just check if user matches removing the slash
            alternatives = [correct.replace("/", " "), correct.replace("/", "")]
            for alt in alternatives:
                normalized_alt = self._normalize(alt)
                if user == normalized_alt:
                    return True
        return False
