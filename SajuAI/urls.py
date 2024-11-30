from django.urls import path

from .views import ChatView

app_name = "SajuAI"
urlpatterns = [
    path("", ChatView.as_view()),
]
