from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Perfil, Unidade, Setor
from .forms import UserAdminForm


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Administração de perfis"""
    list_display = ['nome', 'nivel_acesso', 'ativo', 'created_at']
    list_filter = ['nivel_acesso', 'ativo', 'created_at']
    search_fields = ['nome', 'descricao']
    ordering = ['nivel_acesso', 'nome']
    list_editable = ['ativo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao')
        }),
        ('Configurações', {
            'fields': ('nivel_acesso', 'ativo')
        }),
    )


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    """Administração de unidades"""
    list_display = ['codigo', 'nome', 'responsavel', 'ativo', 'created_at']
    list_filter = ['ativo', 'created_at']
    search_fields = ['nome', 'codigo', 'responsavel']
    ordering = ['nome']
    list_editable = ['ativo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'nome', 'descricao')
        }),
        ('Gestão', {
            'fields': ('responsavel', 'ativo')
        }),
    )


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    """Administração de setores"""
    list_display = ['codigo', 'get_nome_display', 'unidade', 'responsavel', 'ativo', 'created_at']
    list_filter = ['nome', 'unidade', 'ativo', 'created_at']
    search_fields = ['codigo', 'responsavel', 'unidade__nome']
    ordering = ['nome']
    list_editable = ['ativo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'nome', 'descricao')
        }),
        ('Organização', {
            'fields': ('unidade', 'responsavel')
        }),
        ('Configurações', {
            'fields': ('ativo',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administração de usuários com campos personalizados"""
    form = UserAdminForm
    
    # Campos mostrados na listagem
    list_display = [
        'id', 'username', 'nome', 'email', 'get_perfil_display', 'get_unidade_display', 
        'get_setor_display', 'ativo', 'is_staff', 'created_at'
    ]
    
    # Campos para filtrar
    list_filter = [
        'ativo', 'is_staff', 'is_superuser', 'is_manager', 
        'perfil_ref', 'unidade_ref', 'setor_ref', 'created_at'
    ]
    
    # Campos para busca
    search_fields = ['username', 'nome', 'email', 'departamento', 'cargo']
    
    # Campos ordenáveis
    ordering = ['-created_at']
    
    # Campos editáveis na listagem
    list_editable = ['ativo']
    
    # Organização dos campos no formulário de edição
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('username', 'nome', 'email', 'password')
        }),
        ('Estrutura Organizacional', {
            'fields': ('perfil_ref', 'unidade_ref', 'setor_ref'),
            'description': 'Use os campos abaixo para definir a estrutura organizacional do usuário'
        }),
        ('Campos Legacy (Compatibilidade)', {
            'fields': ('perfil_id', 'unidade_id', 'setor_id', 'departamento', 'cargo'),
            'classes': ('collapse',),
            'description': 'Campos de compatibilidade - prefira usar os campos acima'
        }),
        ('Informações de Contato', {
            'fields': ('telefone', 'foto_perfil')
        }),
        ('Permissões', {
            'fields': ('ativo', 'is_staff', 'is_superuser', 'is_manager', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos para formulário de adição
    add_fieldsets = (
        ('Informações Básicas', {
            'classes': ('wide',),
            'fields': ('username', 'nome', 'email', 'password1', 'password2'),
        }),
        ('Estrutura Organizacional', {
            'classes': ('wide',),
            'fields': ('perfil_ref', 'unidade_ref', 'setor_ref'),
        }),
        ('Configurações', {
            'classes': ('wide',),
            'fields': ('ativo', 'is_staff', 'is_manager'),
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    # Filtro horizontal para grupos e permissões
    filter_horizontal = ['groups', 'user_permissions']
    
    def get_queryset(self, request):
        """Otimizar queryset"""
        return super().get_queryset(request).select_related('perfil_ref', 'unidade_ref', 'setor_ref')
    
    def save_model(self, request, obj, form, change):
        """Override save para sincronizar campos"""
        # Garantir que os campos sejam sincronizados
        if obj.nome:
            nome_parts = obj.nome.split()
            if nome_parts:
                obj.first_name = nome_parts[0]
                if len(nome_parts) > 1:
                    obj.last_name = ' '.join(nome_parts[1:])
        
        # Sincronizar ativo com is_active
        obj.is_active = obj.ativo
        
        super().save_model(request, obj, form, change) 