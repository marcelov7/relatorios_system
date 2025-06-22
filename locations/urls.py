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
    path('equipamentos/criar/', views.equipamento_create, name='equipamento_create'),
] 