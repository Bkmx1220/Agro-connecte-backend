from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    ElevageViewSet,
    ModuleViewSet,
    PaysanViewSet,
    RegisterAPIView,
    LoginAPIView,
    UserViewSet,
    ExpertViewSet,
    ConsultationViewSet,
    MessageViewSet,
    ModuleViewSet,
    ElevageViewSet,
    MeAPIView,
    admin_pending_users,
    AdminVerifyUserView,
    AdminDeleteUserView,
    suspend_user,
    unsuspend_user, 
    
)

# Router DRF
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'experts', ExpertViewSet, basename='experts')
router.register(r'paysans', PaysanViewSet, basename='paysans')
router.register(r'consultations', ConsultationViewSet, basename='consultations')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'modules', ModuleViewSet, basename='modules')
router.register(r'elevages', ElevageViewSet, basename='elevages')

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
    path('admin/users/suspend/<int:user_id>/', suspend_user, name='admin_suspend_user'),
    path('admin/users/unsuspend/<int:user_id>/', unsuspend_user, name='admin_unsuspend_user'),
]