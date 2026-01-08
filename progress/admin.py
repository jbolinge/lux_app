from django.contrib import admin

from .models import CardProgress, ReviewHistory, TopicProgress, UserStats


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    """Admin for user statistics."""

    list_display = (
        "user",
        "total_cards_studied",
        "total_correct",
        "total_incorrect",
        "current_streak",
        "longest_streak",
        "last_study_date",
    )
    list_filter = ("last_study_date",)
    search_fields = ("user__username", "user__email")
    readonly_fields = (
        "total_cards_studied",
        "total_correct",
        "total_incorrect",
        "current_streak",
        "longest_streak",
        "last_study_date",
    )


@admin.register(CardProgress)
class CardProgressAdmin(admin.ModelAdmin):
    """Admin for card progress."""

    list_display = (
        "user",
        "card_content_type",
        "card_object_id",
        "times_shown",
        "times_correct",
        "times_incorrect",
        "next_review",
    )
    list_filter = ("card_content_type", "next_review")
    search_fields = ("user__username",)


@admin.register(ReviewHistory)
class ReviewHistoryAdmin(admin.ModelAdmin):
    """Admin for review history."""

    list_display = (
        "user",
        "card_content_type",
        "direction",
        "was_correct",
        "reviewed_at",
    )
    list_filter = ("was_correct", "direction", "reviewed_at")
    search_fields = ("user__username", "user_answer")
    readonly_fields = ("reviewed_at",)


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    """Admin for topic progress."""

    list_display = (
        "user",
        "topic",
        "cards_seen",
        "cards_mastered",
        "started_at",
        "completed_at",
    )
    list_filter = ("topic", "completed_at")
    search_fields = ("user__username", "topic__name")
