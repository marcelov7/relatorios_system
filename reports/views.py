from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Report, ReportCategory, ReportData
from .forms import ReportForm, ReportDataForm
from .utils import generate_pdf_report, generate_excel_report
import json


@login_required
def report_list(request):
    """Lista de relatórios"""
    reports = Report.objects.all()
    
    # Filtros
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if category_id:
        reports = reports.filter(category_id=category_id)
    
    if status:
        reports = reports.filter(status=status)
    
    if search:
        reports = reports.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ReportCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_status': status,
        'search_query': search,
    }
    
    return render(request, 'reports/report_list.html', context)


@login_required
def report_detail(request, pk):
    """Detalhes do relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Incrementar visualizações
    report.views_count += 1
    report.save()
    
    # Obter dados do relatório
    report_data = report.data.all()
    
    context = {
        'report': report,
        'report_data': report_data,
    }
    
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_create(request):
    """Criar novo relatório"""
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.author = request.user
            report.save()
            messages.success(request, 'Relatório criado com sucesso!')
            return redirect('reports:detail', pk=report.pk)
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'title': 'Criar Relatório'
    })


@login_required
def report_edit(request, pk):
    """Editar relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Verificar se o usuário pode editar
    if report.author != request.user and not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para editar este relatório.')
        return redirect('reports:detail', pk=report.pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Relatório atualizado com sucesso!')
            return redirect('reports:detail', pk=report.pk)
    else:
        form = ReportForm(instance=report)
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'report': report,
        'title': 'Editar Relatório'
    })


@login_required
def report_delete(request, pk):
    """Excluir relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Verificar se o usuário pode excluir
    if report.author != request.user and not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para excluir este relatório.')
        return redirect('reports:detail', pk=report.pk)
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Relatório excluído com sucesso!')
        return redirect('reports:list')
    
    return render(request, 'reports/report_confirm_delete.html', {'report': report})


@login_required
def report_generate_pdf(request, pk):
    """Gerar PDF do relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Obter dados do relatório
    data = {}
    for item in report.data.all():
        data[item.field_name] = item.field_value
    
    # Incrementar downloads
    report.downloads_count += 1
    report.save()
    
    return generate_pdf_report(report, data)


@login_required
def report_generate_excel(request, pk):
    """Gerar Excel do relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Obter dados do relatório
    data = {}
    for item in report.data.all():
        data[item.field_name] = item.field_value
    
    # Incrementar downloads
    report.downloads_count += 1
    report.save()
    
    return generate_excel_report(report, data)


@login_required
def report_data_manage(request, pk):
    """Gerenciar dados do relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Verificar permissão
    if report.author != request.user and not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para gerenciar dados deste relatório.')
        return redirect('reports:detail', pk=report.pk)
    
    if request.method == 'POST':
        form = ReportDataForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.report = report
            data.save()
            messages.success(request, 'Dados adicionados com sucesso!')
            return redirect('reports:data_manage', pk=report.pk)
    else:
        form = ReportDataForm()
    
    report_data = report.data.all()
    
    context = {
        'report': report,
        'form': form,
        'report_data': report_data,
    }
    
    return render(request, 'reports/report_data_manage.html', context)


@login_required
def report_data_delete(request, pk, data_id):
    """Excluir dado do relatório"""
    report = get_object_or_404(Report, pk=pk)
    data = get_object_or_404(ReportData, pk=data_id, report=report)
    
    # Verificar permissão
    if report.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    if request.method == 'POST':
        data.delete()
        return JsonResponse({'success': True, 'message': 'Dado excluído com sucesso!'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def dashboard_reports(request):
    """Dashboard de relatórios para o usuário"""
    user_reports = Report.objects.filter(author=request.user)
    
    stats = {
        'total_reports': user_reports.count(),
        'draft_reports': user_reports.filter(status='draft').count(),
        'completed_reports': user_reports.filter(status='completed').count(),
        'total_views': sum(report.views_count for report in user_reports),
        'total_downloads': sum(report.downloads_count for report in user_reports),
    }
    
    recent_reports = user_reports.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_reports': recent_reports,
    }
    
    return render(request, 'reports/dashboard.html', context) 