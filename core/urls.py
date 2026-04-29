from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    ModuleViewSet,
    PaysanViewSet,
    RegisterAPIView,
    LoginAPIView,
    UserViewSet,
    ExpertViewSet,
    ConsultationViewSet,
    MessageViewSet,
    ModuleViewSet,
    MeAPIView,
    admin_pending_users,
    AdminVerifyUserView,
    AdminDeleteUserView
    
)

# Router DRF
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'experts', ExpertViewSet, basename='experts')
router.register(r'paysans', PaysanViewSet, basename='paysans')
router.register(r'consultations', ConsultationViewSet, basename='consultations')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'modules', ModuleViewSet, basename='modules')

urlpatterns = [
    # AUTH
    path('auth/register/', RegisterAPIView.as_view(), name='register'),

    # LOGIN (email ou username)
    path('auth/login/', LoginAPIView.as_view(), name='login'),

     # ✅ PROFIL PAYSAN
    path("me/", MeAPIView.as_view()),

    # Routes API
    path("", include(router.urls)),
 
    # ADMIN - GESTION DES UTILISATEURS
    path('admin/pending-users/', admin_pending_users, name='admin_pending_users'),
    
    path('admin/verify-user/<int:user_id>/', AdminVerifyUserView.as_view(), name='admin_verify_user'),
    path('admin/delete-user/<int:user_id>/', AdminDeleteUserView.as_view(), name='admin_delete_user'),
]