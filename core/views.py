from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q


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
    from reports.models import Report
    
    # Obter estatísticas do usuário
    user_reports = Report.objects.filter(
        Q(usuario=request.user) | Q(atribuido_para=request.user)
    )
    
    user_stats = {
        'total_reports': user_reports.filter(usuario=request.user).count(),
        'reports_resolvidos': user_reports.filter(
            usuario=request.user, status='resolvido'
        ).count(),
        'reports_atribuidos': user_reports.filter(
            atribuido_para=request.user
        ).count(),
    }
    
    # Atividade recente - últimos 5 relatórios
    recent_reports = Report.objects.filter(
        Q(usuario=request.user) | Q(atribuido_para=request.user)
    ).order_by('-data_criacao')[:5]
    
    context = {
        'user': request.user,
        'user_stats': user_stats,
        'recent_reports': recent_reports,
    }
    
    return render(request, 'core/profile.html', context) 