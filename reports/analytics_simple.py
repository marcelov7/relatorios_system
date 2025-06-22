"""
Sistema de Analytics Simplificado para evitar referências circulares
"""

from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Report
from locations.models import Local, Equipamento
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleReportAnalytics:
    """Classe simplificada para análise de relatórios sem referências circulares"""
    
    def __init__(self, user=None, date_range=None):
        self.user = user
        self.date_range = date_range or self._get_default_date_range()
        
    def _get_default_date_range(self):
        """Retorna range padrão dos últimos 30 dias"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        return (start_date, end_date)
    
    def _serialize_value(self, value):
        """Serializa valores de forma segura"""
        if isinstance(value, Decimal):
            return float(value)
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, timedelta):
            return value.total_seconds()
        return value
    
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
            stats['progresso_medio'] = round(float(avg_progress), 1)
            
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
        result = []
        for item in distribution:
            clean_item = {
                'prioridade': item['prioridade'],
                'count': item['count'],
                'resolvidos': item['resolvidos'],
                'progresso_medio': round(float(item['progresso_medio'] or 0), 1),
                'percentual': 0,
                'taxa_resolucao': 0
            }
            
            if total > 0:
                clean_item['percentual'] = round((item['count'] / total) * 100, 1)
                clean_item['taxa_resolucao'] = round(
                    (item['resolvidos'] / item['count']) * 100, 1
                ) if item['count'] > 0 else 0
            
            result.append(clean_item)
        
        return result
    
    def get_timeline_data(self, group_by='day'):
        """Dados da timeline de relatórios"""
        queryset = Report.objects.filter(data_criacao__range=self.date_range)
        
        if self.user and not self.user.is_staff:
            queryset = queryset.filter(
                Q(usuario=self.user) | Q(atribuido_para=self.user)
            )
        
        timeline = queryset.annotate(
            periodo=TruncDate('data_criacao')
        ).values('periodo').annotate(
            criados=Count('id'),
            resolvidos=Count('id', filter=Q(status='resolvido')),
            em_andamento=Count('id', filter=Q(status='em_andamento')),
            pendentes=Count('id', filter=Q(status='pendente'))
        ).order_by('periodo')
        
        # Converter para formato serializable
        result = []
        for item in timeline:
            clean_item = {
                'periodo': item['periodo'].isoformat(),
                'criados': item['criados'],
                'resolvidos': item['resolvidos'],
                'em_andamento': item['em_andamento'],
                'pendentes': item['pendentes']
            }
            result.append(clean_item)
        
        return result
    
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
            progresso_medio=Avg('progresso')
        ).order_by('-total_reports')
        
        # Calcular métricas adicionais
        result = []
        for item in performance:
            clean_item = {
                'local__nome': item['local__nome'],
                'local__id': item['local__id'],
                'total_reports': item['total_reports'],
                'resolvidos': item['resolvidos'],
                'em_andamento': item['em_andamento'],
                'pendentes': item['pendentes'],
                'progresso_medio': round(float(item['progresso_medio'] or 0), 1),
                'taxa_resolucao': 0,
                'tempo_medio_dias': 0
            }
            
            if item['total_reports'] > 0:
                clean_item['taxa_resolucao'] = round(
                    (item['resolvidos'] / item['total_reports']) * 100, 1
                )
            
            result.append(clean_item)
        
        return result
    
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
        result = []
        for item in equipment_stats:
            clean_item = {
                'equipamento__nome': item['equipamento__nome'],
                'equipamento__codigo': item['equipamento__codigo'],
                'equipamento__tipo': item['equipamento__tipo'],
                'equipamento__local__nome': item['equipamento__local__nome'],
                'total_issues': item['total_issues'],
                'issues_resolvidas': item['issues_resolvidas'],
                'issues_pendentes': item['issues_pendentes'],
                'progresso_medio': round(float(item['progresso_medio'] or 0), 1),
                'taxa_resolucao': 0
            }
            
            if item['total_issues'] > 0:
                clean_item['taxa_resolucao'] = round(
                    (item['issues_resolvidas'] / item['total_issues']) * 100, 1
                )
            
            result.append(clean_item)
        
        return result


class SimpleDashboardData:
    """Classe simplificada para preparar dados do dashboard"""
    
    def __init__(self, user=None, period='30d'):
        self.user = user
        self.period = period
        self.analytics = SimpleReportAnalytics(user, self._get_date_range(period))
    
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
        """Retorna todos os dados para o dashboard de forma serializable"""
        return {
            'overview': self.analytics.get_overview_stats(),
            'priority_distribution': self.analytics.get_priority_distribution(),
            'location_performance': self.analytics.get_location_performance(),
            'timeline': self.analytics.get_timeline_data(),
            'equipment_issues': self.analytics.get_equipment_issues(),
            'period': self.period,
            'date_range': [
                self.analytics.date_range[0].isoformat(),
                self.analytics.date_range[1].isoformat()
            ],
            'trends': {  # Dados básicos de tendências
                'total_reports': {'variacao': 0, 'tendencia': 'stable'},
                'resolvidos': {'variacao': 0, 'tendencia': 'stable'}
            }
        }