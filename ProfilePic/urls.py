from django.urls import path

from .views import ProfilePicListView

app_name = "ProfilePic"

urlpatterns = [
    path("", ProfilePicListView.as_view()),
]