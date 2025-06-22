from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import io
from PIL import Image, ImageDraw

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa a funcionalidade de foto de perfil criando uma imagem de teste'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testando funcionalidade de foto de perfil...'))
        
        try:
            # Buscar um usuário para teste (admin ou primeiro usuário)
            try:
                user = User.objects.get(username='admin')
                self.stdout.write(f'✅ Usuário encontrado: {user.username}')
            except User.DoesNotExist:
                user = User.objects.first()
                if not user:
                    self.stdout.write(self.style.ERROR('❌ Nenhum usuário encontrado'))
                    return
                self.stdout.write(f'✅ Usando primeiro usuário: {user.username}')
            
            # Criar uma imagem de teste simples
            img = Image.new('RGB', (200, 200), color='#667eea')
            draw = ImageDraw.Draw(img)
            
            # Desenhar um círculo simples
            draw.ellipse([50, 50, 150, 150], fill='white')
            draw.text((85, 90), user.username[:2].upper(), fill='#667eea')
            
            # Salvar em memória
            img_io = io.BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)
            
            # Criar arquivo Django
            img_file = ContentFile(img_io.getvalue(), name=f'{user.username}_profile.png')
            
            # Verificar se já tem foto
            if user.foto_perfil:
                self.stdout.write(f'ℹ️ Usuário já possui foto: {user.foto_perfil.name}')
                self.stdout.write('🔄 Substituindo foto existente...')
                # Deletar foto antiga
                user.foto_perfil.delete(save=False)
            
            # Salvar nova foto
            user.foto_perfil.save(f'{user.username}_profile.png', img_file, save=True)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Foto de perfil criada com sucesso!'))
            self.stdout.write(f'   📁 Arquivo: {user.foto_perfil.name}')
            self.stdout.write(f'   🔗 URL: {user.foto_perfil.url}')
            
            # Informações do usuário
            self.stdout.write(f'\n👤 Informações do usuário:')
            self.stdout.write(f'   • Username: {user.username}')
            self.stdout.write(f'   • Nome: {user.get_full_name() or "Não informado"}')
            self.stdout.write(f'   • Email: {user.email}')
            self.stdout.write(f'   • Perfil: {user.get_perfil_display()}')
            self.stdout.write(f'   • Unidade: {user.get_unidade_display()}')
            self.stdout.write(f'   • Setor: {user.get_setor_display()}')
            
            self.stdout.write(self.style.SUCCESS('\n🎉 Teste concluído! Acesse o perfil do usuário para ver a foto.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro durante o teste: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())