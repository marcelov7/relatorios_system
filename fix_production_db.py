#!/usr/bin/env python3
"""
Script SIMPLES para corrigir o banco de produção PostgreSQL
Execute este script para criar as tabelas e usuários no banco hospedado
"""

import os
import sys

def main():
    print("🔧 Correção Rápida do Banco de Produção")
    print("=" * 50)
    
    # Configurar variáveis de ambiente para produção
    print("📝 Configurando conexão com PostgreSQL...")
    
    os.environ['DJANGO_SETTINGS_MODULE'] = 'relatorio_system.settings'
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['DEBUG'] = 'False'
    os.environ['DB_NAME'] = 'dbrelatorio_rqkg'
    os.environ['DB_USER'] = 'dbrelatorio_rqkg_user'
    os.environ['DB_PASSWORD'] = 'CJZUYC4FeqPg3FfSZDVu75oSaXhpzPwV'
    os.environ['DB_HOST'] = 'dpg-d10oti95pdvs73acede0-a.oregon-postgres.render.com'
    os.environ['DB_PORT'] = '5432'
    os.environ['SECRET_KEY'] = 'temp-migration-key-12345'
    os.environ['ALLOWED_HOSTS'] = '.onrender.com,localhost'
    
    # Inicializar Django
    import django
    django.setup()
    
    from django.core.management import call_command
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        print("\n🔄 Executando migrações...")
        call_command('makemigrations', verbosity=2)
        call_command('migrate', verbosity=2)
        print("✅ Migrações concluídas!")
        
        print("\n👤 Criando superusuário admin...")
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@sistema.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            try:
                admin.departamento = 'TI'
                admin.cargo = 'Administrador'
                admin.is_manager = True
                admin.save()
            except:
                pass
            print("✅ Admin criado: admin / admin123")
        else:
            print("ℹ️ Admin já existe")
        
        print("\n📊 Configurando dados iniciais...")
        call_command('setup_initial_data')
        
        print("\n👥 Criando usuário de teste...")
        if not User.objects.filter(username='teste').exists():
            User.objects.create_user(
                username='teste',
                email='teste@sistema.com',
                password='teste123',
                first_name='Usuário',
                last_name='Teste',
                departamento='Geral',
                cargo='Teste'
            )
            print("✅ Usuário teste criado: teste / teste123")
        else:
            print("ℹ️ Usuário teste já existe")
        
        print("\n🎉 SUCESSO! Banco de produção configurado!")
        print("=" * 50)
        print("🔑 Credenciais:")
        print("   Admin: admin / admin123")
        print("   Teste: teste / teste123")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 Soluções:")
        print("1. Verifique se o PostgreSQL está acessível")
        print("2. Confirme as credenciais do banco")
        print("3. Tente executar via Render Console")

if __name__ == "__main__":
    # Verificar se as dependências estão instaladas
    try:
        import psycopg2
    except ImportError:
        print("❌ ERRO: psycopg2-binary não está instalado")
        print("Execute: pip install psycopg2-binary")
        sys.exit(1)
    
    main() 