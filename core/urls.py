from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    PaysanViewSet,
    RegisterAPIView,
    LoginAPIView,
    UserViewSet,
    ExpertViewSet,
    ConsultationViewSet,
    MessageViewSet,
    MeAPIView
)

# Router DRF
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'experts', ExpertViewSet, basename='experts')
router.register(r'paysans', PaysanViewSet, basename='paysans')
router.register(r'consultations', ConsultationViewSet, basename='consultations')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    # AUTH
    path('auth/register/', RegisterAPIView.as_view(), name='register'),

    # LOGIN (email ou username)
    path('auth/login/', LoginAPIView.as_view(), name='login'),

     # ✅ PROFIL PAYSAN
    path("me/", MeAPIView.as_view()),

    # Routes API
    path('', include(router.urls)),
]