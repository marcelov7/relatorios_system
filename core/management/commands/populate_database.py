from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reports.models import ReportCategory, Report, ReportData
from notifications_app.models import NotificationTemplate, Notification
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando população do banco de dados...'))
        
        # Criar superusuário
        self.create_superuser()
        
        # Criar usuários de exemplo
        self.create_sample_users()
        
        # Criar categorias de relatórios
        self.create_report_categories()
        
        # Criar relatórios de exemplo
        self.create_sample_reports()
        
        # Criar templates de notificação
        self.create_notification_templates()
        
        # Criar notificações de exemplo
        self.create_sample_notifications()
        
        self.stdout.write(self.style.SUCCESS('✅ Banco de dados populado com sucesso!'))

    def create_superuser(self):
        """Cria superusuário admin"""
        try:
            if not User.objects.filter(username='admin').exists():
                admin = User.objects.create_superuser(
                    username='admin',
                    email='admin@sistema.com',
                    password='admin123',
                    first_name='Administrador',
                    last_name='Sistema',
                    departamento='TI',
                    cargo='Administrador do Sistema',
                    is_manager=True
                )
                self.stdout.write(f'👤 Superusuário criado: admin / admin123')
            else:
                self.stdout.write('👤 Superusuário já existe')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar superusuário: {e}'))

    def create_sample_users(self):
        """Cria usuários de exemplo"""
        users_data = [
            {
                'username': 'joao.silva',
                'email': 'joao.silva@empresa.com',
                'first_name': 'João',
                'last_name': 'Silva',
                'departamento': 'Vendas',
                'cargo': 'Gerente de Vendas',
                'is_manager': True
            },
            {
                'username': 'maria.santos',
                'email': 'maria.santos@empresa.com',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'departamento': 'Marketing',
                'cargo': 'Analista de Marketing',
                'is_manager': False
            },
            {
                'username': 'carlos.oliveira',
                'email': 'carlos.oliveira@empresa.com',
                'first_name': 'Carlos',
                'last_name': 'Oliveira',
                'departamento': 'Financeiro',
                'cargo': 'Controller',
                'is_manager': True
            },
            {
                'username': 'ana.costa',
                'email': 'ana.costa@empresa.com',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'departamento': 'RH',
                'cargo': 'Especialista em RH',
                'is_manager': False
            }
        ]
        
        for user_data in users_data:
            try:
                if not User.objects.filter(username=user_data['username']).exists():
                    user = User.objects.create_user(
                        password='123456',
                        **user_data
                    )
                    self.stdout.write(f'👤 Usuário criado: {user.username} / 123456')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao criar usuário {user_data["username"]}: {e}'))

    def create_report_categories(self):
        """Cria categorias de relatórios"""
        categories_data = [
            {'name': 'Vendas', 'description': 'Relatórios de vendas e performance comercial', 'color': '#28a745'},
            {'name': 'Financeiro', 'description': 'Relatórios financeiros e contábeis', 'color': '#17a2b8'},
            {'name': 'Marketing', 'description': 'Relatórios de campanhas e marketing digital', 'color': '#ffc107'},
            {'name': 'Operacional', 'description': 'Relatórios operacionais e de produção', 'color': '#6f42c1'},
            {'name': 'RH', 'description': 'Relatórios de recursos humanos', 'color': '#e83e8c'},
            {'name': 'TI', 'description': 'Relatórios de tecnologia e sistemas', 'color': '#fd7e14'},
        ]
        
        for cat_data in categories_data:
            category, created = ReportCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'📂 Categoria criada: {category.name}')

    def create_sample_reports(self):
        """Cria relatórios de exemplo"""
        users = list(User.objects.all())
        categories = list(ReportCategory.objects.all())
        
        reports_data = [
            {
                'title': 'Relatório de Vendas - Janeiro 2025',
                'description': 'Análise completa das vendas do primeiro mês do ano',
                'content': 'Este relatório apresenta uma análise detalhada das vendas realizadas em janeiro de 2025. Os resultados mostram um crescimento de 15% em relação ao mesmo período do ano anterior.',
                'status': 'approved',
                'priority': 'high'
            },
            {
                'title': 'Análise de Performance de Marketing',
                'description': 'Avaliação das campanhas digitais do último trimestre',
                'content': 'Relatório detalhado sobre o desempenho das campanhas de marketing digital, incluindo métricas de conversão, ROI e engagement.',
                'status': 'pending',
                'priority': 'medium'
            },
            {
                'title': 'Balanço Financeiro - Q4 2024',
                'description': 'Balanço financeiro do quarto trimestre',
                'content': 'Demonstrativo financeiro completo do último trimestre de 2024, incluindo receitas, despesas e projeções.',
                'status': 'approved',
                'priority': 'urgent'
            },
            {
                'title': 'Relatório de Produtividade da Equipe',
                'description': 'Análise de produtividade e performance dos colaboradores',
                'content': 'Relatório detalhado sobre a produtividade das equipes, identificando pontos fortes e oportunidades de melhoria.',
                'status': 'draft',
                'priority': 'low'
            }
        ]
        
        for i, report_data in enumerate(reports_data):
            if not Report.objects.filter(title=report_data['title']).exists():
                report = Report.objects.create(
                    created_by=random.choice(users),
                    category=random.choice(categories),
                    **report_data
                )
                
                # Adicionar dados estruturados ao relatório
                self.add_report_data(report)
                
                self.stdout.write(f'📊 Relatório criado: {report.title}')

    def add_report_data(self, report):
        """Adiciona dados estruturados aos relatórios"""
        sample_data = [
            {'field_name': 'receita_total', 'field_value': '125000.50', 'field_type': 'number'},
            {'field_name': 'periodo', 'field_value': '2025-01-01', 'field_type': 'date'},
            {'field_name': 'aprovado', 'field_value': 'true', 'field_type': 'boolean'},
            {'field_name': 'observacoes', 'field_value': 'Excelente performance do período', 'field_type': 'text'},
        ]
        
        for data in sample_data:
            ReportData.objects.create(report=report, **data)

    def create_notification_templates(self):
        """Cria templates de notificação"""
        templates_data = [
            {
                'name': 'Relatório Aprovado',
                'subject': 'Seu relatório foi aprovado',
                'message': 'Parabéns! Seu relatório "{title}" foi aprovado e está disponível no sistema.',
                'template_type': 'email'
            },
            {
                'name': 'Novo Relatório',
                'subject': 'Novo relatório disponível',
                'message': 'Um novo relatório foi criado: "{title}". Acesse o sistema para visualizar.',
                'template_type': 'system'
            },
            {
                'name': 'Relatório Rejeitado',
                'subject': 'Relatório necessita revisão',
                'message': 'Seu relatório "{title}" foi rejeitado. Verifique os comentários e faça as correções necessárias.',
                'template_type': 'email'
            }
        ]
        
        for template_data in templates_data:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'📧 Template criado: {template.name}')

    def create_sample_notifications(self):
        """Cria notificações de exemplo"""
        users = list(User.objects.all())
        templates = list(NotificationTemplate.objects.all())
        
        notifications_data = [
            {
                'title': 'Bem-vindo ao Sistema',
                'message': 'Seja bem-vindo ao Sistema de Relatórios! Explore todas as funcionalidades disponíveis.',
                'notification_type': 'info'
            },
            {
                'title': 'Relatório Aprovado',
                'message': 'Seu relatório de vendas foi aprovado pela gerência.',
                'notification_type': 'success'
            },
            {
                'title': 'Ação Necessária',
                'message': 'Você tem 3 relatórios pendentes de revisão.',
                'notification_type': 'warning'
            }
        ]
        
        for notif_data in notifications_data:
            for user in users[:2]:  # Criar apenas para os primeiros 2 usuários
                Notification.objects.create(
                    recipient=user,
                    sender=User.objects.filter(username='admin').first(),
                    template=random.choice(templates) if templates else None,
                    **notif_data
                )
        
        self.stdout.write(f'🔔 Notificações criadas para usuários') 