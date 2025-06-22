from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa informações de foto de perfil dos usuários'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Verificando fotos de perfil dos usuários...'))
        
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.ERROR('❌ Nenhum usuário encontrado'))
            return
        
        self.stdout.write(f'📊 Total de usuários: {users.count()}')
        self.stdout.write('─' * 50)
        
        for user in users:
            self.stdout.write(f'\n👤 {user.username}')
            self.stdout.write(f'   • Nome: {user.get_full_name() or "Não informado"}')
            self.stdout.write(f'   • Email: {user.email}')
            self.stdout.write(f'   • Perfil: {user.get_perfil_display()}')
            self.stdout.write(f'   • Unidade: {user.get_unidade_display()}')
            self.stdout.write(f'   • Setor: {user.get_setor_display()}')
            
            if user.foto_perfil:
                self.stdout.write(f'   📸 Foto: {user.foto_perfil.name}')
                self.stdout.write(f'   🔗 URL: {user.foto_perfil.url}')
                try:
                    # Verificar se arquivo existe fisicamente
                    import os
                    if os.path.exists(user.foto_perfil.path):
                        size = os.path.getsize(user.foto_perfil.path)
                        self.stdout.write(f'   📏 Tamanho: {size} bytes')
                    else:
                        self.stdout.write(self.style.WARNING('   ⚠️ Arquivo não encontrado no disco'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'   ⚠️ Erro ao verificar arquivo: {e}'))
            else:
                self.stdout.write('   📸 Foto: Não possui')
        
        # Estatísticas
        with_photo = users.exclude(foto_perfil='').count()
        without_photo = users.filter(foto_perfil='').count()
        
        self.stdout.write('\n' + '─' * 50)
        self.stdout.write(f'📈 Estatísticas:')
        self.stdout.write(f'   • Com foto: {with_photo}')
        self.stdout.write(f'   • Sem foto: {without_photo}')
        self.stdout.write(f'   • Percentual com foto: {(with_photo/users.count()*100):.1f}%')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Verificação concluída!')) 