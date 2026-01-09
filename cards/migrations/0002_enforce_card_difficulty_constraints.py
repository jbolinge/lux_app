"""
Migration to enforce card type difficulty constraints.

This migration fixes any existing data that violates the new constraints:
- VocabularyCard: ADVANCED -> INTERMEDIATE
- PhraseCard: BEGINNER/INTERMEDIATE -> ADVANCED
"""

from django.db import migrations


def migrate_invalid_cards(apps, schema_editor):
    """
    Migrate existing cards to comply with new difficulty rules:
    - VocabularyCard ADVANCED -> convert to INTERMEDIATE
    - PhraseCard BEGINNER/INTERMEDIATE -> convert to ADVANCED
    """
    VocabularyCard = apps.get_model("cards", "VocabularyCard")
    PhraseCard = apps.get_model("cards", "PhraseCard")

    # Difficulty level constants (matching DifficultyLevel enum)
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3

    # Downgrade advanced vocabulary to intermediate
    vocab_updated = VocabularyCard.objects.filter(difficulty_level=ADVANCED).update(
        difficulty_level=INTERMEDIATE
    )

    # Upgrade non-advanced phrases to advanced
    phrase_updated = PhraseCard.objects.filter(
        difficulty_level__in=[BEGINNER, INTERMEDIATE]
    ).update(difficulty_level=ADVANCED)

    if vocab_updated or phrase_updated:
        print(
            f"\nMigrated {vocab_updated} vocabulary cards (ADVANCED -> INTERMEDIATE) "
            f"and {phrase_updated} phrase cards (to ADVANCED)"
        )


def reverse_migration(apps, schema_editor):
    """Reverse migration is a no-op - we can't know what the original values were."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_invalid_cards, reverse_migration),
    ]
