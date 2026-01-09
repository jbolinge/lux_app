# CLAUDE.md - LearnLux Development Guide

## Project Overview

LearnLux is a flashcard-based web application for learning Luxembourgish. It uses spaced repetition (SM-2 algorithm) to optimize learning retention.

## Tech Stack

- **Backend**: Django 6.0+ with Python 3.12+
- **Frontend**: Django Templates + Tailwind CSS (CDN)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: pytest-django + Playwright
- **Package Manager**: uv
- **Linting**: ruff

## Quick Start

```bash
# Install dependencies
uv sync --extra dev

# Run migrations
uv run python manage.py migrate

# Load sample data (optional)
uv run python manage.py load_sample_data

# Run development server
uv run python manage.py runserver

# Create superuser for admin access
uv run python manage.py createsuperuser
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit

# Run integration tests
uv run pytest tests/integration

# Run e2e tests (requires Playwright browsers)
uv run playwright install --with-deps chromium
uv run pytest tests/e2e

# Run with coverage
uv run pytest --cov

# Run linting
uv run ruff check .
```

## Project Architecture

### Django Apps

- **accounts/** - User authentication and profiles
  - Custom User model with `display_name` field
  - Registration, login, logout, password reset

- **cards/** - Flashcard content models
  - `Topic` - Hierarchical topics with difficulty levels
  - `VocabularyCard` - Single word flashcards
  - `PhraseCard` - Phrase flashcards with language register (formal/informal/neutral)
  - Management commands: `import_cards`, `load_sample_data`

- **progress/** - Progress tracking models
  - `CardProgress` - Per-card progress with SM-2 spaced repetition data
  - `ReviewHistory` - Individual review records
  - `UserStats` - Aggregate user statistics (streaks, totals)
  - `TopicProgress` - Per-topic completion tracking

- **learning/** - Learning engine and views
  - Services in `learning/services/`:
    - `spaced_repetition.py` - SM-2 algorithm implementation
    - `card_selector.py` - Card selection logic
    - `answer_checker.py` - Answer validation
    - `progress_updater.py` - Progress updates
  - Views: dashboard, study, topics

- **core/** - Shared functionality and template tags

- **learnlux/** - Project configuration
  - Settings split: `base.py`, `development.py`, `production.py`

### Key URLs

- `/` - Dashboard (requires login)
- `/topics/` - Topic browser
- `/study/<topic_slug>/` - Study session
- `/accounts/login/` - Login
- `/accounts/register/` - Registration
- `/progress/statistics/` - User statistics
- `/admin/` - Django admin

### Database Models Relationships

```
User (accounts)
  └── UserStats (progress, 1:1)
  └── CardProgress (progress, 1:N) ──> VocabularyCard | PhraseCard (via GenericFK)
  └── ReviewHistory (progress, 1:N) ──> VocabularyCard | PhraseCard (via GenericFK)
  └── TopicProgress (progress, 1:N) ──> Topic

Topic (cards)
  └── parent (self-referential, hierarchical)
  └── VocabularyCard (M2M)
  └── PhraseCard (M2M)
```

## Settings

Development settings are used by default. Key settings:
- `DJANGO_SETTINGS_MODULE = "learnlux.settings.development"`
- Custom user model: `AUTH_USER_MODEL = "accounts.User"`
- Login redirects to dashboard: `LOGIN_REDIRECT_URL = "learning:dashboard"`

## Color Palette (Tailwind)

| Role | Class |
|------|-------|
| Primary | `teal-600` |
| Secondary | `orange-500` |
| Success | `green-500` |
| Error | `red-500` |
| Background | `slate-50` |
| Text | `slate-800` |

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

Difficulty: 1=Beginner, 2=Intermediate, 3=Advanced

## Test Fixtures

Common fixtures defined in `tests/conftest.py`:
- `client` - Django test client
- `authenticated_client` - Logged-in test client
- `user` - Test user (testuser@example.com)
- `admin_user` - Admin user

## CI/CD

GitHub Actions workflow in `.github/workflows/ci.yml`:
- Runs on push/PR to main and develop
- Runs ruff linting
- Runs unit and integration tests
- Installs Playwright and runs e2e tests
