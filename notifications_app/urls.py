from django.urls import path
from . import views

app_name = 'notifications_app'

urlpatterns = [
    # Principais
    path('', views.notification_list, name='list'),
    path('settings/', views.notification_settings, name='settings'),
    path('send/', views.send_custom_notification, name='send'),
    
    # Ações
    path('mark-read/<str:notification_type>/<int:notification_id>/', 
         views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('delete/<str:notification_type>/<int:notification_id>/', 
         views.delete_notification, name='delete'),
    
    # APIs
    path('api/unread-count/', views.api_unread_count, name='api_unread_count'),
    path('api/recent/', views.api_recent_notifications, name='api_recent_notifications'),
] 