from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Local, Equipamento
from .forms import LocalForm, EquipamentoForm, LocalFilterForm, EquipamentoFilterForm


# Views para Locais
@login_required
def local_list(request):
    """Lista de locais"""
    # Query base para locais
    locais = Local.objects.all()
    
    # Adicionar anotações e ordenação
    locais = locais.annotate(
        equipamentos_count=Count('equipamentos'),
        equipamentos_ativos=Count('equipamentos', filter=Q(equipamentos__status_operacional='operando'))
    ).order_by('nome')
    
    # Filtros
    form = LocalFilterForm(request.GET)
    if form.is_valid():
        tipo = form.cleaned_data.get('tipo')
        status = form.cleaned_data.get('status')
        search = form.cleaned_data.get('search')
        
        if tipo:
            locais = locais.filter(tipo=tipo)
        if status:
            locais = locais.filter(status=status)
        if search:
            locais = locais.filter(
                Q(nome__icontains=search) |
                Q(codigo__icontains=search) |
                Q(endereco__icontains=search)
            )
    
    # Paginação
    paginator = Paginator(locais, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': form,
    }
    
    return render(request, 'locations/local_list.html', context)


@login_required
def local_detail(request, pk):
    """Detalhes do local"""
    local = get_object_or_404(Local, pk=pk)
    equipamentos = local.equipamentos.all()
    
    # Estatísticas
    stats = {
        'total_equipamentos': equipamentos.count(),
        'equipamentos_ativos': equipamentos.filter(status_operacional='operando').count(),
        'equipamentos_manutencao': equipamentos.filter(status_operacional='manutencao').count(),
        'equipamentos_inativos': equipamentos.filter(status_operacional='inativo').count(),
    }
    
    context = {
        'local': local,
        'equipamentos': equipamentos[:10],  # Mostrar apenas os primeiros 10
        'stats': stats,
    }
    
    return render(request, 'locations/local_detail.html', context)


@login_required
def local_create(request):
    """Criar novo local"""
    if request.method == 'POST':
        form = LocalForm(request.POST)
        if form.is_valid():
            local = form.save()
            messages.success(request, f'Local "{local.nome}" criado com sucesso!')
            return redirect('locations:local_detail', pk=local.pk)
    else:
        form = LocalForm()
    
    return render(request, 'locations/local_form.html', {
        'form': form,
        'title': 'Criar Local'
    })


@login_required
def local_edit(request, pk):
    """Editar local"""
    local = get_object_or_404(Local, pk=pk)
    
    if request.method == 'POST':
        form = LocalForm(request.POST, instance=local)
        if form.is_valid():
            form.save()
            messages.success(request, f'Local "{local.nome}" atualizado com sucesso!')
            return redirect('locations:local_detail', pk=local.pk)
    else:
        form = LocalForm(instance=local)
    
    return render(request, 'locations/local_form.html', {
        'form': form,
        'local': local,
        'title': 'Editar Local'
    })


@login_required
def local_delete(request, pk):
    """Excluir local"""
    local = get_object_or_404(Local, pk=pk)
    
    if request.method == 'POST':
        nome = local.nome
        local.delete()
        messages.success(request, f'Local "{nome}" excluído com sucesso!')
        return redirect('locations:local_list')
    
    return render(request, 'locations/local_confirm_delete.html', {'local': local})


# Views para Equipamentos
@login_required
def equipamento_list(request):
    """Lista de equipamentos"""
    equipamentos = Equipamento.objects.select_related('local')
    
    # Filtros
    form = EquipamentoFilterForm(request.GET)
    if form.is_valid():
        local = form.cleaned_data.get('local')
        tipo = form.cleaned_data.get('tipo')
        status_operacional = form.cleaned_data.get('status_operacional')
        search = form.cleaned_data.get('search')
        
        if local:
            equipamentos = equipamentos.filter(local=local)
        if tipo:
            equipamentos = equipamentos.filter(tipo=tipo)
        if status_operacional:
            equipamentos = equipamentos.filter(status_operacional=status_operacional)
        if search:
            equipamentos = equipamentos.filter(
                Q(nome__icontains=search) |
                Q(codigo__icontains=search) |
                Q(fabricante__icontains=search) |
                Q(modelo__icontains=search)
            )
    
    # Paginação
    paginator = Paginator(equipamentos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': form,
    }
    
    return render(request, 'locations/equipamento_list.html', context)


@login_required
def equipamento_detail(request, pk):
    """Detalhes do equipamento"""
    equipamento = get_object_or_404(Equipamento, pk=pk)
    
    context = {
        'equipamento': equipamento,
    }
    
    return render(request, 'locations/equipamento_detail.html', context)


@login_required
def equipamento_create(request):
    """Criar novo equipamento"""
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            equipamento = form.save()
            messages.success(request, f'Equipamento "{equipamento.nome}" criado com sucesso!')
            return redirect('locations:local_detail', pk=equipamento.local.pk)
    else:
        form = EquipamentoForm()
        # Se foi passado um local_id, pré-selecionar
        local_id = request.GET.get('local_id')
        if local_id:
            try:
                local = Local.objects.get(pk=local_id)
                form.initial['local'] = local
            except Local.DoesNotExist:
                pass
    
    return render(request, 'locations/equipamento_form.html', {
        'form': form,
        'title': 'Criar Equipamento'
    })


@login_required
def equipamento_edit(request, pk):
    """Editar equipamento"""
    equipamento = get_object_or_404(Equipamento, pk=pk)
    
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Equipamento "{equipamento.nome}" atualizado com sucesso!')
            return redirect('locations:equipamento_detail', pk=equipamento.pk)
    else:
        form = EquipamentoForm(instance=equipamento)
    
    return render(request, 'locations/equipamento_form.html', {
        'form': form,
        'equipamento': equipamento,
        'title': 'Editar Equipamento'
    })


@login_required
def equipamento_delete(request, pk):
    """Excluir equipamento"""
    equipamento = get_object_or_404(Equipamento, pk=pk)
    
    if request.method == 'POST':
        nome = equipamento.nome
        local = equipamento.local
        equipamento.delete()
        messages.success(request, f'Equipamento "{nome}" excluído com sucesso!')
        return redirect('locations:local_detail', pk=local.pk)
    
    return render(request, 'locations/equipamento_confirm_delete.html', {'equipamento': equipamento})


# Views de Dashboard/Estatísticas
@login_required
def dashboard(request):
    """Dashboard de locais e equipamentos"""
    # Estatísticas gerais
    stats = {
        'total_locais': Local.objects.count(),
        'locais_ativos': Local.objects.filter(status='ativo').count(),
        'total_equipamentos': Equipamento.objects.count(),
        'equipamentos_ativos': Equipamento.objects.filter(status_operacional='operando').count(),
        'equipamentos_manutencao': Equipamento.objects.filter(status_operacional='manutencao').count(),
    }
    
    # Locais com mais equipamentos
    top_locais = Local.objects.annotate(
        equipamentos_count=Count('equipamentos')
    ).filter(equipamentos_count__gt=0).order_by('-equipamentos_count')[:5]
    
    # Equipamentos por tipo
    equipamentos_por_tipo = Equipamento.objects.values('tipo').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Locais recentes
    locais_recentes = Local.objects.order_by('-data_criacao')[:5]
    
    # Equipamentos recentes
    equipamentos_recentes = Equipamento.objects.select_related('local').order_by('-data_criacao')[:5]
    
    context = {
        'stats': stats,
        'top_locais': top_locais,
        'equipamentos_por_tipo': equipamentos_por_tipo,
        'locais_recentes': locais_recentes,
        'equipamentos_recentes': equipamentos_recentes,
    }
    
    return render(request, 'locations/dashboard.html', context)


# API Views para AJAX
@login_required
def api_equipamentos_por_local(request, local_id):
    """API para buscar equipamentos de um local específico"""
    try:
        local = Local.objects.get(pk=local_id)
        equipamentos = local.equipamentos.values('id', 'nome', 'codigo', 'tipo', 'status')
        return JsonResponse({
            'success': True,
            'equipamentos': list(equipamentos)
        })
    except Local.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Local não encontrado'
        })


@login_required
def api_stats_local(request, local_id):
    """API para estatísticas de um local específico"""
    try:
        local = Local.objects.get(pk=local_id)
        equipamentos = local.equipamentos.all()
        
        stats = {
            'total': equipamentos.count(),
            'ativos': equipamentos.filter(status='ativo').count(),
            'inativos': equipamentos.filter(status='inativo').count(),
            'manutencao': equipamentos.filter(status='manutencao').count(),
            'descartados': equipamentos.filter(status='descartado').count(),
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Local.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Local não encontrado'
        })
