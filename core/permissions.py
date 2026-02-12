# core/permissions.py
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from core.models import Expert

class IsAdminOrReadOnly(permissions.BasePermission):
    """Seul l'admin peut écrire; les autres peuvent lire."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Seul le propriétaire de l'objet peut le modifier."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Cas objet avec champ user (Expert par ex.)
        if hasattr(obj, "user"):
            return obj.user == request.user

        # Cas User lui-même
        return obj == request.user


class IsExpert(BasePermission):
    """Autorise uniquement les utilisateurs ayant un profil Expert."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return Expert.objects.filter(user=request.user).exists()



class IsPaysan(permissions.BasePermission):
    """Autorise seulement les users avec role 'paysan'."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'paysan'
        )


# 🔥 IMPORTANT : Consultation (security)
class IsConsultationParticipant(permissions.BasePermission):
    """Autorise seulement le paysan, l’expert assigné ou l’admin."""
    def has_object_permission(self, request, view, consultation):
        return (
            request.user.is_staff or
            consultation.paysan == request.user or
            consultation.expert == request.user
        )


# 🔥 IMPORTANT : Messages (chat security)
class IsMessageParticipant(permissions.BasePermission):
    """Seuls l’expéditeur et le destinataire peuvent accéder au message."""
    def has_object_permission(self, request, view, message):
        return (
            request.user.is_staff or
            message.sender == request.user or
            message.receiver == request.user
        )
