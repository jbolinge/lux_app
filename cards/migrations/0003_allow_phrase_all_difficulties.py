"""
Migration to document removal of PhraseCard ADVANCED-only constraint.

PhraseCards can now have any difficulty level (BEGINNER, INTERMEDIATE, ADVANCED)
to support the mastery-based learning progression where all cards start as
multiple choice and transition to text input after mastery.

No database changes required - this was a Python-level validation constraint.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cards", "0002_enforce_card_difficulty_constraints"),
    ]

    operations = []  # Python validation removed; no DB schema changes
