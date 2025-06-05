from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin personalizado para o modelo User"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'departamento', 'is_manager', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_manager', 'departamento', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('telefone', 'departamento', 'cargo', 'foto_perfil', 'is_manager')
        }),
    ) 