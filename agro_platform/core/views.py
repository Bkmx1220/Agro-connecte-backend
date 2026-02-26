from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q

from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Expert, Consultation, Message
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    ExpertSerializer,
    ConsultationSerializer,
    MessageSerializer,
)
from .permissions import (
    IsAdminOrReadOnly,
    IsOwnerOrReadOnly,
    IsExpert,
)

User = get_user_model()

# ============================================================
# 🔐 LOGIN JWT PERSONNALISÉ (email OU username)
# ============================================================
class LoginAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        login_input = request.data.get("login_input")
        password = request.data.get("password")

        if not login_input or not password:
            return Response(
                {"detail": "Identifiants manquants"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if "@" in login_input:
                user_obj = User.objects.get(email=login_input)
            else:
                user_obj = User.objects.get(username=login_input)
        except User.DoesNotExist:
            return Response(
                {"detail": "Utilisateur introuvable"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=user_obj.username,
            password=password
        )

        if user is None:
            return Response(
                {"detail": "Mot de passe incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_staff": user.is_staff,
            }
        })


# ============================================================
# 🔁 REFRESH JWT
# ============================================================
class RefreshAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token manquant"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({"access": str(refresh.access_token)})
        except Exception:
            return Response(
                {"detail": "Refresh token invalide"},
                status=status.HTTP_401_UNAUTHORIZED
            )


# ============================================================
# REGISTER
# ============================================================
class RegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


# ============================================================
# 👤 PROFIL UTILISATEUR CONNECTÉ (PAYSAN)
# GET / PUT → /api/me/
# ============================================================
class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.role != "paysan":
            raise PermissionDenied("Accès réservé aux paysans")
        return user


# ============================================================
# USER VIEWSET
# ============================================================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)


# ============================================================
# EXPERT VIEWSET
# ============================================================
class ExpertViewSet(viewsets.ModelViewSet):
    queryset = Expert.objects.select_related("user").all().order_by("-id")
    serializer_class = ExpertSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_serializer_class(self):
        return ExpertSerializer

    @action(
        detail=False,
        methods=["get", "put"],
        permission_classes=[IsAuthenticated, IsExpert],
        url_path="me"
    )
    def me(self, request):
        expert, _ = Expert.objects.get_or_create(
            user=request.user,
            defaults={
                "domaine": "Agriculture générale",
                "experience": 0,
                "description": "Profil expert"
            }
        )

        if request.method == "PUT":
            serializer = ExpertSerializer(
                expert,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response(ExpertSerializer(expert).data)


# ============================================================
# 🌾 PAYSAN VIEWSET
# ============================================================
class PaysanViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["get", "put"],
        url_path="me"
    )
    def me(self, request):
        user = request.user

        # 🔒 Sécurité : uniquement paysan
        if user.role != "paysan":
            raise PermissionDenied("Accès réservé aux paysans")

        # ==========================
        # GET → profil paysan
        # ==========================
        if request.method == "GET":
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "phone": user.phone,
                "avatar": user.avatar.url if user.avatar else None,
                "first_name": user.first_name,
                "last_name": user.last_name,
            })

        # ==========================
        # PUT → update profil
        # ==========================
        serializer = UserSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# ============================================================
# CONSULTATION VIEWSET
# ============================================================
class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.select_related(
        "paysan", "expert"
    ).all().order_by("-created_at")
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Consultation.objects.all()

        if user.role == "expert":
            return Consultation.objects.filter(expert=user)

        return Consultation.objects.filter(paysan=user)

    def perform_create(self, serializer):
        serializer.save(paysan=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsExpert])
    def accept(self, request, pk=None):
        consultation = self.get_object()
        consultation.status = "accepted"
        consultation.save()
        return Response({"status": "accepted"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsExpert])
    def reject(self, request, pk=None):
        consultation = self.get_object()
        consultation.status = "rejected"
        consultation.save()
        return Response({"status": "rejected"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        consultation = self.get_object()
        consultation.status = "completed"
        consultation.save()
        return Response({"status": "completed"})


# ============================================================
# MESSAGE VIEWSET
# ============================================================
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related(
        "sender", "receiver", "consultation"
    ).all().order_by("created_at")
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) |
            Q(receiver=user)
        )

    def perform_create(self, serializer):
        serializer.save()

