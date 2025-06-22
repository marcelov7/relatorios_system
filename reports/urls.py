from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Lista e visualização
    path('', views.report_list, name='list'),
    path('<int:pk>/', views.report_detail, name='detail'),
    
    # CRUD de relatórios
    path('create/', views.report_create, name='create'),
    path('bulk-create/', views.report_bulk_create, name='bulk_create'),
    path('<int:pk>/edit/', views.report_edit, name='edit'),
    path('<int:pk>/delete/', views.report_delete, name='delete'),
    path('<int:pk>/duplicate/', views.report_duplicate, name='duplicate'),
    path('<int:pk>/update-status/', views.report_update_status, name='update_status'),
    
    # Geração de arquivos
    path('<int:pk>/pdf/', views.report_generate_pdf, name='generate_pdf'),
    path('<int:pk>/excel/', views.report_generate_excel, name='generate_excel'),
    
    # Gerenciamento de dados
    path('<int:pk>/data/', views.report_data_manage, name='data_manage'),
    path('<int:pk>/data/<int:data_id>/delete/', views.report_data_delete, name='data_delete'),
    
    # Dashboard
    path('dashboard/', views.dashboard_reports, name='dashboard'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('analytics/api/', views.analytics_api, name='analytics_api'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
    
    # APIs
    path('api/equipamentos-por-local/<int:local_id>/', views.api_equipamentos_por_local, name='api_equipamentos_por_local'),
] 