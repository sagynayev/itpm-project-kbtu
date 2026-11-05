from django.urls import path

from .views import HealthAPIView, LoginAPIView, QuestionAPIView, RegisterAPIView


urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("questions/", QuestionAPIView.as_view(), name="questions"),
]

