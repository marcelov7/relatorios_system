from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reports.models import ReportCategory, Report
from notifications_app.models import NotificationTemplate, Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica se o banco de dados está populado com dados iniciais'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando dados no banco...'))
        
        # Verificar usuários
        total_users = User.objects.count()
        admin_exists = User.objects.filter(username='admin').exists()
        
        self.stdout.write(f'👥 Usuários: {total_users}')
        if admin_exists:
            self.stdout.write(self.style.SUCCESS('✅ Superusuário admin encontrado'))
        else:
            self.stdout.write(self.style.ERROR('❌ Superusuário admin NÃO encontrado'))
        
        # Verificar categorias
        total_categories = ReportCategory.objects.count()
        self.stdout.write(f'📂 Categorias: {total_categories}')
        
        if total_categories > 0:
            categories = ReportCategory.objects.all()
            for cat in categories:
                self.stdout.write(f'   - {cat.name}')
        
        # Verificar relatórios
        total_reports = Report.objects.count()
        self.stdout.write(f'📊 Relatórios: {total_reports}')
        
        # Verificar templates de notificação
        total_templates = NotificationTemplate.objects.count()
        self.stdout.write(f'📧 Templates de Notificação: {total_templates}')
        
        # Verificar notificações
        total_notifications = Notification.objects.count()
        self.stdout.write(f'🔔 Notificações: {total_notifications}')
        
        # Resumo
        self.stdout.write('\n' + '='*50)
        if total_users > 1 and admin_exists and total_categories > 0:
            self.stdout.write(self.style.SUCCESS('✅ Banco populado com sucesso!'))
            self.stdout.write('\n🔑 Credenciais para teste:')
            self.stdout.write('   Admin: admin / admin123')
            self.stdout.write('   Gerente: joao.silva / 123456')
            self.stdout.write('   Analista: maria.santos / 123456')
        else:
            self.stdout.write(self.style.ERROR('❌ Banco NÃO está populado'))
            self.stdout.write('💡 Execute: python manage.py populate_database')
        
        # Listar usuários existentes
        if total_users > 0:
            self.stdout.write('\n👥 Usuários no banco:')
            users = User.objects.all()
            for user in users:
                role = "Superusuário" if user.is_superuser else "Gerente" if user.is_manager else "Usuário"
                self.stdout.write(f'   - {user.username} ({user.get_full_name()}) - {role}') 