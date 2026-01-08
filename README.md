# LearnLux

A flashcard-based web application for learning Luxembourgish.

## Features

- **Flashcard Learning**: Learn vocabulary and phrases through interactive flashcards
- **Bidirectional Practice**: Practice Luxembourgish → English and English → Luxembourgish
- **Spaced Repetition**: SM-2 algorithm for optimal learning retention
- **Progress Tracking**: Track your learning progress with detailed statistics
- **Topic Organization**: Content organized in hierarchical topics by difficulty
- **User Accounts**: Personal progress saved across sessions
- **Mobile-First Design**: Responsive design optimized for mobile learning
- **Django Admin**: Easy content management through Django's admin interface
- **CSV Import**: Bulk import vocabulary and phrases from CSV files

## Tech Stack

- **Backend**: Django 6.0+
- **Frontend**: Django Templates + Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production)
- **Testing**: pytest-django + Playwright
- **Package Manager**: uv

## Getting Started

### Prerequisites

- Python 3.12+
- uv package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd lux_app
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Run migrations:
   ```bash
   uv run python manage.py migrate
   ```

4. Load sample data (optional):
   ```bash
   uv run python manage.py load_sample_data
   ```

5. Create a superuser:
   ```bash
   uv run python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   uv run python manage.py runserver
   ```

7. Visit http://localhost:8000 in your browser

### Admin Access

Access the Django admin at http://localhost:8000/admin/ to manage:
- Topics (with hierarchical organization)
- Vocabulary cards
- Phrase cards
- User progress

## Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit

# Run integration tests
uv run pytest tests/integration

# Run with coverage
uv run pytest --cov
```

## Project Structure

```
lux_app/
├── accounts/          # User authentication app
├── cards/             # Flashcard content models
├── progress/          # Progress tracking models
├── learning/          # Learning engine and views
├── core/              # Shared functionality
├── templates/         # HTML templates
├── static/            # Static files
├── tests/             # Test suites
└── learnlux/          # Project configuration
```

## CSV Import Format

### Vocabulary Cards
```csv
luxembourgish,english,difficulty,topics
Moien,Hello,1,"Greetings,Basics"
```

### Phrase Cards
```csv
luxembourgish,english,difficulty,topics,register
Wéi geet et?,How are you?,1,"Greetings",informal
```

**Difficulty Levels**: 1=Beginner, 2=Intermediate, 3=Advanced

**Register Options**: neutral, formal, informal

## Contributing

1. Write tests first (TDD)
2. Make small, focused commits
3. Run tests before pushing
4. Follow the existing code style (ruff for formatting)

## License

MIT License
