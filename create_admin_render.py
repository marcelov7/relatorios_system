#!/usr/bin/env python3
"""
Script para executar no CONSOLE DO RENDER
Cria superusuário e usuários de teste diretamente
"""

# Este script deve ser executado no console/shell do Render
# Não execute localmente - só no servidor do Render

from django.contrib.auth import get_user_model

User = get_user_model()

print("🚀 Criando usuários no banco PostgreSQL...")

# 1. Deletar usuários existentes (se houver)
User.objects.filter(username__in=['admin', 'teste']).delete()
print("🗑️ Usuários antigos removidos")

# 2. Criar superusuário admin
try:
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@sistema.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema',
        departamento='TI',
        cargo='Administrador',
        is_manager=True
    )
    print("✅ Superusuário admin criado: admin / admin123")
except Exception as e:
    print(f"❌ Erro ao criar admin: {e}")

# 3. Criar usuário de teste
try:
    teste = User.objects.create_user(
        username='teste',
        email='teste@sistema.com',
        password='teste123',
        first_name='Usuário',
        last_name='Teste',
        departamento='Geral',
        cargo='Teste',
        is_manager=False
    )
    print("✅ Usuário teste criado: teste / teste123")
except Exception as e:
    print(f"❌ Erro ao criar teste: {e}")

# 4. Verificar criação
total_users = User.objects.count()
admin_exists = User.objects.filter(username='admin', is_superuser=True).exists()

print(f"\n📊 RESULTADO:")
print(f"Total de usuários: {total_users}")
print(f"Admin existe: {'✅' if admin_exists else '❌'}")

print(f"\n🔑 CREDENCIAIS:")
print(f"Admin: admin / admin123")
print(f"Teste: teste / teste123")

print(f"\n🎉 CONCLUÍDO! Teste o acesso ao sistema.")

# 5. Listar todos os usuários
print(f"\n👥 USUÁRIOS NO BANCO:")
for user in User.objects.all():
    tipo = "SUPERUSER" if user.is_superuser else "STAFF" if user.is_staff else "USER"
    print(f"- {user.username} ({user.email}) - {tipo}") 