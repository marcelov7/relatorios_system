from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria superusuário admin de forma garantida'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Configurando administrador...')
        
        with transaction.atomic():
            try:
                # Primeiro, deletar admin se existir (para recriar)
                if User.objects.filter(username='admin').exists():
                    User.objects.filter(username='admin').delete()
                    self.stdout.write('🗑️ Admin existente removido')
                
                # Criar novo admin
                admin = User.objects.create_user(
                    username='admin',
                    email='admin@sistema.com',
                    password='admin123',
                    first_name='Administrador',
                    last_name='Sistema',
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                
                # Adicionar campos extras se existirem
                try:
                    admin.departamento = 'TI'
                    admin.cargo = 'Administrador'
                    admin.is_manager = True
                    admin.save()
                except:
                    pass  # Ignorar se campos não existem
                
                self.stdout.write(self.style.SUCCESS('✅ Superusuário criado com sucesso!'))
                self.stdout.write('🔑 Credenciais: admin / admin123')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro: {e}'))
                
                # Fallback: tentar criar de forma mais simples
                try:
                    User.objects.create_superuser('admin', 'admin@sistema.com', 'admin123')
                    self.stdout.write(self.style.SUCCESS('✅ Superusuário criado (fallback)!'))
                except Exception as e2:
                    self.stdout.write(self.style.ERROR(f'❌ Fallback também falhou: {e2}')) 