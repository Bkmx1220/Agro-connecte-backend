from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login_input = attrs.get("username")
        password = attrs.get("password")

        # Recherche par email ou username
        try:
            if "@" in login_input:
                user = User.objects.get(email__iexact=login_input)
            else:
                user = User.objects.get(username__iexact=login_input)
        except User.DoesNotExist:
            raise Exception("Utilisateur introuvable")

        # Vérification mot de passe
        if not check_password(password, user.password):
            raise Exception("Mot de passe incorrect")

        # Authentification validée -> générer tokens JWT
        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        }


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
