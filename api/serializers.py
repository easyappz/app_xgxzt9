from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Member
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    timestamp = serializers.DateTimeField(read_only=True)


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "email", "first_name", "last_name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        error_messages={
            "required": "Пароль обязателен для заполнения",
            "blank": "Пароль не может быть пустым"
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        error_messages={
            "required": "Подтверждение пароля обязательно для заполнения",
            "blank": "Подтверждение пароля не может быть пустым"
        }
    )

    class Meta:
        model = Member
        fields = ["id", "email", "first_name", "last_name", "password", "password_confirm"]
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "required": "Email обязателен для заполнения",
                    "blank": "Email не может быть пустым",
                    "invalid": "Введите корректный email адрес",
                    "unique": "Пользователь с таким email уже существует"
                }
            },
            "first_name": {
                "error_messages": {
                    "required": "Имя обязательно для заполнения",
                    "blank": "Имя не может быть пустым"
                }
            },
            "last_name": {
                "error_messages": {
                    "required": "Фамилия обязательна для заполнения",
                    "blank": "Фамилия не может быть пустой"
                }
            }
        }

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        
        try:
            validate_password(attrs.get("password"))
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        member = Member(**validated_data)
        member.set_password(password)
        member.save()
        return member


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "Email обязателен для заполнения",
            "blank": "Email не может быть пустым",
            "invalid": "Введите корректный email адрес"
        }
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        error_messages={
            "required": "Пароль обязателен для заполнения",
            "blank": "Пароль не может быть пустым"
        }
    )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "email", "first_name", "last_name", "created_at", "updated_at"]
        read_only_fields = ["id", "email", "created_at", "updated_at"]
        extra_kwargs = {
            "first_name": {
                "error_messages": {
                    "required": "Имя обязательно для заполнения",
                    "blank": "Имя не может быть пустым"
                }
            },
            "last_name": {
                "error_messages": {
                    "required": "Фамилия обязательна для заполнения",
                    "blank": "Фамилия не может быть пустой"
                }
            }
        }


class MemberTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField(required=True)
        self.fields["password"] = serializers.CharField(write_only=True, required=True)
        del self.fields["username"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        try:
            member = Member.objects.get(email=email)
            if not member.check_password(password):
                raise serializers.ValidationError({"detail": "Неверные учетные данные"})
        except Member.DoesNotExist:
            raise serializers.ValidationError({"detail": "Неверные учетные данные"})
        
        refresh = self.get_token(member)
        
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "member": MemberSerializer(member).data
        }
    
    @classmethod
    def get_token(cls, member):
        token = super().get_token(member)
        token["member_id"] = member.id
        token["email"] = member.email
        return token
