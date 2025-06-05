from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('analytics/', views.analytics, name='analytics'),
    path('user-stats/', views.user_statistics, name='user_statistics'),
    
    # APIs para gráficos
    path('api/reports-by-status/', views.api_reports_by_status, name='api_reports_by_status'),
    path('api/reports-by-category/', views.api_reports_by_category, name='api_reports_by_category'),
    path('api/recent-activity/', views.api_recent_activity, name='api_recent_activity'),
] 