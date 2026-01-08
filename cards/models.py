from django.db import models
from django.utils.text import slugify


class DifficultyLevel(models.IntegerChoices):
    """Difficulty levels for topics and cards."""

    BEGINNER = 1, "Beginner"
    INTERMEDIATE = 2, "Intermediate"
    ADVANCED = 3, "Advanced"


class Topic(models.Model):
    """Hierarchical topic for organizing flashcards."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    difficulty_level = models.IntegerField(
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER,
    )
    order = models.IntegerField(default=0, help_text="Order in curriculum")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Topic.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_all_cards(self):
        """Return all cards in this topic (vocabulary and phrases)."""
        vocab = list(self.vocabularycard_set.filter(is_active=True))
        phrases = list(self.phrasecard_set.filter(is_active=True))
        return vocab + phrases

    def get_card_count(self):
        """Return total number of active cards in this topic."""
        return (
            self.vocabularycard_set.filter(is_active=True).count()
            + self.phrasecard_set.filter(is_active=True).count()
        )


class BaseCard(models.Model):
    """Abstract base model for all flashcard types."""

    luxembourgish = models.CharField(max_length=500)
    english = models.CharField(max_length=500)
    difficulty_level = models.IntegerField(
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.luxembourgish} = {self.english}"


class VocabularyCard(BaseCard):
    """Flashcard for vocabulary (single words)."""

    topics = models.ManyToManyField(Topic, blank=True)

    class Meta:
        verbose_name = "Vocabulary Card"
        verbose_name_plural = "Vocabulary Cards"


class RegisterChoice(models.TextChoices):
    """Language register choices for phrases."""

    NEUTRAL = "neutral", "Neutral"
    FORMAL = "formal", "Formal"
    INFORMAL = "informal", "Informal"


class PhraseCard(BaseCard):
    """Flashcard for phrases and sentences."""

    topics = models.ManyToManyField(Topic, blank=True)
    register = models.CharField(
        max_length=10,
        choices=RegisterChoice.choices,
        default=RegisterChoice.NEUTRAL,
        blank=True,
    )

    class Meta:
        verbose_name = "Phrase Card"
        verbose_name_plural = "Phrase Cards"
