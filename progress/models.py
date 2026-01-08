from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class CardProgressManager(models.Manager):
    """Custom manager for CardProgress with useful querysets."""

    def due_for_review(self):
        """Return cards that are due for review."""
        return self.filter(next_review__lte=timezone.now())

    def for_card(self, card):
        """Get progress for a specific card."""
        content_type = ContentType.objects.get_for_model(card)
        return self.filter(card_content_type=content_type, card_object_id=card.id)


class CardProgress(models.Model):
    """Tracks a user's progress on a specific flashcard."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="card_progress",
    )

    # Generic foreign key to support both VocabularyCard and PhraseCard
    card_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    card_object_id = models.PositiveIntegerField()
    card = GenericForeignKey("card_content_type", "card_object_id")

    # Progress tracking
    times_shown = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)

    # Spaced repetition fields (SM-2 algorithm)
    ease_factor = models.FloatField(default=2.5)  # Initial ease factor
    interval = models.IntegerField(default=0)  # Days until next review
    repetitions = models.IntegerField(default=0)  # Successful repetitions in a row

    # Timestamps
    last_shown = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CardProgressManager()

    class Meta:
        unique_together = ("user", "card_content_type", "card_object_id")
        verbose_name = "Card Progress"
        verbose_name_plural = "Card Progress"

    def __str__(self):
        return f"{self.user.username} - {self.card}"

    def accuracy(self):
        """Calculate accuracy percentage for this card."""
        total = self.times_correct + self.times_incorrect
        if total == 0:
            return 0
        return round((self.times_correct / total) * 100)


class ReviewDirection(models.TextChoices):
    """Direction of card review."""

    LUX_TO_ENG = "lux_to_eng", "Luxembourgish to English"
    ENG_TO_LUX = "eng_to_lux", "English to Luxembourgish"


class ReviewHistory(models.Model):
    """Records each individual review of a flashcard."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_history",
    )

    # Generic foreign key to support both card types
    card_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    card_object_id = models.PositiveIntegerField()
    card = GenericForeignKey("card_content_type", "card_object_id")

    direction = models.CharField(
        max_length=20,
        choices=ReviewDirection.choices,
        default=ReviewDirection.LUX_TO_ENG,
    )
    user_answer = models.CharField(max_length=500)
    was_correct = models.BooleanField()
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reviewed_at"]
        verbose_name = "Review History"
        verbose_name_plural = "Review History"

    def __str__(self):
        status = "✓" if self.was_correct else "✗"
        return f"{self.user.username} - {self.card} [{status}]"


class UserStats(models.Model):
    """Aggregate statistics for a user's learning progress."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stats",
    )
    total_cards_studied = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_incorrect = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)  # Consecutive days
    longest_streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "User Stats"
        verbose_name_plural = "User Stats"

    def __str__(self):
        return f"Stats for {self.user.username}"

    def accuracy(self):
        """Calculate overall accuracy percentage."""
        total = self.total_correct + self.total_incorrect
        if total == 0:
            return 0
        return round((self.total_correct / total) * 100)


class TopicProgress(models.Model):
    """Tracks a user's progress on a specific topic."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topic_progress",
    )
    topic = models.ForeignKey(
        "cards.Topic",
        on_delete=models.CASCADE,
        related_name="user_progress",
    )
    cards_seen = models.IntegerField(default=0)
    cards_mastered = models.IntegerField(default=0)  # High accuracy cards
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "topic")
        verbose_name = "Topic Progress"
        verbose_name_plural = "Topic Progress"

    def __str__(self):
        return f"{self.user.username} - {self.topic.name}"

    def completion_percentage(self):
        """Calculate completion percentage for this topic."""
        total_cards = self.topic.get_card_count()
        if total_cards == 0:
            return 0
        return min(round((self.cards_seen / total_cards) * 100), 100)


# Signal to create UserStats when a new user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_stats(sender, instance, created, **kwargs):
    if created:
        UserStats.objects.create(user=instance)
