from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria usuário de teste'

    def handle(self, *args, **options):
        self.stdout.write('👤 Criando usuário de teste...')
        
        try:
            # Criar usuário teste simples
            if not User.objects.filter(username='teste').exists():
                user = User.objects.create_user(
                    username='teste',
                    email='teste@sistema.com',
                    password='teste123',
                    first_name='Usuário',
                    last_name='Teste',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS('✅ Usuário teste criado: teste / teste123'))
            else:
                self.stdout.write('ℹ️ Usuário teste já existe')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar usuário teste: {e}')) 