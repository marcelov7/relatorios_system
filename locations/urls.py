from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Locais
    path('locais/', views.local_list, name='local_list'),
    path('locais/criar/', views.local_create, name='local_create'),
    path('locais/<int:pk>/', views.local_detail, name='local_detail'),
    path('locais/<int:pk>/editar/', views.local_edit, name='local_edit'),
    
    # Equipamentos
    path('equipamentos/', views.equipamento_list, name='equipamento_list'),
    path('equipamentos/<int:pk>/', views.equipamento_detail, name='equipamento_detail'),
    path('equipamentos/criar/', views.equipamento_create, name='equipamento_create'),
    path('equipamentos/<int:pk>/editar/', views.equipamento_edit, name='equipamento_edit'),
    path('equipamentos/<int:pk>/excluir/', views.equipamento_delete, name='equipamento_delete'),
    
    # URLs para Motores Elétricos
    path('motores/', views.motor_list, name='motor_list'),
    path('motores/dashboard/', views.motor_dashboard, name='motor_dashboard'),
    path('motores/<int:pk>/', views.motor_detail, name='motor_detail'),
    path('motores/criar/', views.motor_create, name='motor_create'),
    path('motores/<int:pk>/editar/', views.motor_edit, name='motor_edit'),
    path('motores/<int:pk>/excluir/', views.motor_delete, name='motor_delete'),
] 