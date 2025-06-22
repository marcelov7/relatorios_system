from django.contrib import admin
from .models import Local, Equipamento, Motor


class EquipamentoInline(admin.TabularInline):
    """Inline para equipamentos no admin de locais"""
    model = Equipamento
    extra = 0
    fields = ['nome', 'codigo', 'tipo', 'status_operacional', 'fabricante', 'modelo']
    readonly_fields = ['data_criacao']


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    """Admin para locais"""
    list_display = [
        'nome', 'codigo', 'tipo', 'status', 'data_criacao'
    ]
    list_filter = ['tipo', 'status', 'data_criacao']
    search_fields = ['nome', 'codigo', 'endereco']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo', 'tipo', 'status')
        }),
        ('Localização', {
            'fields': ('endereco',)
        }),
        ('Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EquipamentoInline]


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    """Admin para equipamentos"""
    list_display = [
        'nome', 'codigo', 'local', 'tipo', 'fabricante', 'modelo',
        'status_operacional', 'ativo', 'data_criacao'
    ]
    list_filter = [
        'tipo', 'status_operacional', 'ativo', 'local', 'data_criacao',
        'data_instalacao'
    ]
    search_fields = [
        'nome', 'codigo', 'fabricante', 'modelo', 'numero_serie',
        'local__nome', 'local__codigo'
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['local', 'nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('local', 'nome', 'codigo', 'tipo', 'descricao')
        }),
        ('Especificações', {
            'fields': ('fabricante', 'modelo', 'numero_serie', 'data_instalacao')
        }),
        ('Status', {
            'fields': ('status_operacional', 'ativo')
        }),
        ('Sistema', {
            'fields': ('tenant_id', 'deleted_at', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('local')


@admin.register(Motor)
class MotorAdmin(admin.ModelAdmin):
    """Admin para motores elétricos"""
    list_display = [
        'nome', 'codigo', 'local', 'tipo', 'fabricante', 'modelo',
        'potencia', 'voltagem', 'rpm', 'status_operacional', 'ativo', 'data_criacao'
    ]
    list_filter = [
        'tipo', 'status_operacional', 'ativo', 'local', 'fabricante',
        'data_criacao', 'data_instalacao'
    ]
    search_fields = [
        'nome', 'codigo', 'fabricante', 'modelo', 'numero_serie',
        'local__nome', 'local__codigo'
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    ordering = ['local', 'nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('local', 'nome', 'codigo', 'tipo', 'descricao')
        }),
        ('Especificações Técnicas', {
            'fields': ('potencia', 'voltagem', 'corrente', 'rpm')
        }),
        ('Fabricante', {
            'fields': ('fabricante', 'modelo', 'numero_serie', 'data_instalacao')
        }),
        ('Status e Responsabilidade', {
            'fields': ('status_operacional', 'responsavel', 'ativo')
        }),
        ('Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('local', 'responsavel')
