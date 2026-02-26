# core/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Expert, Consultation, Message, Paysan

User = get_user_model()


# ============================================================
# USER SERIALIZERS
# ============================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'role', 'phone', 'avatar', 'is_active'
        ]
        read_only_fields = ['id', 'is_active']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'password', 'password2', 'role', 'phone'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ============================================================
# SIMPLE JWT — LOGIN PAR EMAIL
# ============================================================

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")

        if not user_obj.check_password(password):
            raise serializers.ValidationError("Email ou mot de passe incorrect.")

        self.user = user_obj
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token


# ============================================================
# EXPERT SERIALIZERS
# ============================================================

class ExpertSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Expert
        fields = ['id', 'user', 'domaine', 'experience', 'description']


# ============================================================
# ✅ PAYSAN SERIALIZER (AJOUTÉ)
# ============================================================

class PaysanSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Paysan
        fields = [
            'id',
            'user',
            'region',
            'type_culture',
            'superficie',
            'experience',
        ]


# ============================================================
# CONSULTATION SERIALIZER
# ============================================================

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = [
            'id', 'sujet', 'description',
            'status', 'created_at',
            'paysan', 'expert'
        ]
        read_only_fields = ['id', 'created_at', 'status', 'paysan']

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["paysan"] = request.user
        return super().create(validated_data)



# ============================================================
# MESSAGE SERIALIZER
# ============================================================

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'content', 'created_at',
            'sender', 'receiver', 'consultation'
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        consultation = attrs.get("consultation")

        if not consultation:
            raise serializers.ValidationError(
                {"consultation": "Consultation obligatoire"}
            )

        if request.user not in [consultation.paysan, consultation.expert]:
            raise serializers.ValidationError(
                "Vous ne participez pas à cette consultation"
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        consultation = validated_data["consultation"]

        validated_data["sender"] = request.user
        validated_data["receiver"] = (
            consultation.expert
            if consultation.paysan == request.user
            else consultation.paysan
        )

        return super().create(validated_data)
