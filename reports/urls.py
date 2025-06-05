from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Lista e visualização
    path('', views.report_list, name='list'),
    path('<uuid:pk>/', views.report_detail, name='detail'),
    
    # CRUD de relatórios
    path('create/', views.report_create, name='create'),
    path('<uuid:pk>/edit/', views.report_edit, name='edit'),
    path('<uuid:pk>/delete/', views.report_delete, name='delete'),
    
    # Geração de arquivos
    path('<uuid:pk>/pdf/', views.report_generate_pdf, name='generate_pdf'),
    path('<uuid:pk>/excel/', views.report_generate_excel, name='generate_excel'),
    
    # Gerenciamento de dados
    path('<uuid:pk>/data/', views.report_data_manage, name='data_manage'),
    path('<uuid:pk>/data/<int:data_id>/delete/', views.report_data_delete, name='data_delete'),
    
    # Dashboard
    path('dashboard/', views.dashboard_reports, name='dashboard'),
] 