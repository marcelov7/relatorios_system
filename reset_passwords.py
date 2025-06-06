#!/usr/bin/env python3
"""
Script para RESETAR SENHAS dos usuários existentes
Execute no CONSOLE DO RENDER (Shell)
"""

from django.contrib.auth import get_user_model

User = get_user_model()

print("🔑 RESETANDO SENHAS DOS USUÁRIOS EXISTENTES...")
print("=" * 50)

# Listar usuários atuais
print("👥 Usuários encontrados no banco:")
for user in User.objects.all():
    tipo = "SUPERUSER" if user.is_superuser else "STAFF" if user.is_staff else "USER"
    print(f"- {user.username} ({user.email}) - {tipo}")

print("\n🔄 Atualizando senhas...")

# 1. Resetar senha do admin
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.is_superuser = True
    admin.is_staff = True
    admin.is_active = True
    admin.save()
    print("✅ Admin: senha resetada para 'admin123'")
except User.DoesNotExist:
    print("❌ Usuário 'admin' não encontrado")
except Exception as e:
    print(f"❌ Erro ao resetar admin: {e}")

# 2. Resetar senha do teste
try:
    teste = User.objects.get(username='teste')
    teste.set_password('teste123')
    teste.is_active = True
    teste.save()
    print("✅ Teste: senha resetada para 'teste123'")
except User.DoesNotExist:
    print("❌ Usuário 'teste' não encontrado")
except Exception as e:
    print(f"❌ Erro ao resetar teste: {e}")

# 3. Resetar senha do marcelo (se existir)
try:
    marcelo = User.objects.get(username='marcelo')
    marcelo.set_password('marcelo123')
    marcelo.is_active = True
    marcelo.save()
    print("✅ Marcelo: senha resetada para 'marcelo123'")
except User.DoesNotExist:
    print("ℹ️ Usuário 'marcelo' não encontrado")
except Exception as e:
    print(f"❌ Erro ao resetar marcelo: {e}")

print("\n🔑 CREDENCIAIS ATUALIZADAS:")
print("Admin: admin / admin123")
print("Teste: teste / teste123") 
print("Marcelo: marcelo / marcelo123 (se existir)")

print("\n🎯 TESTE AGORA:")
print("1. Acesse sua URL do Render")
print("2. Vá para /admin")
print("3. Faça login com: admin / admin123")

# Verificar hash das senhas
print("\n🔍 VERIFICAÇÃO:")
for user in User.objects.all():
    print(f"- {user.username}: hash starts with {user.password[:20]}...")

print("\n✅ SENHAS RESETADAS COM SUCESSO!") 