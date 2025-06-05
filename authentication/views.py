from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserUpdateForm
from .models import User


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