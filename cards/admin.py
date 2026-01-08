from django.contrib import admin

from .models import PhraseCard, Topic, VocabularyCard


class TopicInline(admin.TabularInline):
    """Inline admin for child topics."""

    model = Topic
    fk_name = "parent"
    extra = 0
    fields = ("name", "difficulty_level", "order")
    show_change_link = True


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin configuration for Topic model."""

    list_display = (
        "indented_name",
        "difficulty_level",
        "order",
        "card_count",
        "created_at",
    )
    list_filter = ("difficulty_level", "parent")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    inlines = [TopicInline]

    fieldsets = (
        (None, {"fields": ("name", "slug", "description")}),
        ("Hierarchy", {"fields": ("parent",)}),
        (
            "Settings",
            {"fields": ("difficulty_level", "order")},
        ),
    )

    def indented_name(self, obj):
        """Display topic name with indentation for hierarchy."""
        if obj.parent:
            return f"↳ {obj.name}"
        return obj.name

    indented_name.short_description = "Name"

    def card_count(self, obj):
        """Display total card count for the topic."""
        return obj.get_card_count()

    card_count.short_description = "Cards"


class BaseCardAdmin(admin.ModelAdmin):
    """Base admin configuration for card models."""

    list_display = (
        "luxembourgish",
        "english",
        "difficulty_level",
        "topic_list",
        "is_active",
        "created_at",
    )
    list_filter = ("difficulty_level", "is_active", "topics")
    search_fields = ("luxembourgish", "english")
    filter_horizontal = ("topics",)
    ordering = ("-created_at",)
    actions = ["activate_cards", "deactivate_cards"]

    fieldsets = (
        (None, {"fields": ("luxembourgish", "english")}),
        ("Classification", {"fields": ("topics", "difficulty_level")}),
        ("Status", {"fields": ("is_active",)}),
    )

    def topic_list(self, obj):
        """Display comma-separated list of topics."""
        return ", ".join([t.name for t in obj.topics.all()[:3]])

    topic_list.short_description = "Topics"

    @admin.action(description="Activate selected cards")
    def activate_cards(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} cards activated.")

    @admin.action(description="Deactivate selected cards")
    def deactivate_cards(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} cards deactivated.")


@admin.register(VocabularyCard)
class VocabularyCardAdmin(BaseCardAdmin):
    """Admin configuration for VocabularyCard model."""

    pass


@admin.register(PhraseCard)
class PhraseCardAdmin(BaseCardAdmin):
    """Admin configuration for PhraseCard model."""

    list_display = (
        "luxembourgish",
        "english",
        "register",
        "difficulty_level",
        "topic_list",
        "is_active",
        "created_at",
    )
    list_filter = ("difficulty_level", "is_active", "topics", "register")

    fieldsets = (
        (None, {"fields": ("luxembourgish", "english")}),
        ("Classification", {"fields": ("topics", "difficulty_level", "register")}),
        ("Status", {"fields": ("is_active",)}),
    )
