#!/usr/bin/env python3
"""
Script para migrar e popular o banco PostgreSQL de produção
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django para ambiente de produção
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'relatorio_system.settings')

# Configurar variáveis de ambiente para produção
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEBUG'] = 'False'
os.environ['DB_NAME'] = 'dbrelatorio_rqkg'
os.environ['DB_USER'] = 'dbrelatorio_rqkg_user'
os.environ['DB_PASSWORD'] = 'CJZUYC4FeqPg3FfSZDVu75oSaXhpzPwV'
os.environ['DB_HOST'] = 'dpg-d10oti95pdvs73acede0-a.oregon-postgres.render.com'
os.environ['DB_PORT'] = '5432'
os.environ['SECRET_KEY'] = 'temp-key-for-migration'
os.environ['ALLOWED_HOSTS'] = '.onrender.com,localhost'

# Inicializar Django
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model
from django.db import connection
from django.conf import settings

User = get_user_model()

def test_connection():
    """Testa a conexão com o banco"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexão com o banco PostgreSQL estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return False

def run_migrations():
    """Executa as migrações"""
    try:
        print("\n🔄 Executando migrações...")
        
        # Primeiro, fazer migrações
        print("📝 Criando arquivos de migração...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("🚀 Aplicando migrações ao banco...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migrações executadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def create_superuser():
    """Cria o superusuário admin"""
    try:
        print("\n👤 Criando superusuário...")
        
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@sistema.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            
            # Adicionar campos extras se existirem
            try:
                admin.departamento = 'TI'
                admin.cargo = 'Administrador'
                admin.is_manager = True
                admin.save()
            except Exception:
                pass  # Ignorar se campos não existem
                
            print("✅ Superusuário criado: admin / admin123")
        else:
            print("ℹ️ Superusuário admin já existe")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def setup_initial_data():
    """Configura dados iniciais"""
    try:
        print("\n📊 Configurando dados iniciais...")
        execute_from_command_line(['manage.py', 'setup_initial_data'])
        print("✅ Dados iniciais configurados!")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar dados iniciais: {e}")
        return False

def create_test_users():
    """Cria usuários de teste"""
    try:
        print("\n👥 Criando usuários de teste...")
        
        test_users = [
            {
                'username': 'gerente',
                'email': 'gerente@sistema.com',
                'password': 'gerente123',
                'first_name': 'João',
                'last_name': 'Silva',
                'departamento': 'Vendas',
                'cargo': 'Gerente',
                'is_manager': True
            },
            {
                'username': 'analista',
                'email': 'analista@sistema.com',
                'password': 'analista123',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'departamento': 'Marketing',
                'cargo': 'Analista',
                'is_manager': False
            }
        ]
        
        for user_data in test_users:
            username = user_data.pop('username')
            password = user_data.pop('password')
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password, **user_data)
                print(f"✅ Usuário criado: {username} / {password}")
            else:
                print(f"ℹ️ Usuário {username} já existe")
                
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários de teste: {e}")
        return False

def collect_static():
    """Coleta arquivos estáticos"""
    try:
        print("\n📁 Coletando arquivos estáticos...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Arquivos estáticos coletados!")
        return True
    except Exception as e:
        print(f"❌ Erro ao coletar estáticos: {e}")
        return False

def main():
    print("🚀 Configuração do Banco de Produção - PostgreSQL")
    print("=" * 60)
    print(f"Banco: {os.environ['DB_NAME']}")
    print(f"Host: {os.environ['DB_HOST']}")
    print(f"User: {os.environ['DB_USER']}")
    print("=" * 60)
    
    # 1. Testar conexão
    if not test_connection():
        print("\n❌ Não foi possível conectar ao banco. Verifique as credenciais.")
        sys.exit(1)
    
    # 2. Executar migrações
    if not run_migrations():
        print("\n❌ Falha nas migrações. Processo interrompido.")
        sys.exit(1)
    
    # 3. Criar superusuário
    create_superuser()
    
    # 4. Configurar dados iniciais
    setup_initial_data()
    
    # 5. Criar usuários de teste
    create_test_users()
    
    # 6. Coletar arquivos estáticos
    collect_static()
    
    print("\n🎉 Configuração do banco de produção concluída com sucesso!")
    print("=" * 60)
    print("📋 Credenciais criadas:")
    print("   Admin: admin / admin123")
    print("   Gerente: gerente / gerente123")
    print("   Analista: analista / analista123")
    print("=" * 60)
    print("\n💡 Agora você pode acessar o sistema hospedado no Render")

if __name__ == "__main__":
    main() 