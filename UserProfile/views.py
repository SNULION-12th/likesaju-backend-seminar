from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from .models import UserProfile
from ProfilePic.models import ProfilePic

from .serializers import UserSerializer, TokenRefreshRequestSerializer, SignUpRequestSerializer, UserProfileSerializer

def set_token_on_response_cookie(user, status_code) -> Response:
    token = RefreshToken.for_user(user)
    user_profile = UserProfile.objects.get(user=user)
    serialized_data = UserProfileSerializer(user_profile).data
    res = Response(serialized_data, status=status_code)
    res.set_cookie("refresh_token", value=str(token), httponly=True)
    res.set_cookie("access_token", value=str(token.access_token), httponly=True)
    return res


class SignUpView(APIView):
    @swagger_auto_schema(
        operation_id="회원가입",
        operation_description="회원가입을 진행합니다.",
        request_body=SignUpRequestSerializer,
        responses={201: UserProfileSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        nickname = request.data.get("nickname")
        profile_pic_id = request.data.get("profilepic_id")
        
        if not nickname or not profile_pic_id:
            return Response(
                {"message": "nickname or profilepic_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user_serializer.validated_data["password"] = make_password(
                user_serializer.validated_data["password"]
            )
            user = user_serializer.save()
            user.save()
        
        profile_pic = ProfilePic.objects.filter(id=profile_pic_id)

        if not profile_pic.exists():
            return Response(
                {"message": "ProfilePic not found"}, status=status.HTTP_404_NOT_FOUND
            )

        UserProfile.objects.create(
            user=user,
            nickname=nickname,
            profilepic_id=profile_pic.first(),
        )

        return set_token_on_response_cookie(user, status_code=status.HTTP_201_CREATED)

class SignInView(APIView):
    @swagger_auto_schema(
        operation_id="로그인",
        operation_description="로그인을 진행합니다.",
        request_body=UserSerializer,
        responses={200: UserSerializer, 404: "Not Found", 400: "Bad Request"},
    )
    def post(self, request):
        user = User.objects.filter(username=request.data["username"]).first()
        if user is None:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(request.data["password"]):
            return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

        return set_token_on_response_cookie(user, status_code=status.HTTP_200_OK)
    
class TokenRefreshView(APIView):
    @swagger_auto_schema(
        operation_id="토큰 재발급",
        operation_description="access 토큰을 재발급 받습니다.",
        request_body=TokenRefreshRequestSerializer,
        responses={200: UserSerializer},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            RefreshToken(refresh_token).verify()
        except:
            return Response(
                {"detail": "please signin again."}, status=status.HTTP_401_UNAUTHORIZED
            )
        new_access_token = str(RefreshToken(refresh_token).access_token)
        response = Response({"detail": "token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=str(new_access_token), httponly=True)
        return response


class SignOutView(APIView):
    @swagger_auto_schema(
        operation_id="로그아웃",
        operation_description="로그아웃을 진행합니다.",
        responses={204: "No Content"},
    )
    def post(self, request):

        if not request.user.is_authenticated:
            return Response(
                {"detail": "please signin"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "no refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )
        RefreshToken(refresh_token).blacklist()

        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileListView(APIView):
    def get(self, request):
        user_profile = UserProfile.objects.all()
        serializer = UserProfileSerializer(user_profile, many=True)
        return Response(serializer.data)
    
class UserProfileDetailView(APIView):
    def get(self, request, user_id):
        user_profile = UserProfile.objects.get(user_id=user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)
