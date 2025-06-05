from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reports.models import ReportCategory
from notifications_app.models import NotificationTemplate

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura dados iniciais do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove dados existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Removendo dados existentes...')
            ReportCategory.objects.all().delete()
            NotificationTemplate.objects.all().delete()

        # Criar categorias de relatórios
        categories = [
            {
                'name': 'Vendas',
                'description': 'Relatórios de vendas e performance comercial',
                'color': '#007bff'
            },
            {
                'name': 'Financeiro',
                'description': 'Relatórios financeiros e contábeis',
                'color': '#28a745'
            },
            {
                'name': 'Marketing',
                'description': 'Relatórios de marketing e campanhas',
                'color': '#dc3545'
            },
            {
                'name': 'Operacional',
                'description': 'Relatórios operacionais e logística',
                'color': '#ffc107'
            },
            {
                'name': 'Recursos Humanos',
                'description': 'Relatórios de RH e pessoal',
                'color': '#6f42c1'
            },
            {
                'name': 'Geral',
                'description': 'Relatórios gerais e diversos',
                'color': '#6c757d'
            }
        ]

        for cat_data in categories:
            category, created = ReportCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Categoria criada: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Categoria já existe: {category.name}')
                )

        # Criar templates de notificação
        templates = [
            {
                'name': 'Relatório Criado',
                'notification_type': 'report_created',
                'title_template': 'Novo relatório: {report_title}',
                'message_template': 'O relatório "{report_title}" foi criado por {author_name}.'
            },
            {
                'name': 'Relatório Concluído',
                'notification_type': 'report_completed',
                'title_template': 'Relatório concluído: {report_title}',
                'message_template': 'O relatório "{report_title}" foi concluído com sucesso e está disponível para download.'
            },
            {
                'name': 'Relatório com Falha',
                'notification_type': 'report_failed',
                'title_template': 'Erro no relatório: {report_title}',
                'message_template': 'O relatório "{report_title}" falhou durante o processamento. Verifique os dados e tente novamente.'
            },
            {
                'name': 'Usuário Registrado',
                'notification_type': 'user_registered',
                'title_template': 'Bem-vindo ao Sistema de Relatórios!',
                'message_template': 'Olá {user_name}, sua conta foi criada com sucesso. Comece criando seu primeiro relatório!'
            },
            {
                'name': 'Lembrete de Prazo',
                'notification_type': 'deadline_reminder',
                'title_template': 'Lembrete: Relatório com prazo próximo',
                'message_template': 'O relatório "{report_title}" tem prazo até {deadline_date}. Não se esqueça de concluí-lo!'
            }
        ]

        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                defaults={
                    'name': template_data['name'],
                    'title_template': template_data['title_template'],
                    'message_template': template_data['message_template']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Template criado: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template já existe: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Dados iniciais configurados com sucesso!')
        ) 