from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_verified')
    list_filter = ('role', 'is_verified')
    actions = ['validate_users']

    def validate_users(self, request, queryset):
        queryset.update(is_verified=True)