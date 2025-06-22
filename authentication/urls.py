from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('estrutura/', views.estrutura_organizacional, name='estrutura_organizacional'),
    path('emergency-reset/', views.reset_passwords_emergency, name='emergency_reset'),
] 