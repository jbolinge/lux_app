"""
Management command to load sample Luxembourgish learning data.
"""

from django.core.management.base import BaseCommand

from cards.models import (
    DifficultyLevel,
    PhraseCard,
    RegisterChoice,
    Topic,
    VocabularyCard,
)

# Aliases for readability and line length
BEGINNER = DifficultyLevel.BEGINNER
INTERMEDIATE = DifficultyLevel.INTERMEDIATE
ADVANCED = DifficultyLevel.ADVANCED


class Command(BaseCommand):
    help = "Load sample Luxembourgish vocabulary and phrases"

    def handle(self, *args, **options):
        self.stdout.write("Loading sample data...")

        # Create topics
        topics = self._create_topics()

        # Create vocabulary cards
        vocab_count = self._create_vocabulary(topics)

        # Create phrase cards
        phrase_count = self._create_phrases(topics)

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {len(topics)} topics, {vocab_count} vocabulary cards, "
                f"and {phrase_count} phrase cards"
            )
        )

    def _create_topics(self):
        """Create topic hierarchy."""
        topics = {}

        # Main topics
        basics = Topic.objects.get_or_create(
            name="Basics",
            defaults={
                "description": "Essential words and phrases for beginners",
                "difficulty_level": BEGINNER,
                "order": 1,
            },
        )[0]
        topics["basics"] = basics

        greetings = Topic.objects.get_or_create(
            name="Greetings",
            defaults={
                "description": "Common greetings and farewells",
                "difficulty_level": BEGINNER,
                "order": 2,
                "parent": basics,
            },
        )[0]
        topics["greetings"] = greetings

        numbers = Topic.objects.get_or_create(
            name="Numbers",
            defaults={
                "description": "Numbers and counting",
                "difficulty_level": BEGINNER,
                "order": 3,
                "parent": basics,
            },
        )[0]
        topics["numbers"] = numbers

        colors = Topic.objects.get_or_create(
            name="Colors",
            defaults={
                "description": "Colors in Luxembourgish",
                "difficulty_level": BEGINNER,
                "order": 4,
            },
        )[0]
        topics["colors"] = colors

        food = Topic.objects.get_or_create(
            name="Food & Drink",
            defaults={
                "description": "Vocabulary for food and beverages",
                "difficulty_level": BEGINNER,
                "order": 5,
            },
        )[0]
        topics["food"] = food

        family = Topic.objects.get_or_create(
            name="Family",
            defaults={
                "description": "Family members and relationships",
                "difficulty_level": BEGINNER,
                "order": 6,
            },
        )[0]
        topics["family"] = family

        daily = Topic.objects.get_or_create(
            name="Daily Life",
            defaults={
                "description": "Common words for everyday situations",
                "difficulty_level": INTERMEDIATE,
                "order": 7,
            },
        )[0]
        topics["daily"] = daily

        travel = Topic.objects.get_or_create(
            name="Travel",
            defaults={
                "description": "Vocabulary for getting around",
                "difficulty_level": INTERMEDIATE,
                "order": 8,
            },
        )[0]
        topics["travel"] = travel

        return topics

    def _create_vocabulary(self, topics):
        """Create vocabulary cards."""
        vocab_data = [
            # Greetings
            ("Moien", "Hello", topics["greetings"], BEGINNER),
            ("Äddi", "Goodbye", topics["greetings"], BEGINNER),
            ("Merci", "Thank you", topics["greetings"], BEGINNER),
            ("Wann ech gelift", "Please", topics["greetings"], BEGINNER),
            ("Jo", "Yes", topics["basics"], BEGINNER),
            ("Nee", "No", topics["basics"], BEGINNER),
            # Numbers
            ("eent", "one", topics["numbers"], BEGINNER),
            ("zwee", "two", topics["numbers"], BEGINNER),
            ("dräi", "three", topics["numbers"], BEGINNER),
            ("véier", "four", topics["numbers"], BEGINNER),
            ("fënnef", "five", topics["numbers"], BEGINNER),
            ("sechs", "six", topics["numbers"], BEGINNER),
            ("siwen", "seven", topics["numbers"], BEGINNER),
            ("aacht", "eight", topics["numbers"], BEGINNER),
            ("néng", "nine", topics["numbers"], BEGINNER),
            ("zéng", "ten", topics["numbers"], BEGINNER),
            # Colors
            ("rout", "red", topics["colors"], BEGINNER),
            ("blo", "blue", topics["colors"], BEGINNER),
            ("gréng", "green", topics["colors"], BEGINNER),
            ("giel", "yellow", topics["colors"], BEGINNER),
            ("schwaarz", "black", topics["colors"], BEGINNER),
            ("wäiss", "white", topics["colors"], BEGINNER),
            # Food
            ("Brout", "bread", topics["food"], BEGINNER),
            ("Waasser", "water", topics["food"], BEGINNER),
            ("Mëllech", "milk", topics["food"], BEGINNER),
            ("Kaffi", "coffee", topics["food"], BEGINNER),
            ("Téi", "tea", topics["food"], BEGINNER),
            ("Äppel", "apple", topics["food"], BEGINNER),
            ("Fleesch", "meat", topics["food"], INTERMEDIATE),
            ("Geméis", "vegetables", topics["food"], INTERMEDIATE),
            # Family
            ("Mamm", "mother", topics["family"], BEGINNER),
            ("Papp", "father", topics["family"], BEGINNER),
            ("Brudder", "brother", topics["family"], BEGINNER),
            ("Schwëster", "sister", topics["family"], BEGINNER),
            ("Kand", "child", topics["family"], BEGINNER),
            ("Grousspapp", "grandfather", topics["family"], INTERMEDIATE),
            ("Groussmamm", "grandmother", topics["family"], INTERMEDIATE),
            # Daily Life
            ("Haus", "house", topics["daily"], BEGINNER),
            ("Dësch", "table", topics["daily"], BEGINNER),
            ("Stull", "chair", topics["daily"], BEGINNER),
            ("Bett", "bed", topics["daily"], BEGINNER),
            ("Fënster", "window", topics["daily"], INTERMEDIATE),
            ("Dier", "door", topics["daily"], INTERMEDIATE),
            # Travel
            ("Auto", "car", topics["travel"], BEGINNER),
            ("Bus", "bus", topics["travel"], BEGINNER),
            ("Zuch", "train", topics["travel"], BEGINNER),
            ("Gare", "train station", topics["travel"], INTERMEDIATE),
            ("Flughafen", "airport", topics["travel"], INTERMEDIATE),
        ]

        count = 0
        for lux, eng, topic, difficulty in vocab_data:
            card, created = VocabularyCard.objects.get_or_create(
                luxembourgish=lux,
                english=eng,
                defaults={"difficulty_level": difficulty},
            )
            if created:
                card.topics.add(topic)
                count += 1

        return count

    def _create_phrases(self, topics):
        """Create phrase cards.

        All phrases are ADVANCED difficulty (text input for sentences).
        """
        phrase_data = [
            # Greetings
            (
                "Wéi geet et?",
                "How are you?",
                topics["greetings"],
                RegisterChoice.INFORMAL,
            ),
            (
                "Mir geet et gutt",
                "I am fine",
                topics["greetings"],
                RegisterChoice.NEUTRAL,
            ),
            (
                "Wéi geet et Iech?",
                "How are you? (formal)",
                topics["greetings"],
                RegisterChoice.FORMAL,
            ),
            (
                "Ech si frou Iech kennenzeléieren",
                "Nice to meet you",
                topics["greetings"],
                RegisterChoice.FORMAL,
            ),
            (
                "Bis muer",
                "See you tomorrow",
                topics["greetings"],
                RegisterChoice.INFORMAL,
            ),
            (
                "Schéinen Dag nach",
                "Have a nice day",
                topics["greetings"],
                RegisterChoice.NEUTRAL,
            ),
            # Basics
            (
                "Wéi heescht Dir?",
                "What is your name? (formal)",
                topics["basics"],
                RegisterChoice.FORMAL,
            ),
            (
                "Ech heeschen...",
                "My name is...",
                topics["basics"],
                RegisterChoice.NEUTRAL,
            ),
            (
                "Ech verstinn net",
                "I don't understand",
                topics["basics"],
                RegisterChoice.NEUTRAL,
            ),
            (
                "Kënnt Dir dat widderhuelen?",
                "Can you repeat that?",
                topics["basics"],
                RegisterChoice.FORMAL,
            ),
            (
                "Schwätzt Dir Englesch?",
                "Do you speak English?",
                topics["basics"],
                RegisterChoice.FORMAL,
            ),
            # Food
            (
                "Ech hunn Honger",
                "I am hungry",
                topics["food"],
                RegisterChoice.NEUTRAL,
            ),
            (
                "Ech hunn Duuscht",
                "I am thirsty",
                topics["food"],
                RegisterChoice.NEUTRAL,
            ),
            (
                "D'Rechnung, wann ech gelift",
                "The bill, please",
                topics["food"],
                RegisterChoice.FORMAL,
            ),
            # Travel
            (
                "Wou ass...?",
                "Where is...?",
                topics["travel"],
                RegisterChoice.NEUTRAL,
            ),
            (
                "Wéi wäit ass et?",
                "How far is it?",
                topics["travel"],
                RegisterChoice.NEUTRAL,
            ),
            (
                "Ech géif gär eng Kaart",
                "I would like a ticket",
                topics["travel"],
                RegisterChoice.FORMAL,
            ),
        ]

        count = 0
        for lux, eng, topic, register in phrase_data:
            card, created = PhraseCard.objects.get_or_create(
                luxembourgish=lux,
                english=eng,
                defaults={"difficulty_level": ADVANCED, "register": register},
            )
            if created:
                card.topics.add(topic)
                count += 1

        return count
