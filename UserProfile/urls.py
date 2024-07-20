from django.urls import path
from .views import SignUpView, SignInView, SignOutView, TokenRefreshView, UserProfileListView, UserProfileDetailView, KakaoSignInView, KakaoSignInCallbackView


app_name = "UserProfile"
urlpatterns = [
    # CBV url path
    path("signup/", SignUpView.as_view()),
    path("signin/", SignInView.as_view()),
    path("signout/", SignOutView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("userinfo/", UserProfileListView.as_view()),
    path("userinfo/<int:user_id>/", UserProfileDetailView.as_view()),
    path("kakao/signin/", KakaoSignInView.as_view()),
    path("kakao/callback/", KakaoSignInCallbackView.as_view()),
]