# LearnLux - Luxembourgish Language Learning Application

## Project Overview

**Application Name:** LearnLux
**Purpose:** A flashcard-based web application for learning Luxembourgish
**Tech Stack:** Django (latest), Python 3.12+, Tailwind CSS, SQLite (dev) / PostgreSQL (prod)
**Package Manager:** uv
**Testing:** pytest-django + Playwright
**CI/CD:** GitHub Actions

---

## Color Palette

| Role | Hex Code | Tailwind Class |
|------|----------|----------------|
| Primary (Teal) | `#0D9488` | `teal-600` |
| Secondary (Coral) | `#F97316` | `orange-500` |
| Success (Green) | `#22C55E` | `green-500` |
| Error (Red) | `#EF4444` | `red-500` |
| Warning (Yellow) | `#EAB308` | `yellow-500` |
| Background | `#F8FAFC` | `slate-50` |
| Surface | `#FFFFFF` | `white` |
| Text | `#1E293B` | `slate-800` |

---

## Phase 1: Project Foundation

### 1.1 Environment Setup
- [ ] Create Python virtual environment using uv
- [ ] Initialize uv project with pyproject.toml
- [ ] Install Django (latest version)
- [ ] Install development dependencies (pytest-django, playwright, etc.)
- [ ] Create .gitignore file
- [ ] Initialize git repository
- [ ] Create initial commit

### 1.2 Django Project Initialization
- [ ] Create Django project named `learnlux`
- [ ] Create initial Django app named `core` (for shared functionality)
- [ ] Configure settings for development environment
- [ ] Set up settings structure (base, development, production)
- [ ] Configure static files and templates directories
- [ ] Verify development server runs successfully
- [ ] Write first test to verify Django setup
- [ ] Commit: "Initialize Django project structure"

### 1.3 Testing Infrastructure
- [ ] Configure pytest-django in pyproject.toml
- [ ] Create pytest.ini or pyproject.toml pytest section
- [ ] Set up conftest.py with common fixtures
- [ ] Install and configure Playwright
- [ ] Create test directory structure:
  ```
  tests/
  ├── unit/
  ├── integration/
  └── e2e/
  ```
- [ ] Write sample test for each type to verify setup
- [ ] Commit: "Set up testing infrastructure"

### 1.4 GitHub Actions CI/CD
- [ ] Create `.github/workflows/ci.yml`
- [ ] Configure workflow to:
  - Run on push and pull requests
  - Set up Python environment with uv
  - Install dependencies
  - Run pytest (unit and integration)
  - Run Playwright e2e tests
- [ ] Test workflow with initial commit
- [ ] Commit: "Add GitHub Actions CI/CD pipeline"

### 1.5 Tailwind CSS Integration
- [ ] Install Tailwind CSS (CDN for development)
- [ ] Create base template with Tailwind
- [ ] Configure custom color palette in tailwind config
- [ ] Create mobile-first responsive layout structure
- [ ] Commit: "Integrate Tailwind CSS with custom theme"

---

## Phase 2: User Authentication System

### 2.1 Custom User Model
- [ ] Create `accounts` Django app
- [ ] Define custom User model extending AbstractUser
  - Add `display_name` field
- [ ] Write tests for custom User model
- [ ] Create and run migrations
- [ ] Register User model in admin
- [ ] Commit: "Add custom User model with display_name"

### 2.2 User Registration
- [ ] Write tests for registration view
- [ ] Create registration form using Django's UserCreationForm
- [ ] Create registration view (class-based)
- [ ] Create registration template (mobile-first)
- [ ] Add URL routing
- [ ] Verify tests pass
- [ ] Use Playwright MCP to verify styling
- [ ] Commit: "Implement user registration"

### 2.3 User Login/Logout
- [ ] Write tests for login/logout functionality
- [ ] Configure Django's built-in LoginView and LogoutView
- [ ] Create login template (mobile-first)
- [ ] Add URL routing
- [ ] Create navigation with login state
- [ ] Verify tests pass
- [ ] Use Playwright MCP to verify styling
- [ ] Commit: "Implement user login/logout"

### 2.4 Password Reset
- [ ] Write tests for password reset flow
- [ ] Configure Django's password reset views
- [ ] Create password reset templates:
  - Password reset form
  - Password reset done
  - Password reset confirm
  - Password reset complete
- [ ] Configure email backend (console for dev)
- [ ] Add URL routing
- [ ] Verify tests pass
- [ ] Commit: "Implement password reset via email"

### 2.5 User Profile
- [ ] Write tests for profile view and update
- [ ] Create profile view (display and edit display_name)
- [ ] Create profile template
- [ ] Add URL routing
- [ ] Verify tests pass
- [ ] Use Playwright MCP to verify styling
- [ ] Commit: "Implement user profile page"

---

## Phase 3: Content Models (Flashcards)

### 3.1 Topic Model
- [ ] Create `cards` Django app
- [ ] Write tests for Topic model
- [ ] Define Topic model:
  - `name` (CharField)
  - `slug` (SlugField, auto-generated)
  - `description` (TextField, optional)
  - `parent` (ForeignKey to self, nullable - for hierarchy)
  - `difficulty_level` (IntegerChoices: Beginner=1, Intermediate=2, Advanced=3)
  - `order` (IntegerField - for curriculum ordering)
  - `created_at`, `updated_at` (DateTimeFields)
- [ ] Create and run migrations
- [ ] Register in admin with hierarchy display
- [ ] Verify tests pass
- [ ] Commit: "Add Topic model with hierarchy support"

### 3.2 Card Base Model
- [ ] Write tests for Card model
- [ ] Define abstract BaseCard model:
  - `luxembourgish` (CharField)
  - `english` (CharField)
  - `topics` (ManyToManyField to Topic)
  - `difficulty_level` (IntegerChoices)
  - `created_at`, `updated_at` (DateTimeFields)
  - `is_active` (BooleanField, default=True)
- [ ] Verify tests pass
- [ ] Commit: "Add BaseCard abstract model"

### 3.3 Vocabulary Card Model
- [ ] Write tests for VocabularyCard model
- [ ] Define VocabularyCard model inheriting from BaseCard
  - (No additional fields needed per requirements)
- [ ] Create and run migrations
- [ ] Register in admin
- [ ] Verify tests pass
- [ ] Commit: "Add VocabularyCard model"

### 3.4 Phrase Card Model
- [ ] Write tests for PhraseCard model
- [ ] Define PhraseCard model inheriting from BaseCard:
  - `register` (CharField with choices: Neutral, Formal, Informal - nullable)
- [ ] Create and run migrations
- [ ] Register in admin
- [ ] Verify tests pass
- [ ] Commit: "Add PhraseCard model"

### 3.5 Admin Customization
- [ ] Enhance Topic admin:
  - List display with hierarchy indentation
  - Filtering by difficulty level
  - Search by name
- [ ] Enhance Card admins:
  - List display with topics, difficulty
  - Filtering by topics, difficulty, active status
  - Search by luxembourgish, english
  - Bulk actions (activate/deactivate)
- [ ] Write admin tests
- [ ] Commit: "Enhance Django admin for content management"

### 3.6 CSV Import Functionality
- [ ] Write tests for CSV import
- [ ] Create management command `import_cards`
  - Accept file path and card type arguments
  - Validate CSV format
  - Handle topics (create if not exist)
  - Report success/failure counts
- [ ] Add CSV import action to admin
- [ ] Document CSV format requirements
- [ ] Verify tests pass
- [ ] Commit: "Add CSV import for flashcards"

---

## Phase 4: User Progress Tracking

### 4.1 Card Progress Model
- [ ] Create `progress` Django app
- [ ] Write tests for CardProgress model
- [ ] Define CardProgress model:
  - `user` (ForeignKey to User)
  - `card_content_type` (ContentType for polymorphic cards)
  - `card_object_id` (PositiveIntegerField)
  - `card` (GenericForeignKey)
  - `times_shown` (IntegerField)
  - `times_correct` (IntegerField)
  - `times_incorrect` (IntegerField)
  - `last_shown` (DateTimeField)
  - `next_review` (DateTimeField - for spaced repetition)
  - `ease_factor` (FloatField - SM-2 algorithm)
  - `interval` (IntegerField - days until next review)
  - Unique constraint on (user, card_content_type, card_object_id)
- [ ] Create and run migrations
- [ ] Verify tests pass
- [ ] Commit: "Add CardProgress model for tracking"

### 4.2 Review History Model
- [ ] Write tests for ReviewHistory model
- [ ] Define ReviewHistory model:
  - `user` (ForeignKey to User)
  - `card_content_type` (ContentType)
  - `card_object_id` (PositiveIntegerField)
  - `card` (GenericForeignKey)
  - `direction` (CharField: 'lux_to_eng' or 'eng_to_lux')
  - `user_answer` (CharField)
  - `was_correct` (BooleanField)
  - `reviewed_at` (DateTimeField)
- [ ] Create and run migrations
- [ ] Verify tests pass
- [ ] Commit: "Add ReviewHistory model"

### 4.3 User Statistics Model
- [ ] Write tests for UserStats model
- [ ] Define UserStats model (or extend User):
  - `user` (OneToOneField to User)
  - `total_cards_studied` (IntegerField)
  - `total_correct` (IntegerField)
  - `total_incorrect` (IntegerField)
  - `current_streak` (IntegerField - consecutive days)
  - `longest_streak` (IntegerField)
  - `last_study_date` (DateField)
- [ ] Create and run migrations
- [ ] Add signal to create UserStats on User creation
- [ ] Verify tests pass
- [ ] Commit: "Add UserStats model"

### 4.4 Topic Progress Model
- [ ] Write tests for TopicProgress model
- [ ] Define TopicProgress model:
  - `user` (ForeignKey to User)
  - `topic` (ForeignKey to Topic)
  - `cards_seen` (IntegerField)
  - `cards_mastered` (IntegerField)
  - `started_at` (DateTimeField)
  - `completed_at` (DateTimeField, nullable)
  - Unique constraint on (user, topic)
- [ ] Create and run migrations
- [ ] Verify tests pass
- [ ] Commit: "Add TopicProgress model"

---

## Phase 5: Learning Engine

### 5.1 Spaced Repetition Algorithm
- [ ] Create `learning` Django app
- [ ] Write tests for SM-2 algorithm implementation
- [ ] Implement SM-2 algorithm:
  - Calculate ease factor based on response quality
  - Calculate next review interval
  - Handle "new", "learning", "review" card states
- [ ] Verify tests pass
- [ ] Commit: "Implement SM-2 spaced repetition algorithm"

### 5.2 Card Selection Service
- [ ] Write tests for card selection logic
- [ ] Implement CardSelector service:
  - Get cards due for review (based on next_review date)
  - Get new cards from current topic
  - Mix review cards with new cards (configurable ratio)
  - Respect difficulty progression
  - Handle both directions (lux→eng, eng→lux)
- [ ] Verify tests pass
- [ ] Commit: "Implement card selection service"

### 5.3 Answer Checking Service
- [ ] Write tests for answer checking
- [ ] Implement AnswerChecker service:
  - Exact match checking
  - Case-insensitive option
  - Handle common typos (optional, configurable)
  - Return match quality (correct, almost, incorrect)
- [ ] Verify tests pass
- [ ] Commit: "Implement answer checking service"

### 5.4 Progress Update Service
- [ ] Write tests for progress updates
- [ ] Implement ProgressUpdater service:
  - Update CardProgress after each review
  - Update UserStats (totals, streak)
  - Update TopicProgress
  - Create ReviewHistory entry
- [ ] Verify tests pass
- [ ] Commit: "Implement progress update service"

---

## Phase 6: Study Interface (Frontend)

### 6.1 Home/Dashboard Page
- [ ] Write tests for dashboard view
- [ ] Create dashboard view showing:
  - Welcome message with display name
  - Quick stats (cards due, streak, total studied)
  - Continue learning button
  - Topic overview
- [ ] Create mobile-first template
- [ ] Use Playwright MCP to verify styling
- [ ] Verify tests pass
- [ ] Commit: "Implement home dashboard"

### 6.2 Topic Browser
- [ ] Write tests for topic browser view
- [ ] Create topic list view:
  - Display hierarchical topics
  - Show difficulty level badges
  - Show user's progress per topic
  - Indicate recommended next topic
- [ ] Create mobile-first template
- [ ] Use Playwright MCP to verify styling
- [ ] Verify tests pass
- [ ] Commit: "Implement topic browser"

### 6.3 Flashcard Study View
- [ ] Write tests for study view
- [ ] Create study session view:
  - Display card (one side at a time)
  - Text input for answer
  - Submit and check answer
  - Show result (correct/incorrect)
  - Show correct answer if wrong
  - Next card button
  - Session progress indicator
- [ ] Create mobile-first template with:
  - Large, readable text
  - Easy-to-tap input
  - Clear visual feedback
- [ ] Use Playwright MCP to verify styling and interaction
- [ ] Verify tests pass
- [ ] Commit: "Implement flashcard study interface"

### 6.4 Study Session Flow
- [ ] Write tests for session flow
- [ ] Implement session management:
  - Start session (select topic or continue)
  - Track cards in session
  - Handle answer submission via AJAX (no page reload)
  - End session summary
- [ ] Create session summary template
- [ ] Use Playwright MCP to verify flow
- [ ] Verify tests pass
- [ ] Commit: "Implement study session flow"

### 6.5 AJAX/JavaScript Interactions
- [ ] Write e2e tests for JavaScript interactions
- [ ] Implement vanilla JavaScript for:
  - Answer submission without page reload
  - Card flip animation
  - Progress bar updates
  - Timer (optional, for future gamification)
- [ ] Ensure graceful degradation without JS
- [ ] Verify tests pass
- [ ] Commit: "Add JavaScript interactions for study flow"

---

## Phase 7: Progress Dashboard

### 7.1 Statistics Overview
- [ ] Write tests for stats view
- [ ] Create statistics view showing:
  - Total cards studied
  - Accuracy percentage
  - Current/longest streak
  - Cards due for review
- [ ] Create mobile-first template
- [ ] Use Playwright MCP to verify styling
- [ ] Verify tests pass
- [ ] Commit: "Implement statistics overview"

### 7.2 Progress Charts
- [ ] Write tests for chart data endpoints
- [ ] Integrate Chart.js or similar library
- [ ] Create charts for:
  - Cards studied over time (line chart)
  - Accuracy over time (line chart)
  - Cards per topic (bar chart)
  - Strength by topic (radar chart)
- [ ] Create mobile-friendly chart layouts
- [ ] Use Playwright MCP to verify display
- [ ] Verify tests pass
- [ ] Commit: "Add progress charts"

### 7.3 Per-Card History View
- [ ] Write tests for card history view
- [ ] Create view showing:
  - List of recently studied cards
  - Per-card accuracy
  - Last review date
  - Next scheduled review
  - Filter by topic
- [ ] Create mobile-first template
- [ ] Use Playwright MCP to verify styling
- [ ] Verify tests pass
- [ ] Commit: "Implement per-card history view"

### 7.4 Topic Progress View
- [ ] Write tests for topic progress view
- [ ] Create view showing:
  - Progress bars per topic
  - Mastery levels
  - Completion percentages
  - Recommended next topic
- [ ] Create mobile-first template
- [ ] Use Playwright MCP to verify styling
- [ ] Verify tests pass
- [ ] Commit: "Implement topic progress view"

---

## Phase 8: Polish & Optimization

### 8.1 Navigation & Layout
- [ ] Create consistent navigation component
  - Mobile hamburger menu
  - Desktop sidebar/topbar
  - User menu (profile, logout)
- [ ] Create footer component
- [ ] Ensure consistent styling across all pages
- [ ] Use Playwright MCP to verify responsive behavior
- [ ] Commit: "Polish navigation and layout"

### 8.2 Error Handling & Messages
- [ ] Implement Django messages framework
- [ ] Create styled message components (success, error, warning, info)
- [ ] Add 404 and 500 error pages
- [ ] Verify error handling with tests
- [ ] Commit: "Add error handling and user messages"

### 8.3 Performance Optimization
- [ ] Add database indexes for frequent queries
- [ ] Implement query optimization (select_related, prefetch_related)
- [ ] Add caching where appropriate
- [ ] Optimize static file loading
- [ ] Run performance tests
- [ ] Commit: "Optimize database queries and performance"

### 8.4 Accessibility
- [ ] Audit for accessibility (WCAG 2.1)
- [ ] Add proper ARIA labels
- [ ] Ensure keyboard navigation works
- [ ] Test with screen reader
- [ ] Fix any accessibility issues
- [ ] Commit: "Improve accessibility"

### 8.5 Security Hardening
- [ ] Review OWASP top 10
- [ ] Ensure CSRF protection is active
- [ ] Validate all user inputs
- [ ] Configure security headers
- [ ] Review Django security checklist
- [ ] Commit: "Security hardening"

---

## Phase 9: Documentation & Deployment Prep

### 9.1 Documentation
- [ ] Create README.md with:
  - Project description
  - Setup instructions
  - Development workflow
  - Testing instructions
- [ ] Document CSV import format
- [ ] Document API endpoints (if any)
- [ ] Add inline code documentation where needed
- [ ] Commit: "Add project documentation"

### 9.2 Docker Configuration
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml for local development
- [ ] Create docker-compose.prod.yml for production
- [ ] Configure PostgreSQL service
- [ ] Test Docker build and run
- [ ] Commit: "Add Docker configuration"

### 9.3 Production Settings
- [ ] Create production settings file
- [ ] Configure environment variables
- [ ] Set up PostgreSQL connection
- [ ] Configure static file serving
- [ ] Configure allowed hosts
- [ ] Set DEBUG=False handling
- [ ] Commit: "Add production configuration"

### 9.4 Deployment Checklist
- [ ] Create deployment checklist document
- [ ] Document environment variables needed
- [ ] Document database migration process
- [ ] Document static file collection
- [ ] Document backup procedures
- [ ] Commit: "Add deployment documentation"

---

## Future Enhancements (Out of Scope for Initial Build)

These items are noted for potential future development:

- Audio pronunciation support
- Social login (Google, Facebook)
- Multiple choice mode
- Gamification (badges, achievements)
- Offline support (PWA)
- Mobile native apps
- API for third-party integrations
- Advanced analytics
- A/B testing for learning algorithms
- Community features (share custom decks)

---

## File Structure

```
lux_app/
├── .github/
│   └── workflows/
│       └── ci.yml
├── planning/
│   └── app_plan.md
├── learnlux/                    # Django project
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                    # User management app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── cards/                       # Flashcard content app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── management/
│   │   └── commands/
│   │       └── import_cards.py
│   └── views.py
├── progress/                    # Progress tracking app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   └── views.py
├── learning/                    # Learning engine app
│   ├── __init__.py
│   ├── apps.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── spaced_repetition.py
│   │   ├── card_selector.py
│   │   ├── answer_checker.py
│   │   └── progress_updater.py
│   ├── urls.py
│   └── views.py
├── core/                        # Shared functionality
│   ├── __init__.py
│   ├── apps.py
│   └── templatetags/
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── messages.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── password_reset/
│   ├── cards/
│   ├── learning/
│   │   ├── study.html
│   │   ├── session_summary.html
│   │   └── topic_browser.html
│   └── progress/
│       ├── dashboard.html
│       ├── statistics.html
│       └── history.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_views.py
│   │   └── test_api.py
│   └── e2e/
│       ├── __init__.py
│       ├── test_auth_flow.py
│       ├── test_study_flow.py
│       └── test_progress.py
├── .gitignore
├── pyproject.toml
├── pytest.ini
├── README.md
└── manage.py
```

---

## Development Workflow

1. **Before starting a feature:**
   - Write failing tests first (TDD)
   - Create a feature branch

2. **During development:**
   - Make small, focused commits
   - Run tests frequently
   - Use Playwright MCP to verify frontend changes

3. **Before committing:**
   - All tests must pass
   - Code must be formatted
   - No linting errors

4. **Commit message format:**
   ```
   <type>: <short description>

   <optional longer description>
   ```
   Types: feat, fix, test, docs, refactor, style, chore

---

## Getting Started Commands

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install django pytest pytest-django playwright

# Install Playwright browsers
playwright install

# Create Django project
django-admin startproject learnlux .

# Run development server
python manage.py runserver

# Run tests
pytest

# Run e2e tests
pytest tests/e2e/
```

---

*This plan will be updated as development progresses.*
