from django.contrib import admin
from .models import Report, ReportCategory, ReportData, ReportImage, ReportUpdate, ReportUpdateImage


@admin.register(ReportCategory)
class ReportCategoryAdmin(admin.ModelAdmin):
    """Admin para categorias de relatórios"""
    list_display = ['name', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


class ReportDataInline(admin.TabularInline):
    """Inline para dados do relatório"""
    model = ReportData
    extra = 1
    fields = ['field_name', 'field_value', 'data_type']


class ReportImageInline(admin.TabularInline):
    """Inline para imagens do relatório"""
    model = ReportImage
    extra = 1
    fields = ['imagem', 'descricao', 'ordem']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin para relatórios baseado na nova estrutura"""
    list_display = [
        'titulo', 'usuario', 'status', 'prioridade', 
        'progresso', 'local_id', 'equipamento_id', 'data_criacao'
    ]
    list_filter = [
        'status', 'prioridade', 'editavel', 'data_criacao', 'usuario'
    ]
    search_fields = ['titulo', 'descricao', 'usuario__username']
    readonly_fields = ['id', 'data_criacao', 'data_atualizacao']
    ordering = ['-data_criacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'titulo', 'descricao', 'usuario')
        }),
        ('Localização e Equipamento', {
            'fields': ('local_id', 'equipamento_id', 'data_ocorrencia')
        }),
        ('Status e Prioridade', {
            'fields': ('status', 'prioridade', 'progresso', 'editavel')
        }),
        ('Imagens', {
            'fields': ('imagem_principal',)
        }),
        ('Sistema', {
            'fields': ('tenant_id', 'deleted_at', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReportDataInline, ReportImageInline]

    def save_model(self, request, obj, form, change):
        if not change:  # Se está criando um novo relatório
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    """Admin para dados dos relatórios"""
    list_display = ['report', 'field_name', 'data_type', 'created_at']
    list_filter = ['data_type', 'created_at']
    search_fields = ['field_name', 'field_value', 'report__titulo']
    ordering = ['-created_at']


@admin.register(ReportImage)
class ReportImageAdmin(admin.ModelAdmin):
    """Admin para imagens dos relatórios"""
    list_display = ['report', 'descricao', 'ordem', 'data_upload']
    list_filter = ['data_upload']
    search_fields = ['descricao', 'report__titulo']
    ordering = ['report', 'ordem', '-data_upload']


class ReportUpdateImageInline(admin.TabularInline):
    model = ReportUpdateImage
    extra = 1


@admin.register(ReportUpdate)
class ReportUpdateAdmin(admin.ModelAdmin):
    list_display = ['report', 'usuario', 'progresso_anterior', 'progresso_novo', 'status_novo', 'data_atualizacao']
    list_filter = ['status_novo', 'data_atualizacao']
    search_fields = ['report__titulo', 'usuario__username', 'descricao_atualizacao']
    readonly_fields = ['data_atualizacao']
    inlines = [ReportUpdateImageInline]
    date_hierarchy = 'data_atualizacao'


@admin.register(ReportUpdateImage)
class ReportUpdateImageAdmin(admin.ModelAdmin):
    list_display = ['update', 'descricao', 'data_upload']
    list_filter = ['data_upload']
    search_fields = ['update__report__titulo', 'descricao'] 