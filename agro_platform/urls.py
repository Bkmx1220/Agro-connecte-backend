from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # ========================
    # ADMIN
    # ========================
    path('admin/', admin.site.urls),

    # ========================
    # API CORE (LOGIN, USERS, EXPERTS, ETC.)
    # ========================
    path('api/', include('core.urls')),

    # ========================
    # JWT REFRESH
    # ========================
    path(
        'api/auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]

# ========================
# MEDIA (DEV ONLY)
# ========================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
