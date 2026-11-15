from django.urls import path

from .views import (
    AnswerFeedbackAPIView,
    HealthAPIView,
    LoginAPIView,
    ProfileAPIView,
    PublicStatsAPIView,
    QuestionAPIView,
    RegisterAPIView,
)


urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
    path("public/stats/", PublicStatsAPIView.as_view(), name="public-stats"),
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("questions/", QuestionAPIView.as_view(), name="questions"),
    path("feedback/", AnswerFeedbackAPIView.as_view(), name="feedback"),
]

