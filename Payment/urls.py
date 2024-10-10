from django.urls import path
from .views import PayReadyView, PayApproveView, PayRecordView

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    ### 🔻 이 부분 추가 ###
    path("approve/", PayApproveView.as_view()),
     # 카카오페이 주문 조회 API 추가
    path("payRocord/", PayRecordView.as_view()),
]