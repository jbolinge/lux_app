import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view showing user's learning progress and quick actions."""

    template_name = "learning/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get user's statistics
        from progress.models import UserStats

        stats, _ = UserStats.objects.get_or_create(user=user)
        context["stats"] = stats

        # Get topics with progress
        from cards.models import Topic

        context["topics"] = Topic.objects.filter(parent__isnull=True).order_by("order")

        # Get cards due for review
        from progress.models import CardProgress

        context["cards_due"] = CardProgress.objects.due_for_review().filter(
            user=user
        ).count()

        return context


class TopicListView(LoginRequiredMixin, ListView):
    """View showing all available topics."""

    template_name = "learning/topics.html"
    context_object_name = "topics"

    def get_queryset(self):
        from cards.models import Topic

        return Topic.objects.filter(parent__isnull=True).order_by("order")


class TopicDetailView(LoginRequiredMixin, DetailView):
    """View showing details of a specific topic."""

    template_name = "learning/topic_detail.html"
    context_object_name = "topic"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        from cards.models import Topic

        return Topic.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.object

        # Get subtopics
        context["subtopics"] = topic.children.all().order_by("order")

        # Get card counts
        from cards.models import PhraseCard, VocabularyCard

        context["vocab_count"] = VocabularyCard.objects.filter(
            topics=topic, is_active=True
        ).count()
        context["phrase_count"] = PhraseCard.objects.filter(
            topics=topic, is_active=True
        ).count()

        return context


class StudySessionView(LoginRequiredMixin, TemplateView):
    """View for studying flashcards."""

    template_name = "learning/study.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = kwargs.get("topic_id")

        if topic_id:
            from cards.models import Topic

            context["topic"] = Topic.objects.get(pk=topic_id)

        return context


class CheckAnswerView(LoginRequiredMixin, View):
    """API endpoint to check a user's answer."""

    def post(self, request):
        try:
            data = json.loads(request.body)
            card_type = data.get("card_type")
            card_id = data.get("card_id")
            user_answer = data.get("answer", "").strip()
            direction = data.get("direction", "lux_to_eng")
            input_mode = data.get("input_mode", "text_input")

            from learning.services.answer_checker import AnswerChecker
            from learning.services.progress_updater import ProgressUpdater

            # Get the card
            if card_type == "vocabulary":
                from cards.models import VocabularyCard

                card = VocabularyCard.objects.get(pk=card_id)
            else:
                from cards.models import PhraseCard

                card = PhraseCard.objects.get(pk=card_id)

            correct_answer = (
                card.english if direction == "lux_to_eng" else card.luxembourgish
            )

            # Check the answer based on input mode
            if input_mode == "multiple_choice":
                # For multiple choice, use exact string matching (case-insensitive)
                is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
                result = {
                    "is_correct": is_correct,
                    "match_quality": "exact" if is_correct else "incorrect",
                }
            else:
                # For text input, use fuzzy matching with typo tolerance
                checker = AnswerChecker()
                result = checker.check(user_answer, correct_answer)

            # Update progress
            updater = ProgressUpdater()
            updater.update(
                user=request.user,
                card=card,
                direction=direction,
                user_answer=user_answer,
                was_correct=result["is_correct"],
            )

            return JsonResponse(
                {
                    "is_correct": result["is_correct"],
                    "match_quality": result["match_quality"],
                    "correct_answer": correct_answer,
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class NextCardView(LoginRequiredMixin, View):
    """API endpoint to get the next card for study."""

    def get(self, request):
        try:
            topic_id = request.GET.get("topic_id")
            direction = request.GET.get("direction", "lux_to_eng")

            from cards.models import DifficultyLevel
            from learning.services.card_selector import CardSelector
            from learning.services.option_generator import (
                InsufficientOptionsError,
                OptionGenerator,
            )

            selector = CardSelector(request.user)
            card = selector.get_next_card(topic_id=topic_id)

            if card is None:
                return JsonResponse({"card": None, "message": "No cards available"})

            from cards.models import VocabularyCard as VocabModel

            card_type = "vocabulary" if isinstance(card, VocabModel) else "phrase"

            # Determine input mode based on difficulty
            input_mode = "text_input"
            options_data = {}

            if card.difficulty_level == DifficultyLevel.BEGINNER and card_type == "vocabulary":
                # Try to generate multiple choice options for beginner cards
                try:
                    generator = OptionGenerator(card, direction)
                    options_data = generator.get_options()
                    input_mode = "multiple_choice"
                except InsufficientOptionsError:
                    # Fallback to text input if not enough options
                    input_mode = "text_input"

            response_data = {
                "card": {
                    "id": card.id,
                    "type": card_type,
                    "question": (
                        card.luxembourgish
                        if direction == "lux_to_eng"
                        else card.english
                    ),
                    "direction": direction,
                    "difficulty_level": card.difficulty_level,
                    "input_mode": input_mode,
                }
            }

            # Add options for multiple choice
            if input_mode == "multiple_choice":
                response_data["card"]["options"] = options_data["options"]
                response_data["card"]["correct_index"] = options_data["correct_index"]

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
