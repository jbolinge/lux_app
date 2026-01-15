"""
Management command to import flashcards from CSV files.

CSV Format for Vocabulary:
    luxembourgish,english,difficulty,topics
    Moien,Hello,1,"Greetings,Basics"

CSV Format for Phrases:
    luxembourgish,english,difficulty,topics,register
    Wéi geet et?,How are you?,1,"Greetings,Basics",informal

Difficulty levels: 1=Beginner, 2=Intermediate, 3=Advanced
Note: VocabularyCards are restricted to BEGINNER/INTERMEDIATE difficulty.
      PhraseCards support all difficulty levels (BEGINNER, INTERMEDIATE, ADVANCED).
Topics: Comma-separated list of topic names (will be created if they don't exist)
Register: neutral, formal, informal (phrases only)
"""

import csv

from django.core.management.base import BaseCommand, CommandError

from cards.models import (
    DifficultyLevel,
    PhraseCard,
    RegisterChoice,
    Topic,
    VocabularyCard,
)


class Command(BaseCommand):
    help = "Import flashcards from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--type",
            type=str,
            choices=["vocabulary", "phrase"],
            default="vocabulary",
            help="Type of cards to import (default: vocabulary)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse the file but don't save to database",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        card_type = options["type"]
        dry_run = options["dry_run"]

        self.stdout.write(f"Importing {card_type} cards from {file_path}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - no changes will be saved"))

        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                self._validate_headers(reader.fieldnames, card_type)

                created_count = 0
                skipped_count = 0
                error_count = 0

                # Row numbers start at 2 (1-indexed + header row)
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if card_type == "vocabulary":
                            created = self._import_vocabulary(row, dry_run)
                        else:
                            created = self._import_phrase(row, dry_run)

                        if created:
                            created_count += 1
                        else:
                            skipped_count += 1

                    except Exception as e:
                        error_count += 1
                        self.stderr.write(
                            self.style.ERROR(f"Row {row_num}: {str(e)}")
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Import complete: {created_count} created, "
                        f"{skipped_count} skipped, {error_count} errors"
                    )
                )

        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")
        except csv.Error as e:
            raise CommandError(f"CSV error: {str(e)}")

    def _validate_headers(self, fieldnames, card_type):
        """Validate CSV headers."""
        required = {"luxembourgish", "english"}
        if not required.issubset(set(fieldnames)):
            raise CommandError(
                f"CSV must contain columns: {', '.join(required)}"
            )

    def _get_or_create_topics(self, topic_names: str) -> list:
        """Get or create topics from comma-separated string."""
        if not topic_names:
            return []

        topics = []
        for name in topic_names.split(","):
            name = name.strip()
            if name:
                topic, _ = Topic.objects.get_or_create(
                    name=name,
                    defaults={"difficulty_level": DifficultyLevel.BEGINNER},
                )
                topics.append(topic)
        return topics

    def _get_vocabulary_difficulty(self, value: str) -> int:
        """Convert difficulty string to integer for vocabulary cards.

        VocabularyCards are restricted to BEGINNER and INTERMEDIATE only.
        ADVANCED difficulty is not allowed and will default to INTERMEDIATE.
        """
        if not value:
            return DifficultyLevel.BEGINNER
        try:
            level = int(value)
            if level == DifficultyLevel.BEGINNER:
                return DifficultyLevel.BEGINNER
            if level in [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]:
                # Cap at INTERMEDIATE since VocabularyCard cannot be ADVANCED
                return DifficultyLevel.INTERMEDIATE
        except ValueError:
            pass
        return DifficultyLevel.BEGINNER

    def _get_phrase_difficulty(self, value: str) -> int:
        """Convert difficulty string to integer for phrase cards.

        PhraseCards support all difficulty levels (BEGINNER, INTERMEDIATE, ADVANCED).
        Defaults to BEGINNER if not specified or invalid.
        """
        if not value:
            return DifficultyLevel.BEGINNER
        try:
            level = int(value)
            if level in [
                DifficultyLevel.BEGINNER,
                DifficultyLevel.INTERMEDIATE,
                DifficultyLevel.ADVANCED,
            ]:
                return level
        except ValueError:
            pass
        return DifficultyLevel.BEGINNER

    def _import_vocabulary(self, row: dict, dry_run: bool) -> bool:
        """Import a vocabulary card from a CSV row."""
        luxembourgish = row.get("luxembourgish", "").strip()
        english = row.get("english", "").strip()

        if not luxembourgish or not english:
            return False

        # Check if card already exists
        if VocabularyCard.objects.filter(
            luxembourgish=luxembourgish,
            english=english,
        ).exists():
            return False

        if dry_run:
            self.stdout.write(f"Would create: {luxembourgish} = {english}")
            return True

        card = VocabularyCard.objects.create(
            luxembourgish=luxembourgish,
            english=english,
            difficulty_level=self._get_vocabulary_difficulty(row.get("difficulty", "")),
        )

        topics = self._get_or_create_topics(row.get("topics", ""))
        if topics:
            card.topics.set(topics)

        return True

    def _import_phrase(self, row: dict, dry_run: bool) -> bool:
        """Import a phrase card from a CSV row.

        PhraseCards support all difficulty levels (BEGINNER, INTERMEDIATE, ADVANCED).
        """
        luxembourgish = row.get("luxembourgish", "").strip()
        english = row.get("english", "").strip()

        if not luxembourgish or not english:
            return False

        # Check if card already exists
        if PhraseCard.objects.filter(
            luxembourgish=luxembourgish,
            english=english,
        ).exists():
            return False

        # Get register
        register = row.get("register", "").strip().lower()
        if register not in [r.value for r in RegisterChoice]:
            register = RegisterChoice.NEUTRAL

        if dry_run:
            self.stdout.write(f"Would create: {luxembourgish} = {english}")
            return True

        card = PhraseCard.objects.create(
            luxembourgish=luxembourgish,
            english=english,
            difficulty_level=self._get_phrase_difficulty(row.get("difficulty", "")),
            register=register,
        )

        topics = self._get_or_create_topics(row.get("topics", ""))
        if topics:
            card.topics.set(topics)

        return True
