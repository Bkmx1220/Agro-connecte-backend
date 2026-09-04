from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q

from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Elevage, Expert, Consultation, Message
from .serializers import (
    PaysanSerializer,
    UserSerializer,
    UserRegisterSerializer,
    ExpertSerializer,
    ConsultationSerializer,
    MessageSerializer,
    ModuleSerializer,
    ElevageSerializer,
)
from .permissions import (
    IsAdminOrReadOnly,
    IsOwnerOrReadOnly,
    IsExpert,
    IsPaysan,
    IsConsultationParticipant,
    IsEleveur,
    IsMessageParticipant                   
)
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Module

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser


User = get_user_model()

# ============================================================
# LOGIN JWT PERSONNALISÉ (email OU username)
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
                "is_verified": user.is_verified,
            }
        })


# ============================================================
# REFRESH JWT
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
# PROFIL UTILISATEUR CONNECTÉ (PAYSAN)
# GET / PUT → /api/me/
# ============================================================
class MeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
      

        return self.request.user


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
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["get", "put", "post"],
        permission_classes=[IsAuthenticated],
        url_path="me"
    )
    def me(self, request):

        if request.user.role != "expert":
            raise PermissionDenied("Accès réservé aux experts")

        # ======================
        # CREATE PROFILE
        # ======================
        if request.method == "POST":
            if Expert.objects.filter(user=request.user).exists():
                return Response(
                    {"detail": "Profil existe déjà"},
                    status=400
                )

            expert = Expert.objects.create(
                user=request.user,
                domaine=request.data.get("domaine", ""),
                experience=request.data.get("experience", 0),
                description=request.data.get("description", "")
            )

            return Response(ExpertSerializer(expert).data)

        # ======================
        # GET PROFILE
        # ======================
        try:
            expert = Expert.objects.get(user=request.user)
        except Expert.DoesNotExist:
            return Response(
                {"detail": "Profil non trouvé"},
                status=404
            )

        # ======================
        # UPDATE PROFILE
        # ======================
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
# PAYSAN VIEWSET
# ============================================================
class PaysanViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["get", "post", "put"],  # ✅ ajout POST
        url_path="me"
    )
    def me(self, request):
        user = request.user

        # 🔐 Sécurité
        if user.role != "paysan":
            raise PermissionDenied("Accès réservé aux paysans")

        # ========================
        # 📥 GET → récupérer profil
        # ========================
        if request.method == "GET":
            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "avatar": user.avatar.url if user.avatar else None,
                "first_name": user.first_name,
                "last_name": user.last_name,
            })

        # ========================
        # ➕ POST → créer profil
        # ========================
        if request.method == "POST":
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=201)

        # ========================
        # ✏️ PUT → modifier profil
        # ========================
        if request.method == "PUT":
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

    # =====================================================
    # 📌 FILTRAGE DES CONSULTATIONS
    # =====================================================
    def get_queryset(self):
        user = self.request.user

        # Admin → voit tout
        if user.is_staff:
            return Consultation.objects.all()

        # Expert → voit ses consultations
        if user.role == "expert":
            return Consultation.objects.filter(expert=user)

        # Paysan + Éleveur → voient leurs consultations
        return Consultation.objects.filter(paysan=user)

    # =====================================================
    # 📌 CRÉATION CONSULTATION (PAYSAN + ELEVEUR)
    # =====================================================
    def perform_create(self, serializer):
        user = self.request.user

        # ❌ empêcher expert de créer
        if user.role == "expert":
            raise PermissionDenied("Un expert ne peut pas créer une consultation.")

        # 🔥 récupérer expert depuis le frontend
        expert_id = self.request.data.get("expert")

        if not expert_id:
            raise PermissionDenied("Vous devez sélectionner un expert.")

        serializer.save(
            paysan=user,       # paysan OU eleveur (même champ)
            expert_id=expert_id
        )

    # =====================================================
    # ✅ EXPERT ACCEPTE
    # =====================================================
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsExpert])
    def accept(self, request, pk=None):
        consultation = self.get_object()

        if consultation.expert != request.user:
            raise PermissionDenied("Vous n'êtes pas assigné à cette consultation.")

        consultation.status = "accepted"
        consultation.save()

        return Response({"status": "accepted"})

    # =====================================================
    # ❌ EXPERT REFUSE
    # =====================================================
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsExpert])
    def reject(self, request, pk=None):
        consultation = self.get_object()

        if consultation.expert != request.user:
            raise PermissionDenied("Vous n'êtes pas assigné à cette consultation.")

        consultation.status = "rejected"
        consultation.save()

        return Response({"status": "rejected"})

    # =====================================================
    # 🔒 CLOTURE (PAYSAN / ELEVEUR / ADMIN)
    # =====================================================
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        consultation = self.get_object()

        if not (
            request.user.is_staff or
            consultation.paysan == request.user or
            consultation.expert == request.user
        ):
            raise PermissionDenied("Accès refusé.")

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


# ============================================================
#  ADMIN API (VALIDATION UTILISATEURS)
# ============================================================
class AdminVerifyUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.role != "admin":
            raise PermissionDenied("Accès réservé à l'admin")

        try:
            user = User.objects.get(id=user_id)
            user.is_verified = True
            user.save()
            return Response({"message": "Utilisateur validé"})
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable"}, status=404)


class AdminDeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if request.user.role != "admin":
            raise PermissionDenied("Accès réservé à l'admin")

        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "Utilisateur supprimé"})
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_pending_users(request):
    if request.user.role != "admin":
        raise PermissionDenied("Accès réservé à l'admin")

    users = User.objects.filter(is_verified=False)

    data = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
        }
        for u in users
    ]

    return Response(data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def admin_verify_user(request, user_id):
    if request.user.role != "admin":
        raise PermissionDenied("Accès réservé à l'admin")

    try:
        user = User.objects.get(id=user_id)
        user.is_verified = True
        user.save()
        return Response({"message": "Utilisateur validé"})
    except User.DoesNotExist:
        return Response({"error": "Utilisateur introuvable"}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def admin_delete_user(request, user_id):
    if request.user.role != "admin":
        raise PermissionDenied("Accès réservé à l'admin")

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "Utilisateur supprimé"})
    except User.DoesNotExist:
        return Response({"error": "Utilisateur introuvable"}, status=404)
    
 # ============================================================
 #  ModuleViewSet (Module de Guide)
 # ============================================================
   

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all().order_by("-created_at")
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # tout le monde peut voir les modules validés
        return Module.objects.all()

    def perform_create(self, serializer):
        # seul expert peut créer
        if self.request.user.role != "expert":
            raise PermissionDenied("Seuls les experts peuvent publier")

        serializer.save(expert=self.request.user)

 # ============================================================
 #  ElevageViewSet
 # ============================================================
 

class ElevageViewSet(viewsets.ModelViewSet):
    queryset = Elevage.objects.all().order_by("-created_at")
    serializer_class = ElevageSerializer
    permission_classes = [IsAuthenticated, IsEleveur]

    # 👇 Filtrer uniquement les élevages de l'utilisateur connecté
    def get_queryset(self):
        user = self.request.user

        # Admin voit tout
        if user.role == "admin":
            return Elevage.objects.all()

        # Eleveur voit seulement ses élevages
        return Elevage.objects.filter(user=user)

    # 👇 Lors de la création, on attache automatiquement l'utilisateur
    def perform_create(self, serializer):
        if self.request.user.role != "eleveur":
            raise PermissionDenied("Seuls les éleveurs peuvent créer un élevage")

        serializer.save(user=self.request.user)

 # ============================================================ 
 # Suspension / Réactivation d'un utilisateur (Admin)   
 # ============================================================
@api_view(['POST'])
@permission_classes([IsAdminUser])
def suspend_user(request, user_id):

    user = get_object_or_404(User, id=user_id)

    user.is_suspended = True
    user.save()

    return Response({
        "message": "Utilisateur suspendu"
    })
@api_view(['POST'])
@permission_classes([IsAdminUser])
def unsuspend_user(request, user_id):

    user = get_object_or_404(User, id=user_id)

    user.is_suspended = False
    user.save()

    return Response({
        "message": "Utilisateur réactivé"
    })