from django.urls import path
from .views import PayReadyView, PayApproveView

app_name = 'payment'
urlpatterns = [
  path("ready/", PayReadyView.as_view()),
  path("approve/", PayApproveView.as_view()),
]