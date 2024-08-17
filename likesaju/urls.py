"""
URL configuration for likesaju project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework.routers import DefaultRouter

# siwon added 0811
from webchat.views import MessageViewSet, ChatRoomViewSet

# siwon added 0812
from webchat.consumer import WebChatConsumer


schema_view = get_schema_view(
    openapi.Info(
        title="LIKESAJU API",
        default_version='v1',
        description="멋쟁이 사주처럼 api 테스트 페이지",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# siwon added 0811
router = DefaultRouter()
router.register("api/messages", MessageViewSet, basename="message")
router.register('api/chatrooms', ChatRoomViewSet, basename='chatroom')  # 추가된 부분


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/user/', include('UserProfile.urls')),
    path('api/profilepic/', include('ProfilePic.urls')),
    path('api/point/', include('Point.urls')),
    path("api/payment/", include("Payment.urls")),
] + router.urls

# siwon added for websocket routing 0811
# 웹소켓 요청은 view가 아닌 consumer로 forward
# 웹소켓 엔드포인트 설정
websocket_urlpatterns = [
    path( "ws/test/" ,  WebChatConsumer.as_asgi())
]
