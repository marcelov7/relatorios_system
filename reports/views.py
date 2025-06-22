from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from locations.models import Local, Equipamento
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Report, ReportCategory, ReportData, ReportImage, ReportUpdate
from .forms import ReportForm, ReportDataForm, ReportImageFormSet, ReportFilterForm, ReportUpdateForm, ReportUpdateImageFormSet
from .utils import generate_pdf_report, generate_excel_report
import json
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from .analytics_simple import SimpleDashboardData, SimpleReportAnalytics


@login_required
def report_list(request):
    """Lista de relatórios com paginação e filtros avançados"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Query base com otimizações
    reports = Report.objects.select_related('local', 'equipamento', 'usuario').prefetch_related('imagens')
    
    # Filtros usando o formulário
    filter_form = ReportFilterForm(request.GET)
    
    # Estatísticas para exibir
    total_reports = reports.count()
    
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        prioridade = filter_form.cleaned_data.get('prioridade')
        search = filter_form.cleaned_data.get('search')
        data_inicio = filter_form.cleaned_data.get('data_inicio')
        data_fim = filter_form.cleaned_data.get('data_fim')
        periodo = filter_form.cleaned_data.get('periodo')
        local = filter_form.cleaned_data.get('local')
        equipamento = filter_form.cleaned_data.get('equipamento')
        usuario = filter_form.cleaned_data.get('usuario')
        ordenar_por = filter_form.cleaned_data.get('ordenar_por') or '-data_criacao'
        
        # Filtros básicos
    if status:
        reports = reports.filter(status=status)
    
        if prioridade:
            reports = reports.filter(prioridade=prioridade)
        
    if search:
        reports = reports.filter(
                Q(titulo__icontains=search) | 
                Q(descricao__icontains=search) |
                Q(usuario__first_name__icontains=search) |
                Q(usuario__last_name__icontains=search) |
                Q(usuario__username__icontains=search)
            )
        
        if local:
            reports = reports.filter(local=local)
        
        if equipamento:
            reports = reports.filter(equipamento=equipamento)
        
        if usuario:
            reports = reports.filter(
                Q(usuario__first_name__icontains=usuario) |
                Q(usuario__last_name__icontains=usuario) |
                Q(usuario__username__icontains=usuario)
            )
        
        # Lógica de filtros por data
        now = timezone.now()
        today = now.date()
        
        if periodo:
            if periodo == 'hoje':
                data_inicio = today
                data_fim = today
            elif periodo == 'ontem':
                yesterday = today - timedelta(days=1)
                data_inicio = yesterday
                data_fim = yesterday
            elif periodo == 'ultima_semana':
                data_inicio = today - timedelta(days=7)
                data_fim = today
            elif periodo == 'ultimo_mes':
                data_inicio = today - timedelta(days=30)
                data_fim = today
            elif periodo == 'ultimos_3_meses':
                data_inicio = today - timedelta(days=90)
                data_fim = today
            elif periodo == 'este_ano':
                data_inicio = today.replace(month=1, day=1)
                data_fim = today
        
        # Aplicar filtros de data
        if data_inicio:
            # Converter para datetime para incluir todo o dia
            data_inicio_dt = timezone.make_aware(
                datetime.combine(data_inicio, datetime.min.time())
            )
            reports = reports.filter(data_ocorrencia__gte=data_inicio_dt)
        
        if data_fim:
            # Converter para datetime para incluir todo o dia
            data_fim_dt = timezone.make_aware(
                datetime.combine(data_fim, datetime.max.time())
            )
            reports = reports.filter(data_ocorrencia__lte=data_fim_dt)
        
        # Aplicar ordenação
        reports = reports.order_by(ordenar_por)
    else:
        # Ordenação padrão se não há filtros
        reports = reports.order_by('-data_criacao')
    
    # Estatísticas após filtros
    filtered_count = reports.count()
    
    # Paginação configurável
    items_per_page = request.GET.get('per_page', 12)
    try:
        items_per_page = int(items_per_page)
        if items_per_page not in [6, 12, 24, 48]:
            items_per_page = 12
    except (ValueError, TypeError):
        items_per_page = 12
    
    paginator = Paginator(reports, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas por status (para exibir gráficos)
    status_stats = {
        'pendente': reports.filter(status='pendente').count(),
        'em_andamento': reports.filter(status='em_andamento').count(),
        'resolvido': reports.filter(status='resolvido').count(),
    }
    
    # Preservar parâmetros de filtro na paginação
    filter_params = request.GET.copy()
    if 'page' in filter_params:
        del filter_params['page']
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_reports': total_reports,
        'filtered_count': filtered_count,
        'status_stats': status_stats,
        'filter_params': filter_params.urlencode(),
        'items_per_page': items_per_page,
        'current_filters': {
            'status': filter_form.cleaned_data.get('status') if filter_form.is_valid() else '',
            'search': filter_form.cleaned_data.get('search') if filter_form.is_valid() else '',
            'periodo': filter_form.cleaned_data.get('periodo') if filter_form.is_valid() else '',
        }
    }
    
    return render(request, 'reports/report_list.html', context)


@login_required
def report_detail(request, pk):
    """Detalhes do relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Obter dados do relatório
    report_data = report.data.all()
    
    # Obter histórico de atualizações
    atualizacoes = report.atualizacoes.select_related('usuario').prefetch_related('imagens')
    
    # Verificar permissões
    pode_editar = report.pode_editar(request.user)
    pode_atualizar_status = report.pode_atualizar_status(request.user)
    
    context = {
        'report': report,
        'report_data': report_data,
        'atualizacoes': atualizacoes,
        'pode_editar': pode_editar,
        'pode_atualizar_status': pode_atualizar_status,
    }
    
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_create(request):
    """Criar novo relatório"""
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        image_formset = ReportImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and image_formset.is_valid():
            report = form.save(commit=False)
            report.usuario = request.user
            
            # 🧠 Lógica inteligente de status baseada em imagens e progresso
            has_main_image = bool(form.cleaned_data.get('imagem_principal'))
            has_additional_images = any(
                form.cleaned_data.get('imagem') for form in image_formset 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            )
            
            # Determinar status automaticamente
            if has_main_image or has_additional_images:
                if report.progresso == 0:
                    # Tem fotos mas progresso 0 = documentando problema
                    report.status = 'em_andamento'
                    report.progresso = 10  # Inicia com 10% por ter documentação
                elif report.progresso == 100:
                    # Progresso 100% = trabalho concluído
                    report.status = 'resolvido'
                else:
                    # Tem fotos e progresso intermediário = em andamento
                    report.status = 'em_andamento'
            
            report.save()
            
            # Salvar imagens adicionais
            image_formset.instance = report
            image_formset.save()
            
            messages.success(request, 'Relatório criado com sucesso!')
            return redirect('reports:detail', pk=report.pk)
    else:
        form = ReportForm()
        image_formset = ReportImageFormSet()
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'image_formset': image_formset,
        'title': 'Criar Relatório'
    })


@login_required
def report_edit(request, pk):
    """Editar relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Verificar se o usuário pode editar
    if not report.pode_editar(request.user):
        messages.error(request, 'Você não tem permissão para editar este relatório.')
        return redirect('reports:detail', pk=report.pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report)
        image_formset = ReportImageFormSet(request.POST, request.FILES, instance=report)
        
        if form.is_valid() and image_formset.is_valid():
            updated_report = form.save(commit=False)
            
            # 🧠 Lógica inteligente de status para edição
            has_main_image = bool(form.cleaned_data.get('imagem_principal')) or bool(report.imagem_principal)
            has_additional_images = any(
                form.cleaned_data.get('imagem') for form in image_formset 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
            ) or report.imagens.exists()
            
            # Atualizar status baseado em mudanças
            if has_main_image or has_additional_images:
                if updated_report.progresso == 100 and updated_report.status != 'resolvido':
                    updated_report.status = 'resolvido'
                elif updated_report.progresso > 0 and updated_report.status == 'pendente':
                    updated_report.status = 'em_andamento'
            
            updated_report.save()
            image_formset.save()
            messages.success(request, 'Relatório atualizado com sucesso!')
            return redirect('reports:detail', pk=report.pk)
    else:
        form = ReportForm(instance=report)
        image_formset = ReportImageFormSet(instance=report)
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'image_formset': image_formset,
        'report': report,
        'title': 'Editar Relatório'
    })


@login_required
def report_delete(request, pk):
    """Excluir relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Verificar se o usuário pode excluir
    if report.usuario != request.user and not request.user.is_staff:
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
    
    # Não incrementar downloads por enquanto (campo removido)
    # report.downloads_count += 1
    # report.save()
    
    return generate_pdf_report(report, data)


@login_required
def report_generate_excel(request, pk):
    """Gerar Excel do relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Obter dados do relatório
    data = {}
    for item in report.data.all():
        data[item.field_name] = item.field_value
    
    # Não incrementar downloads por enquanto (campo removido)
    # report.downloads_count += 1
    # report.save()
    
    return generate_excel_report(report, data)


@login_required
def report_data_manage(request, pk):
    """Gerenciar dados do relatório"""
    report = get_object_or_404(Report, pk=pk)
    
    # Verificar permissão
    if report.usuario != request.user and not request.user.is_staff:
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
        'total_downloads': 0,  # Campo removido temporariamente
    }
    
    recent_reports = user_reports.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_reports': recent_reports,
    }
    
    return render(request, 'reports/dashboard.html', context) 


@login_required
def api_equipamentos_por_local(request, local_id):
    """API para retornar equipamentos de um local específico"""
    try:
        local = get_object_or_404(Local, pk=local_id)
        equipamentos = Equipamento.objects.filter(
            local=local, 
            ativo=True
        ).order_by('nome')
        
        equipamentos_data = [
            {
                'id': eq.id,
                'nome': eq.nome,
                'codigo': eq.codigo,
                'tipo': eq.get_tipo_display() if eq.tipo else 'Não informado'
            }
            for eq in equipamentos
        ]
        
        return JsonResponse({
            'success': True,
            'equipamentos': equipamentos_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def report_duplicate(request, pk):
    """Duplicar relatório para outro equipamento"""
    original_report = get_object_or_404(Report, pk=pk)
    
    # Verificar permissão
    if original_report.usuario != request.user and not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para duplicar este relatório.')
        return redirect('reports:detail', pk=original_report.pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Criar novo relatório baseado no original
            new_report = form.save(commit=False)
            new_report.usuario = request.user
            new_report.titulo = f"{original_report.titulo} - Cópia"
            new_report.save()
            
            messages.success(request, f'Relatório duplicado com sucesso!')
            return redirect('reports:detail', pk=new_report.pk)
    else:
        # Pré-preencher formulário com dados do relatório original
        initial_data = {
            'titulo': f"{original_report.titulo} - Cópia",
            'descricao': original_report.descricao,
            'local': original_report.local,
            'data_ocorrencia': original_report.data_ocorrencia,
            'prioridade': original_report.prioridade,
            'status': 'pendente',  # Resetar status
            'progresso': 0,  # Resetar progresso
            'editavel': True,
        }
        form = ReportForm(initial=initial_data)
    
    return render(request, 'reports/report_duplicate.html', {
        'form': form,
        'original_report': original_report,
        'title': 'Duplicar Relatório'
    })


@login_required
def report_bulk_create(request):
    """Criar relatórios em lote para múltiplos equipamentos"""
    if request.method == 'POST':
        # Dados base do formulário
        titulo_base = request.POST.get('titulo_base')
        descricao = request.POST.get('descricao')
        local_id = request.POST.get('local')
        prioridade = request.POST.get('prioridade')
        data_ocorrencia = request.POST.get('data_ocorrencia')
        
        # Lista de equipamentos selecionados
        equipamentos_ids = request.POST.getlist('equipamentos')
        
        if not equipamentos_ids:
            messages.error(request, 'Selecione pelo menos um equipamento.')
            return render(request, 'reports/report_bulk_create.html', {
                'locais': Local.objects.filter(status='ativo'),
                'title': 'Criar Relatórios em Lote'
            })
        
        try:
            local = Local.objects.get(id=local_id)
            created_reports = []
            
            with transaction.atomic():
                for equipamento_id in equipamentos_ids:
                    equipamento = Equipamento.objects.get(id=equipamento_id)
                    
                    # Criar relatório individual
                    report = Report.objects.create(
                        titulo=f"{titulo_base} - {equipamento.nome}",
                        descricao=descricao,
                        local=local,
                        equipamento=equipamento,
                        usuario=request.user,
                        prioridade=prioridade,
                        data_ocorrencia=data_ocorrencia,
                        status='pendente',
                        progresso=0,
                        editavel=True
                    )
                    created_reports.append(report)
            
            messages.success(
                request, 
                f'{len(created_reports)} relatórios criados com sucesso!'
            )
            return redirect('reports:list')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar relatórios: {str(e)}')
    
    return render(request, 'reports/report_bulk_create.html', {
        'locais': Local.objects.filter(status='ativo'),
        'title': 'Criar Relatórios em Lote'
    })


@login_required
def report_update_status(request, pk):
    """Atualizar status e progresso do relatório via modal"""
    report = get_object_or_404(Report, pk=pk)
    
    # Verificar se o usuário pode atualizar o status
    if not report.pode_atualizar_status(request.user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para atualizar este relatório.'
            })
        messages.error(request, 'Você não tem permissão para atualizar este relatório.')
        return redirect('reports:detail', pk=pk)
    
    # Verificar se o relatório pode ser atualizado
    if report.status == 'resolvido':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Relatórios resolvidos não podem ser atualizados.'
            })
        messages.error(request, 'Relatórios resolvidos não podem ser atualizados.')
        return redirect('reports:detail', pk=pk)
    
    if request.method == 'POST':
        form = ReportUpdateForm(request.POST, report=report, user=request.user)
        image_formset = ReportUpdateImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and image_formset.is_valid():
            try:
                with transaction.atomic():
                    # Salvar dados anteriores para histórico
                    progresso_anterior = report.progresso
                    status_anterior = report.status
                    
                    # Criar registro de atualização
                    update = form.save(commit=False)
                    update.report = report
                    update.usuario = request.user
                    update.progresso_anterior = progresso_anterior
                    update.status_anterior = status_anterior
                    
                    # Determinar novo status baseado no progresso
                    novo_progresso = form.cleaned_data['progresso_novo']
                    if novo_progresso == 100:
                        novo_status = 'resolvido'
                    elif novo_progresso > 0:
                        novo_status = 'em_andamento'
                    else:
                        novo_status = 'pendente'
                    
                    update.status_novo = novo_status
                    update.save()
                    
                    # Salvar imagens da atualização
                    image_formset.instance = update
                    image_formset.save()
                    
                    # Atualizar o relatório principal
                    report.progresso = novo_progresso
                    report.status = novo_status
                    report.save()
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'Relatório atualizado com sucesso!',
                            'novo_progresso': novo_progresso,
                            'novo_status': novo_status,
                            'status_display': report.get_status_display(),
                            'redirect_url': f'/reports/{pk}/'
                        })
                    
                    messages.success(request, 'Relatório atualizado com sucesso!')
                    return redirect('reports:detail', pk=pk)
                    
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Erro ao atualizar relatório: {str(e)}'
                    })
                messages.error(request, f'Erro ao atualizar relatório: {str(e)}')
        else:
            # Retornar erros do formulário
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                if form.errors:
                    errors.update(form.errors)
                if image_formset.errors:
                    errors['images'] = image_formset.errors
                    
                return JsonResponse({
                    'success': False,
                    'message': 'Verifique os dados informados.',
                    'errors': errors
                })
    else:
        form = ReportUpdateForm(report=report, user=request.user)
        image_formset = ReportUpdateImageFormSet()
    
    # Para requisições AJAX, retornar o HTML do modal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        from django.urls import reverse
        
        # Definir action URL para o formulário
        action_url = reverse('reports:update_status', kwargs={'pk': pk})
        
        html = render_to_string('reports/report_update_modal.html', {
            'form': form,
            'image_formset': image_formset,
            'report': report,
            'action_url': action_url,
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': html
        })
    
    # Fallback para requisições normais
    return render(request, 'reports/report_update_form.html', {
        'form': form,
        'image_formset': image_formset,
        'report': report,
        'title': 'Atualizar Relatório'
    }) 


@login_required
def analytics_dashboard(request):
    """Dashboard de analytics inteligente para relatórios"""
    
    # Obter período selecionado
    period = request.GET.get('period', '30d')
    
    # Criar instância do dashboard
    dashboard = SimpleDashboardData(user=request.user, period=period)
    
    # Obter todos os dados
    data = dashboard.get_complete_dashboard_data()
    
    # Serializar dados para JSON de forma segura
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    from decimal import Decimal
    from datetime import datetime, date, timedelta
    
    def safe_serialize(obj):
        """Função para serializar objetos de forma segura, evitando referências circulares"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            # Para objetos complexos, retornar apenas valores básicos
            return str(obj)
        return obj
    
    # Criar uma cópia limpa dos dados para serialização
    clean_data = {}
    
    # Processar cada seção dos dados
    for key, value in data.items():
        if key == 'date_range':
            # Converter range de datas para strings
            if isinstance(value, tuple) and len(value) == 2:
                clean_data[key] = [
                    value[0].isoformat() if hasattr(value[0], 'isoformat') else str(value[0]),
                    value[1].isoformat() if hasattr(value[1], 'isoformat') else str(value[1])
                ]
            else:
                clean_data[key] = str(value)
        elif key == 'timeline':
            # Processar dados de timeline
            clean_timeline = []
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        clean_item = {}
                        for k, v in item.items():
                            if k == 'periodo':
                                clean_item[k] = v.isoformat() if hasattr(v, 'isoformat') else str(v)
                            else:
                                clean_item[k] = safe_serialize(v)
                        clean_timeline.append(clean_item)
            clean_data[key] = clean_timeline
        elif isinstance(value, list):
            # Processar listas (como priority_distribution, location_performance, etc.)
            clean_list = []
            for item in value:
                if isinstance(item, dict):
                    clean_item = {}
                    for k, v in item.items():
                        clean_item[k] = safe_serialize(v)
                    clean_list.append(clean_item)
                else:
                    clean_list.append(safe_serialize(item))
            clean_data[key] = clean_list
        elif isinstance(value, dict):
            # Processar dicionários
            clean_dict = {}
            for k, v in value.items():
                clean_dict[k] = safe_serialize(v)
            clean_data[key] = clean_dict
        else:
            # Valores simples
            clean_data[key] = safe_serialize(value)
    
    # Serializar para JSON
    try:
        dashboard_data_json = json.dumps(clean_data, ensure_ascii=False, indent=2)
    except Exception as e:
        # Fallback: criar estrutura mínima
        print(f"Erro na serialização: {e}")
        fallback_data = {
            'overview': data.get('overview', {}),
            'timeline': [],
            'priority_distribution': [],
            'location_performance': [],
            'equipment_issues': [],
            'period': period
        }
        dashboard_data_json = json.dumps(fallback_data, ensure_ascii=False)
    
    # Adicionar dados específicos para o template
    context = {
        'dashboard_data': data,
        'dashboard_data_json': dashboard_data_json,
        'period': period,
        'period_options': [
            ('7d', 'Últimos 7 dias'),
            ('30d', 'Últimos 30 dias'),
            ('90d', 'Últimos 90 dias'),
            ('365d', 'Último ano'),
        ],
        'user_is_staff': request.user.is_staff,
    }
    
    return render(request, 'reports/analytics_dashboard.html', context)


@login_required
def analytics_api(request):
    """API para dados de analytics em tempo real"""
    
    period = request.GET.get('period', '30d')
    chart_type = request.GET.get('chart', 'overview')
    
    analytics = SimpleReportAnalytics(
        user=request.user,
        date_range=SimpleDashboardData(period=period)._get_date_range(period)
    )
    
    data = {}
    
    if chart_type == 'overview':
        data = analytics.get_overview_stats()
    elif chart_type == 'priority':
        data = analytics.get_priority_distribution()
    elif chart_type == 'timeline':
        group_by = request.GET.get('group_by', 'day')
        data = analytics.get_timeline_data(group_by)
    elif chart_type == 'locations':
        data = analytics.get_location_performance()
    elif chart_type == 'equipment':
        data = analytics.get_equipment_issues()
    
    return JsonResponse(data, safe=False)


@login_required
def export_analytics(request):
    """Exportar dados de analytics"""
    
    period = request.GET.get('period', '30d')
    format_type = request.GET.get('format', 'json')
    
    dashboard = SimpleDashboardData(user=request.user, period=period)
    data = dashboard.get_complete_dashboard_data()
    
    if format_type == 'json':
        response = JsonResponse(data)
        response['Content-Disposition'] = f'attachment; filename="analytics_{period}.json"'
        return response
    
    # Implementar outros formatos (CSV, Excel) se necessário
    return JsonResponse({'error': 'Formato não suportado'}, status=400) 