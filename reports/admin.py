from django.contrib import admin
from .models import Report, ReportCategory, ReportData, ReportSchedule


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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin para relatórios"""
    list_display = [
        'title', 'author', 'category', 'status', 
        'views_count', 'downloads_count', 'created_at'
    ]
    list_filter = [
        'status', 'category', 'is_public', 'created_at', 'author'
    ]
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['id', 'views_count', 'downloads_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'title', 'description', 'category', 'author')
        }),
        ('Configurações', {
            'fields': ('status', 'is_public', 'start_date', 'end_date')
        }),
        ('Arquivos', {
            'fields': ('pdf_file', 'excel_file')
        }),
        ('Estatísticas', {
            'fields': ('views_count', 'downloads_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReportDataInline]

    def save_model(self, request, obj, form, change):
        if not change:  # Se está criando um novo relatório
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    """Admin para dados dos relatórios"""
    list_display = ['report', 'field_name', 'data_type', 'created_at']
    list_filter = ['data_type', 'created_at', 'report__category']
    search_fields = ['field_name', 'field_value', 'report__title']
    ordering = ['-created_at']


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    """Admin para agendamentos de relatórios"""
    list_display = [
        'report', 'frequency', 'is_active', 'next_run', 'last_run'
    ]
    list_filter = ['frequency', 'is_active', 'next_run']
    search_fields = ['report__title']
    ordering = ['next_run'] 