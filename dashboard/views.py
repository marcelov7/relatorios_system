from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import JsonResponse
from reports.models import Report, ReportCategory
from datetime import datetime, timedelta
import json

User = get_user_model()


@login_required
def index(request):
    """Dashboard principal"""
    user = request.user
    
    # Estatísticas gerais
    total_reports = Report.objects.count()
    user_reports = Report.objects.filter(created_by=user).count()
    total_users = User.objects.count()
    recent_reports = Report.objects.order_by('-created_at')[:5]
    
    # Estatísticas por categoria
    categories_stats = ReportCategory.objects.annotate(
        report_count=Count('reports')
    ).order_by('-report_count')
    
    # Relatórios por status
    status_stats = Report.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Atividade recente (últimos 30 dias)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_activity = Report.objects.filter(
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')[:10]
    
    # Top autores
    top_authors = User.objects.annotate(
        report_count=Count('created_reports')
    ).filter(report_count__gt=0).order_by('-report_count')[:5]
    
    context = {
        'total_reports': total_reports,
        'user_reports': user_reports,
        'total_users': total_users,
        'recent_reports': recent_reports,
        'categories_stats': categories_stats,
        'status_stats': status_stats,
        'recent_activity': recent_activity,
        'top_authors': top_authors,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def analytics(request):
    """Página de analytics avançadas"""
    
    # Dados para gráficos
    # Relatórios por mês (últimos 12 meses)
    reports_by_month = []
    for i in range(12):
        month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Report.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        reports_by_month.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    reports_by_month.reverse()
    
    # Relatórios por categoria
    category_data = list(ReportCategory.objects.annotate(
        report_count=Count('reports')
    ).values('name', 'report_count', 'color'))
    
    # Usuários mais ativos
    active_users = list(User.objects.annotate(
        report_count=Count('created_reports')
    ).filter(report_count__gt=0).order_by('-report_count')[:10].values(
        'username', 'first_name', 'last_name', 'report_count'
    ))
    
    context = {
        'reports_by_month': json.dumps(reports_by_month),
        'category_data': json.dumps(category_data),
        'active_users': active_users,
    }
    
    return render(request, 'dashboard/analytics.html', context)


@login_required
def api_reports_by_status(request):
    """API para dados de relatórios por status"""
    data = list(Report.objects.values('status').annotate(
        count=Count('id')
    ).values('status', 'count'))
    
    # Traduzir status para português
    status_translation = {
        'draft': 'Rascunho',
        'pending': 'Pendente',
        'approved': 'Aprovado',
        'rejected': 'Rejeitado',
    }
    
    for item in data:
        item['status_display'] = status_translation.get(item['status'], item['status'])
    
    return JsonResponse(data, safe=False)


@login_required
def api_reports_by_category(request):
    """API para dados de relatórios por categoria"""
    data = list(ReportCategory.objects.annotate(
        report_count=Count('reports')
    ).values('name', 'report_count', 'color'))
    
    return JsonResponse(data, safe=False)


@login_required
def api_recent_activity(request):
    """API para atividade recente"""
    days = int(request.GET.get('days', 7))
    start_date = datetime.now() - timedelta(days=days)
    
    reports = Report.objects.filter(
        created_at__gte=start_date
    ).select_related('author', 'category').order_by('-created_at')[:20]
    
    data = []
    for report in reports:
        data.append({
            'title': report.title,
            'author': report.created_by.get_full_name(),
            'category': report.category.name,
            'status': report.get_status_display(),
            'created_at': report.created_at.strftime('%d/%m/%Y %H:%M'),
            'url': f'/reports/{report.id}/',
        })
    
    return JsonResponse(data, safe=False)


@login_required
def user_statistics(request):
    """Estatísticas específicas do usuário"""
    user = request.user
    
    # Relatórios do usuário
    user_reports = Report.objects.filter(created_by=user)
    
    # Estatísticas
    stats = {
        'total_reports': user_reports.count(),
        'draft_reports': user_reports.filter(status='draft').count(),
        'approved_reports': user_reports.filter(status='approved').count(),
        'pending_reports': user_reports.filter(status='pending').count(),
        'rejected_reports': user_reports.filter(status='rejected').count(),
        'total_views': 0,  # Implementar depois
        'total_downloads': 0,  # Implementar depois
    }
    
    # Relatórios por categoria do usuário
    user_categories = user_reports.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Relatórios recentes do usuário
    recent_user_reports = user_reports.order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'user_categories': user_categories,
        'recent_user_reports': recent_user_reports,
    }
    
    return render(request, 'dashboard/user_statistics.html', context) 