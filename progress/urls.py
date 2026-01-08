from django.urls import path

from . import views

app_name = "progress"

urlpatterns = [
    path("", views.StatisticsView.as_view(), name="statistics"),
    path("history/", views.HistoryView.as_view(), name="history"),
    path("topics/", views.TopicProgressView.as_view(), name="topic_progress"),
]
