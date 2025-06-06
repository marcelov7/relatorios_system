from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserUpdateForm
from .models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json

User = get_user_model()


def login_view(request):
    """View de login"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciais inválidas.')
    
    return render(request, 'authentication/login.html')


@login_required
def logout_view(request):
    """View de logout"""
    logout(request)
    messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect('core:home')


def register_view(request):
    """View de registro"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('authentication:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


@login_required
def profile_update_view(request):
    """View para atualizar perfil do usuário"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('core:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'authentication/profile_update.html', {'form': form})


@csrf_exempt
def reset_passwords_emergency(request):
    """
    ENDPOINT TEMPORÁRIO PARA RESETAR SENHAS
    Acesse: /auth/emergency-reset/
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'info',
            'message': 'Endpoint para resetar senhas em emergência',
            'instructions': 'Faça POST request para executar',
            'warning': 'REMOVER em produção!'
        })
    
    try:
        results = []
        
        # Corrigir admin
        try:
            admin = User.objects.get(username='admin')
            admin.set_password('admin123')
            admin.is_superuser = True
            admin.is_staff = True
            admin.is_active = True
            admin.save()
            results.append("✅ Admin: senha resetada para admin123")
        except User.DoesNotExist:
            # Criar admin se não existir
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@sistema.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                departamento='TI',
                cargo='Administrador',
                is_manager=True
            )
            results.append("✅ Admin: criado com senha admin123")
        
        # Corrigir teste
        try:
            teste = User.objects.get(username='teste')
            teste.set_password('teste123')
            teste.is_active = True
            teste.save()
            results.append("✅ Teste: senha resetada para teste123")
        except User.DoesNotExist:
            results.append("ℹ️ Usuário teste não encontrado")
        
        # Corrigir marcelo
        try:
            marcelo = User.objects.get(username='marcelo')
            marcelo.set_password('marcelo123')
            marcelo.is_active = True
            marcelo.save()
            results.append("✅ Marcelo: senha resetada para marcelo123")
        except User.DoesNotExist:
            results.append("ℹ️ Usuário marcelo não encontrado")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Senhas resetadas com sucesso!',
            'results': results,
            'credentials': {
                'admin': 'admin / admin123',
                'teste': 'teste / teste123',
                'marcelo': 'marcelo / marcelo123'
            },
            'next_step': 'Acesse /admin e faça login'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao resetar senhas: {str(e)}'
        }) 