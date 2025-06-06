#!/usr/bin/env python3
"""
Script para FORÇAR RESET DE SENHAS no deploy
Este script executa automaticamente e corrige senhas inválidas
"""

import os
import sys
import django

# Configurar Django para produção
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'relatorio_system.settings')
os.environ['ENVIRONMENT'] = 'production'

django.setup()

from django.contrib.auth import get_user_model

def main():
    print("🔑 AUTO-CORREÇÃO DE SENHAS INICIADA...")
    
    User = get_user_model()
    
    # Verificar se há usuários
    total_users = User.objects.count()
    print(f"👥 Total de usuários encontrados: {total_users}")
    
    if total_users == 0:
        print("❌ Nenhum usuário encontrado. Criando admin...")
        create_admin_user(User)
        return
    
    # Listar usuários atuais
    print("📋 Usuários existentes:")
    for user in User.objects.all():
        tipo = "SUPERUSER" if user.is_superuser else "STAFF" if user.is_staff else "USER"
        print(f"   - {user.username} ({tipo})")
    
    # Corrigir senhas
    fix_passwords(User)
    
    print("✅ AUTO-CORREÇÃO CONCLUÍDA!")

def create_admin_user(User):
    """Cria usuário admin se não existir"""
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
        print("✅ ADMIN CRIADO: admin / admin123")
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")

def fix_passwords(User):
    """Corrige senhas dos usuários existentes"""
    
    # Corrigir admin
    try:
        admin = User.objects.get(username='admin')
        admin.set_password('admin123')
        admin.is_superuser = True
        admin.is_staff = True
        admin.is_active = True
        admin.save()
        print("✅ ADMIN: senha corrigida (admin123)")
    except User.DoesNotExist:
        print("⚠️ Admin não encontrado, criando...")
        create_admin_user(User)
    except Exception as e:
        print(f"❌ Erro no admin: {e}")
    
    # Corrigir teste
    try:
        teste = User.objects.get(username='teste')
        teste.set_password('teste123')
        teste.is_active = True
        teste.save()
        print("✅ TESTE: senha corrigida (teste123)")
    except User.DoesNotExist:
        print("ℹ️ Usuário teste não encontrado")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    # Corrigir marcelo
    try:
        marcelo = User.objects.get(username='marcelo')
        marcelo.set_password('marcelo123')
        marcelo.is_active = True
        marcelo.save()
        print("✅ MARCELO: senha corrigida (marcelo123)")
    except User.DoesNotExist:
        print("ℹ️ Usuário marcelo não encontrado")
    except Exception as e:
        print(f"❌ Erro no marcelo: {e}")

if __name__ == "__main__":
    main() 