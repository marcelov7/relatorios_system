from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    """Página inicial do sistema"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'core/home.html')


def about(request):
    """Página sobre o sistema"""
    return render(request, 'core/about.html')


@login_required
def profile(request):
    """Perfil do usuário"""
    return render(request, 'core/profile.html', {
        'user': request.user
    }) 