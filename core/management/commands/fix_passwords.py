from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Corrige as senhas dos usuários existentes no banco'

    def handle(self, *args, **options):
        self.stdout.write('🔑 Corrigindo senhas dos usuários...')
        
        # Listar usuários atuais
        total_users = User.objects.count()
        self.stdout.write(f'👥 Total de usuários no banco: {total_users}')
        
        for user in User.objects.all():
            tipo = "SUPERUSER" if user.is_superuser else "STAFF" if user.is_staff else "USER"
            self.stdout.write(f'   - {user.username} ({tipo})')
        
        # Corrigir senha do admin
        try:
            admin = User.objects.get(username='admin')
            admin.set_password('admin123')
            admin.is_superuser = True
            admin.is_staff = True
            admin.is_active = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('✅ Admin: senha corrigida'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠️ Usuário admin não encontrado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no admin: {e}'))
        
        # Corrigir senha do teste
        try:
            teste = User.objects.get(username='teste')
            teste.set_password('teste123')
            teste.is_active = True
            teste.save()
            self.stdout.write(self.style.SUCCESS('✅ Teste: senha corrigida'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠️ Usuário teste não encontrado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no teste: {e}'))
        
        # Corrigir senha do marcelo (se existir)
        try:
            marcelo = User.objects.get(username='marcelo')
            marcelo.set_password('marcelo123')
            marcelo.is_active = True
            marcelo.save()
            self.stdout.write(self.style.SUCCESS('✅ Marcelo: senha corrigida'))
        except User.DoesNotExist:
            self.stdout.write('ℹ️ Usuário marcelo não encontrado')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro no marcelo: {e}'))
        
        self.stdout.write('\n🔑 CREDENCIAIS CORRIGIDAS:')
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Teste: teste / teste123')
        self.stdout.write('   Marcelo: marcelo / marcelo123 (se existir)')
        
        self.stdout.write('\n🎯 PRÓXIMO PASSO:')
        self.stdout.write('   Acesse /admin e faça login com admin / admin123')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Senhas corrigidas com sucesso!')) 