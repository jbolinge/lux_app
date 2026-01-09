# Difficulty-Based Learning Flow Implementation Plan

## Overview

Transform the learning flow from uniform text input to difficulty-aware modes:
- **Easy (Beginner)**: Multiple choice - 3 clickable options (1 correct, 2 wrong)
- **Intermediate**: Text input for single words (current behavior)
- **Advanced**: Text input for sentences/phrases (current behavior)

## Constraints (User Requirements)

- Wrong options: Same topic + same difficulty first, then cascade to broader pools
- Card type enforcement: VocabularyCard = Easy/Intermediate ONLY, PhraseCard = Advanced ONLY
- Direction: All modes support both Lux→Eng and Eng→Lux

---

## Implementation Steps

### Phase 1: Model Validation (TDD)

**Files to modify:**
- `cards/models.py` (lines 87-95 VocabularyCard, lines 105-118 PhraseCard)
- `tests/unit/test_models.py`

**Tests to write first:**
```python
# tests/unit/test_models.py
- test_vocabulary_card_allows_beginner
- test_vocabulary_card_allows_intermediate
- test_vocabulary_card_rejects_advanced
- test_phrase_card_allows_advanced
- test_phrase_card_rejects_beginner
- test_phrase_card_rejects_intermediate
```

**Implementation:**
```python
# In VocabularyCard
def clean(self):
    super().clean()
    if self.difficulty_level == DifficultyLevel.ADVANCED:
        raise ValidationError({'difficulty_level': 'VocabularyCard cannot have ADVANCED difficulty.'})

def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)

# In PhraseCard
def clean(self):
    super().clean()
    if self.difficulty_level != DifficultyLevel.ADVANCED:
        raise ValidationError({'difficulty_level': 'PhraseCard must have ADVANCED difficulty.'})
```

**Data migration:** Create migration to fix existing cards (ADVANCED vocab → INTERMEDIATE, non-ADVANCED phrases → ADVANCED)

---

### Phase 2: OptionGenerator Service (TDD)

**New file:** `learning/services/option_generator.py`
**New test file:** `tests/unit/test_option_generator.py`

**Tests to write first:**
```python
- test_get_options_returns_three_options
- test_get_options_includes_correct_answer
- test_get_options_lux_to_eng_direction
- test_get_options_eng_to_lux_direction
- test_options_are_unique
- test_correct_index_is_valid
- test_insufficient_options_raises_error
- test_priority_same_topic_same_difficulty
- test_fallback_to_any_difficulty
- test_options_shuffled
```

**Implementation:**
```python
class InsufficientOptionsError(Exception):
    pass

class OptionGenerator:
    def __init__(self, card, direction: str, count: int = 2):
        self.card = card
        self.direction = direction
        self.count = count

    def get_options(self) -> dict:
        """Returns: {'correct_answer': str, 'options': List[str], 'correct_index': int}"""
        correct = self._get_answer_field(self.card)
        wrong = self._get_wrong_options()

        if len(wrong) < self.count:
            raise InsufficientOptionsError()

        options = [correct] + wrong[:self.count]
        random.shuffle(options)

        return {
            'correct_answer': correct,
            'options': options,
            'correct_index': options.index(correct)
        }

    def _get_wrong_options(self) -> List[str]:
        """Priority cascade: same topic+diff → same topic any diff → any topic same diff → any"""
        # Implementation details...
```

---

### Phase 3: View Layer Changes (TDD)

**Files to modify:**
- `learning/views.py` (NextCardView lines 154-188, CheckAnswerView lines 101-151)
- `tests/integration/test_views.py`

**Tests to write first:**
```python
- test_beginner_card_returns_multiple_choice
- test_intermediate_card_returns_text_input
- test_advanced_card_returns_text_input
- test_check_answer_multiple_choice_correct
- test_check_answer_multiple_choice_incorrect
- test_fallback_to_text_when_insufficient_options
```

**NextCardView changes:**
```python
# Add to response for BEGINNER cards:
if card.difficulty_level == DifficultyLevel.BEGINNER:
    try:
        generator = OptionGenerator(card, direction)
        options_data = generator.get_options()
        response_data["card"]["input_mode"] = "multiple_choice"
        response_data["card"]["options"] = options_data["options"]
        response_data["card"]["correct_index"] = options_data["correct_index"]
    except InsufficientOptionsError:
        response_data["card"]["input_mode"] = "text_input"
else:
    response_data["card"]["input_mode"] = "text_input"

response_data["card"]["difficulty_level"] = card.difficulty_level
```

**CheckAnswerView changes:**
```python
input_mode = data.get("input_mode", "text_input")

if input_mode == "multiple_choice":
    # Exact string match for multiple choice
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    result = {"is_correct": is_correct, "match_quality": "exact" if is_correct else "incorrect"}
else:
    # Fuzzy matching for text input
    result = checker.check(user_answer, correct_answer)
```

---

### Phase 4: Frontend Changes

**File to modify:** `templates/learning/study.html`

**HTML additions (after line 60):**
```html
<!-- Multiple Choice Options (hidden initially) -->
<div id="options-section" class="hidden bg-slate-50 p-6 border-t border-slate-200">
    <label class="block text-sm font-medium text-slate-700 mb-4">Select the correct answer:</label>
    <div id="options-container" class="space-y-3"></div>
</div>
```

**JavaScript changes:**

1. Add to state:
```javascript
inputMode: 'text_input',
options: [],
correctIndex: null,
```

2. Update `displayCard()` to branch on input_mode
3. Add `displayMultipleChoice(options)` function
4. Add `displayTextInput()` function
5. Add `selectOption(answer, index)` function
6. Update `checkAnswer()` to include input_mode in request
7. Update `showResult()` to highlight correct/incorrect options

---

### Phase 5: Integration Testing

**E2E tests to add:** `tests/e2e/test_study_flow.py`
```python
- test_beginner_multiple_choice_flow
- test_intermediate_text_input_flow
- test_advanced_text_input_flow
- test_mixed_difficulty_session
```

---

## API Response Changes

**NextCardView response (Beginner):**
```json
{
    "card": {
        "id": 123,
        "type": "vocabulary",
        "question": "Moien",
        "direction": "lux_to_eng",
        "difficulty_level": 1,
        "input_mode": "multiple_choice",
        "options": ["Hello", "Goodbye", "Thank you"],
        "correct_index": 0
    }
}
```

**NextCardView response (Intermediate/Advanced):**
```json
{
    "card": {
        "id": 456,
        "type": "vocabulary",
        "question": "Haus",
        "direction": "lux_to_eng",
        "difficulty_level": 2,
        "input_mode": "text_input"
    }
}
```

---

## Files Summary

### New Files
- `learning/services/option_generator.py`
- `tests/unit/test_option_generator.py`
- `cards/migrations/XXXX_enforce_card_difficulty_constraints.py`

### Modified Files
- `cards/models.py` - Add clean/save validation
- `learning/views.py` - Modify NextCardView and CheckAnswerView
- `templates/learning/study.html` - Add multiple choice UI
- `tests/unit/test_models.py` - Add validation tests
- `tests/integration/test_views.py` - Add flow tests

---

## Verification

1. **Run unit tests:** `uv run pytest tests/unit -v`
2. **Run integration tests:** `uv run pytest tests/integration -v`
3. **Run e2e tests:** `uv run pytest tests/e2e -v`
4. **Manual testing:**
   - Load sample data with mixed difficulties
   - Study beginner cards → verify multiple choice appears
   - Study intermediate cards → verify text input appears
   - Study advanced cards → verify text input appears
   - Test both directions (Lux→Eng, Eng→Lux)
   - Test insufficient options fallback
5. **Admin validation:** Verify difficulty dropdowns respect constraints
