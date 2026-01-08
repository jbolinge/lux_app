from django.urls import path

from . import views

app_name = "learning"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("topics/", views.TopicListView.as_view(), name="topics"),
    path("topics/<slug:slug>/", views.TopicDetailView.as_view(), name="topic_detail"),
    path("study/", views.StudySessionView.as_view(), name="study"),
    path("study/<int:topic_id>/", views.StudySessionView.as_view(), name="study_topic"),
    path("api/check-answer/", views.CheckAnswerView.as_view(), name="check_answer"),
    path("api/next-card/", views.NextCardView.as_view(), name="next_card"),
]
