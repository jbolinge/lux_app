from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView


class StatisticsView(LoginRequiredMixin, TemplateView):
    """View showing user's overall statistics and progress charts."""

    template_name = "progress/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        from .models import ReviewHistory, UserStats

        # Get or create user stats
        stats, _ = UserStats.objects.get_or_create(user=user)
        context["stats"] = stats

        # Calculate accuracy and incorrect percentages
        total = stats.total_correct + stats.total_incorrect
        if total > 0:
            context["accuracy"] = round((stats.total_correct / total) * 100)
            context["incorrect_pct"] = 100 - context["accuracy"]
        else:
            context["accuracy"] = 0
            context["incorrect_pct"] = 0

        # Get recent activity for charts (last 30 days)
        from datetime import timedelta

        from django.db.models import Count
        from django.db.models.functions import TruncDate
        from django.utils import timezone

        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_activity = (
            ReviewHistory.objects.filter(user=user, reviewed_at__gte=thirty_days_ago)
            .annotate(date=TruncDate("reviewed_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        context["daily_activity"] = list(daily_activity)

        return context


class HistoryView(LoginRequiredMixin, ListView):
    """View showing user's card review history."""

    template_name = "progress/history.html"
    context_object_name = "reviews"
    paginate_by = 50

    def get_queryset(self):
        from .models import ReviewHistory

        return ReviewHistory.objects.filter(user=self.request.user).order_by(
            "-reviewed_at"
        )


class TopicProgressView(LoginRequiredMixin, TemplateView):
    """View showing user's progress per topic."""

    template_name = "progress/topic_progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        from cards.models import Topic

        from .models import TopicProgress

        # Get all top-level topics with progress
        topics = Topic.objects.filter(parent__isnull=True).order_by("order")
        topic_progress_list = []

        for topic in topics:
            progress, _ = TopicProgress.objects.get_or_create(user=user, topic=topic)

            # Calculate total cards in topic
            from cards.models import PhraseCard, VocabularyCard

            total_cards = (
                VocabularyCard.objects.filter(topics=topic, is_active=True).count()
                + PhraseCard.objects.filter(topics=topic, is_active=True).count()
            )

            completion = 0
            if total_cards > 0:
                completion = round((progress.cards_seen / total_cards) * 100)

            topic_progress_list.append(
                {
                    "topic": topic,
                    "progress": progress,
                    "total_cards": total_cards,
                    "completion": min(completion, 100),
                }
            )

        context["topic_progress_list"] = topic_progress_list
        return context
