from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    MessageSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    MemberSerializer,
    MemberTokenObtainPairSerializer
)
from .models import Member


class HelloView(APIView):
    """
    A simple API endpoint that returns a greeting message.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: MessageSerializer}, description="Get a hello world message"
    )
    def get(self, request):
        data = {"message": "Hello!", "timestamp": timezone.now()}
        serializer = MessageSerializer(data)
        return Response(serializer.data)


class RegisterView(APIView):
    """
    User registration endpoint.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                description="Пользователь успешно зарегистрирован",
            ),
            400: OpenApiResponse(description="Ошибка валидации данных")
        },
        description="Регистрация нового пользователя"
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            
            token_serializer = MemberTokenObtainPairSerializer()
            refresh = token_serializer.get_token(member)
            
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "member": MemberSerializer(member).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    User login endpoint.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description="Успешная авторизация"),
            400: OpenApiResponse(description="Неверные учетные данные")
        },
        description="Авторизация пользователя"
    )
    def post(self, request):
        login_serializer = UserLoginSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = login_serializer.validated_data["email"]
        password = login_serializer.validated_data["password"]
        
        try:
            member = Member.objects.get(email=email)
            if not member.check_password(password):
                return Response(
                    {"detail": "Неверные учетные данные"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Member.DoesNotExist:
            return Response(
                {"detail": "Неверные учетные данные"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_serializer = MemberTokenObtainPairSerializer()
        refresh = token_serializer.get_token(member)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "member": MemberSerializer(member).data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    User logout endpoint.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Успешный выход из системы"),
            401: OpenApiResponse(description="Не авторизован")
        },
        description="Выход из системы"
    )
    def post(self, request):
        return Response(
            {"detail": "Успешный выход из системы"},
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    """
    User profile endpoint.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: UserProfileSerializer,
            401: OpenApiResponse(description="Не авторизован")
        },
        description="Получение профиля текущего пользователя"
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Ошибка валидации данных"),
            401: OpenApiResponse(description="Не авторизован")
        },
        description="Полное обновление профиля текущего пользователя"
    )
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Ошибка валидации данных"),
            401: OpenApiResponse(description="Не авторизован")
        },
        description="Частичное обновление профиля текущего пользователя"
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
