"""
Sistema de Analytics Inteligente para Relatórios
Fornece métricas avançadas e insights sobre performance dos relatórios
"""

from django.db.models import Count, Avg, Q, F, Sum, Max, Min
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import json

from .models import Report, ReportUpdate
from locations.models import Local, Equipamento
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportAnalytics:
    """Classe principal para análise de relatórios"""
    
    def __init__(self, user=None, date_range=None):
        self.user = user
        self.date_range = date_range or self._get_default_date_range()
        
    def _get_default_date_range(self):
        """Retorna range padrão dos últimos 30 dias"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        return (start_date, end_date)
    
    def get_overview_stats(self):
        """Estatísticas gerais do sistema"""
        queryset = Report.objects.filter(
            data_criacao__range=self.date_range
        )
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        total_reports = queryset.count()
        
        stats = {
            'total_reports': total_reports,
            'reports_pendentes': queryset.filter(status='pendente').count(),
            'reports_em_andamento': queryset.filter(status='em_andamento').count(),
            'reports_resolvidos': queryset.filter(status='resolvido').count(),
            'taxa_resolucao': 0,
            'tempo_medio_resolucao': 0,
            'progresso_medio': 0,
        }
        
        if total_reports > 0:
            stats['taxa_resolucao'] = round(
                (stats['reports_resolvidos'] / total_reports) * 100, 1
            )
            
            # Progresso médio
            avg_progress = queryset.aggregate(avg=Avg('progresso'))['avg'] or 0
            stats['progresso_medio'] = round(avg_progress, 1)
            
            # Tempo médio de resolução (em dias)
            resolved_reports = queryset.filter(status='resolvido')
            if resolved_reports.exists():
                tempo_total = 0
                count = 0
                for report in resolved_reports:
                    diff = report.data_atualizacao - report.data_criacao
                    tempo_total += diff.total_seconds()
                    count += 1
                
                if count > 0:
                    tempo_medio_segundos = tempo_total / count
                    stats['tempo_medio_resolucao'] = round(
                        tempo_medio_segundos / (24 * 3600), 1  # Converter para dias
                    )
        
        return stats
    
    def get_priority_distribution(self):
        """Distribuição por prioridade"""
        queryset = Report.objects.filter(data_criacao__range=self.date_range)
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        distribution = queryset.values('prioridade').annotate(
            count=Count('id'),
            resolvidos=Count('id', filter=Q(status='resolvido')),
            progresso_medio=Avg('progresso')
        ).order_by('prioridade')
        
        # Calcular percentuais
        total = queryset.count()
        for item in distribution:
            if total > 0:
                item['percentual'] = round((item['count'] / total) * 100, 1)
                item['taxa_resolucao'] = round(
                    (item['resolvidos'] / item['count']) * 100, 1
                ) if item['count'] > 0 else 0
            else:
                item['percentual'] = 0
                item['taxa_resolucao'] = 0
            
            item['progresso_medio'] = round(item['progresso_medio'] or 0, 1)
        
        return list(distribution)
    
    def get_location_performance(self):
        """Performance por local"""
        queryset = Report.objects.filter(
            data_criacao__range=self.date_range,
            local__isnull=False
        )
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        performance = queryset.values(
            'local__nome', 'local__id'
        ).annotate(
            total_reports=Count('id'),
            resolvidos=Count('id', filter=Q(status='resolvido')),
            em_andamento=Count('id', filter=Q(status='em_andamento')),
            pendentes=Count('id', filter=Q(status='pendente')),
            progresso_medio=Avg('progresso'),
            tempo_medio_resolucao=Avg(
                F('data_atualizacao') - F('data_criacao'),
                filter=Q(status='resolvido')
            )
        ).order_by('-total_reports')
        
        # Calcular métricas adicionais
        for item in performance:
            if item['total_reports'] > 0:
                item['taxa_resolucao'] = round(
                    (item['resolvidos'] / item['total_reports']) * 100, 1
                )
            else:
                item['taxa_resolucao'] = 0
            
            item['progresso_medio'] = round(item['progresso_medio'] or 0, 1)
            
            # Converter tempo médio para dias
            if item['tempo_medio_resolucao']:
                dias = item['tempo_medio_resolucao'].total_seconds() / (24 * 3600)
                item['tempo_medio_dias'] = round(dias, 1)
            else:
                item['tempo_medio_dias'] = 0
        
        return list(performance)
    
    def get_user_performance(self):
        """Performance por usuário"""
        queryset = Report.objects.filter(data_criacao__range=self.date_range)
        
        # Performance dos autores
        author_performance = queryset.values(
            'usuario__username', 'usuario__first_name', 'usuario__last_name'
        ).annotate(
            reports_criados=Count('id'),
            resolvidos=Count('id', filter=Q(status='resolvido')),
            progresso_medio=Avg('progresso')
        ).order_by('-reports_criados')
        
        # Performance dos responsáveis
        assigned_performance = queryset.filter(
            atribuido_para__isnull=False
        ).values(
            'atribuido_para__username', 
            'atribuido_para__first_name', 
            'atribuido_para__last_name'
        ).annotate(
            reports_atribuidos=Count('id'),
            resolvidos=Count('id', filter=Q(status='resolvido')),
            progresso_medio=Avg('progresso')
        ).order_by('-reports_atribuidos')
        
        # Processar dados dos autores
        for item in author_performance:
            if item['reports_criados'] > 0:
                item['taxa_resolucao'] = round(
                    (item['resolvidos'] / item['reports_criados']) * 100, 1
                )
            else:
                item['taxa_resolucao'] = 0
            item['progresso_medio'] = round(item['progresso_medio'] or 0, 1)
            item['nome_completo'] = f"{item['usuario__first_name']} {item['usuario__last_name']}".strip() or item['usuario__username']
        
        # Processar dados dos responsáveis
        for item in assigned_performance:
            if item['reports_atribuidos'] > 0:
                item['taxa_resolucao'] = round(
                    (item['resolvidos'] / item['reports_atribuidos']) * 100, 1
                )
            else:
                item['taxa_resolucao'] = 0
            item['progresso_medio'] = round(item['progresso_medio'] or 0, 1)
            item['nome_completo'] = f"{item['atribuido_para__first_name']} {item['atribuido_para__last_name']}".strip() or item['atribuido_para__username']
        
        return {
            'autores': list(author_performance),
            'responsaveis': list(assigned_performance)
        }
    
    def get_timeline_data(self, group_by='day'):
        """Dados da timeline de relatórios"""
        queryset = Report.objects.filter(data_criacao__range=self.date_range)
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        # Escolher função de truncamento baseada no agrupamento
        trunc_functions = {
            'day': TruncDate,
            'week': TruncWeek,
            'month': TruncMonth,
            'year': TruncYear,
        }
        
        trunc_func = trunc_functions.get(group_by, TruncDate)
        
        timeline = queryset.annotate(
            periodo=trunc_func('data_criacao')
        ).values('periodo').annotate(
            criados=Count('id'),
            resolvidos=Count('id', filter=Q(status='resolvido')),
            em_andamento=Count('id', filter=Q(status='em_andamento')),
            pendentes=Count('id', filter=Q(status='pendente'))
        ).order_by('periodo')
        
        return list(timeline)
    
    def get_equipment_issues(self):
        """Equipamentos com mais problemas"""
        queryset = Report.objects.filter(
            data_criacao__range=self.date_range,
            equipamento__isnull=False
        )
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        equipment_stats = queryset.values(
            'equipamento__nome', 
            'equipamento__codigo',
            'equipamento__tipo',
            'equipamento__local__nome'
        ).annotate(
            total_issues=Count('id'),
            issues_resolvidas=Count('id', filter=Q(status='resolvido')),
            issues_pendentes=Count('id', filter=Q(status='pendente')),
            progresso_medio=Avg('progresso')
        ).order_by('-total_issues')
        
        # Calcular métricas adicionais
        for item in equipment_stats:
            if item['total_issues'] > 0:
                item['taxa_resolucao'] = round(
                    (item['issues_resolvidas'] / item['total_issues']) * 100, 1
                )
            else:
                item['taxa_resolucao'] = 0
            
            item['progresso_medio'] = round(item['progresso_medio'] or 0, 1)
        
        return list(equipment_stats)
    
    def get_response_time_analysis(self):
        """Análise de tempo de resposta"""
        updates = ReportUpdate.objects.filter(
            report__data_criacao__range=self.date_range
        ).select_related('report')
        
        if self.user and not self.user.is_staff:
            updates = updates.filter(
                Q(report__usuario=self.user) | Q(report__atribuido_para=self.user)
            )
        
        # Calcular tempo até primeira atualização
        first_updates = []
        for update in updates:
            if update.progresso_anterior == 0:  # Primeira atualização
                time_to_first = update.data_atualizacao - update.report.data_criacao
                first_updates.append({
                    'report_id': update.report.id,
                    'tempo_primeira_resposta': time_to_first.total_seconds() / 3600,  # Em horas
                    'prioridade': update.report.prioridade
                })
        
        # Agrupar por prioridade
        response_by_priority = defaultdict(list)
        for update in first_updates:
            response_by_priority[update['prioridade']].append(
                update['tempo_primeira_resposta']
            )
        
        # Calcular estatísticas por prioridade
        priority_stats = {}
        for priority, times in response_by_priority.items():
            if times:
                priority_stats[priority] = {
                    'tempo_medio': round(sum(times) / len(times), 1),
                    'tempo_min': round(min(times), 1),
                    'tempo_max': round(max(times), 1),
                    'total_reports': len(times)
                }
        
        return priority_stats
    
    def get_trends_analysis(self):
        """Análise de tendências"""
        # Comparar período atual com período anterior
        current_start, current_end = self.date_range
        period_length = current_end - current_start
        previous_start = current_start - period_length
        previous_end = current_start
        
        # Estatísticas do período atual
        current_stats = self._get_period_stats(current_start, current_end)
        
        # Estatísticas do período anterior
        previous_stats = self._get_period_stats(previous_start, previous_end)
        
        # Calcular variações percentuais
        trends = {}
        for key in current_stats:
            current_val = current_stats[key]
            previous_val = previous_stats.get(key, 0)
            
            if previous_val > 0:
                variation = ((current_val - previous_val) / previous_val) * 100
            else:
                variation = 100 if current_val > 0 else 0
            
            trends[key] = {
                'atual': current_val,
                'anterior': previous_val,
                'variacao': round(variation, 1),
                'tendencia': 'up' if variation > 0 else 'down' if variation < 0 else 'stable'
            }
        
        return trends
    
    def _get_period_stats(self, start_date, end_date):
        """Estatísticas para um período específico"""
        queryset = Report.objects.filter(
            data_criacao__range=(start_date, end_date)
        )
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        total = queryset.count()
        
        return {
            'total_reports': total,
            'resolvidos': queryset.filter(status='resolvido').count(),
            'em_andamento': queryset.filter(status='em_andamento').count(),
            'pendentes': queryset.filter(status='pendente').count(),
            'criticos': queryset.filter(prioridade='critica').count(),
            'alta_prioridade': queryset.filter(prioridade='alta').count(),
        }
    
    def get_productivity_metrics(self):
        """Métricas de produtividade"""
        queryset = Report.objects.filter(data_criacao__range=self.date_range)
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        # Relatórios por dia
        days_in_period = (self.date_range[1] - self.date_range[0]).days
        reports_per_day = queryset.count() / max(days_in_period, 1)
        
        # Taxa de conclusão
        total_reports = queryset.count()
        completed_reports = queryset.filter(status='resolvido').count()
        completion_rate = (completed_reports / total_reports * 100) if total_reports > 0 else 0
        
        # Tempo médio de resolução por prioridade
        resolution_times = {}
        for priority, _ in Report.PRIORIDADE_CHOICES:
            priority_reports = queryset.filter(
                prioridade=priority,
                status='resolvido'
            )
            
            if priority_reports.exists():
                total_time = 0
                count = 0
                for report in priority_reports:
                    time_diff = report.data_atualizacao - report.data_criacao
                    total_time += time_diff.total_seconds()
                    count += 1
                
                avg_time_hours = (total_time / count) / 3600 if count > 0 else 0
                resolution_times[priority] = round(avg_time_hours, 1)
            else:
                resolution_times[priority] = 0
        
        return {
            'reports_por_dia': round(reports_per_day, 1),
            'taxa_conclusao': round(completion_rate, 1),
            'tempo_resolucao_por_prioridade': resolution_times,
            'total_atualizacoes': ReportUpdate.objects.filter(
                report__in=queryset
            ).count()
        }


class DashboardData:
    """Classe para preparar dados do dashboard"""
    
    def __init__(self, user=None, period='30d'):
        self.user = user
        self.period = period
        self.analytics = ReportAnalytics(user, self._get_date_range(period))
    
    def _get_date_range(self, period):
        """Converte período em range de datas"""
        end_date = timezone.now()
        
        period_map = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '365d': 365,
        }
        
        days = period_map.get(period, 30)
        start_date = end_date - timedelta(days=days)
        
        return (start_date, end_date)
    
    def get_complete_dashboard_data(self):
        """Retorna todos os dados para o dashboard"""
        return {
            'overview': self.analytics.get_overview_stats(),
            'priority_distribution': self.analytics.get_priority_distribution(),
            'location_performance': self.analytics.get_location_performance(),
            'user_performance': self.analytics.get_user_performance(),
            'timeline': self.analytics.get_timeline_data(),
            'equipment_issues': self.analytics.get_equipment_issues(),
            'response_times': self.analytics.get_response_time_analysis(),
            'trends': self.analytics.get_trends_analysis(),
            'productivity': self.analytics.get_productivity_metrics(),
            'period': self.period,
            'date_range': self.analytics.date_range,
        } 