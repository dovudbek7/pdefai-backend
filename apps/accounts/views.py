from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer

from .serializers import RegisterSerializer, UserSerializer


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def _auth_response_serializer(name):
    return inline_serializer(name=name, fields={
        'access': serializers.CharField(),
        'refresh': serializers.CharField(),
        'user': UserSerializer(),
    })


@extend_schema(tags=['Auth'])
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Ro\'yxatdan o\'tish',
        request=RegisterSerializer,
        responses={
            201: _auth_response_serializer('RegisterResponse'),
            400: OpenApiResponse(description='Validation error'),
        },
        auth=[],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            **_tokens_for_user(user),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'])
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Kirish',
        request=inline_serializer(name='LoginRequest', fields={
            'email': serializers.EmailField(),
            'password': serializers.CharField(),
        }),
        responses={
            200: _auth_response_serializer('LoginResponse'),
            401: OpenApiResponse(description='Email yoki parol noto\'g\'ri'),
        },
        auth=[],
    )
    def post(self, request):
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {'detail': 'Email yoki parol noto\'g\'ri.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response({
            **_tokens_for_user(user),
            'user': UserSerializer(user).data,
        })


@extend_schema(tags=['Auth'])
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Hozirgi foydalanuvchi',
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)
