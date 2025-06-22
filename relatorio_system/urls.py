"""
URL configuration for relatorio_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('reports/', include('reports.urls')),
    path('dashboard/', include('dashboard.urls')),
    # path('locations/', include('locations.urls')),  # Temporariamente desabilitado
    # path('notifications/', include('notifications_app.urls')),
    # path('inbox/notifications/', include('notifications.urls', namespace='notifications')),
    
    # URLs de autenticação do Django
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='authentication/password_change.html',
        success_url='/profile/'
    ), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='authentication/password_change_done.html'
    ), name='password_change_done'),
    
    path('', include('core.urls')),  # Core URLs por último para não interceptar outras URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) 