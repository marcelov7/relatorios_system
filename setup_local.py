#!/usr/bin/env python3
"""
Script para configuração rápida do ambiente local (XAMPP)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 Configuração do Ambiente Local - Sistema de Relatórios")
    print("=" * 60)
    
    # Verificar se está no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ Erro: Execute este script no diretório raiz do projeto Django")
        sys.exit(1)
    
    # 1. Verificar se o ambiente virtual está ativo
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Aviso: Recomenda-se ativar um ambiente virtual antes de continuar")
        resposta = input("Deseja continuar mesmo assim? (s/n): ")
        if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
            print("👋 Operação cancelada")
            sys.exit(0)
    
    # 2. Copiar arquivo de configuração local
    if not os.path.exists('.env'):
        if os.path.exists('env.local.example'):
            shutil.copy('env.local.example', '.env')
            print("✅ Arquivo .env criado a partir do env.local.example")
        else:
            print("❌ Erro: Arquivo env.local.example não encontrado")
            sys.exit(1)
    else:
        print("ℹ️  Arquivo .env já existe")
    
    # 3. Instalar dependências
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        print("💡 Tente instalar manualmente: pip install -r requirements.txt")
    
    # 4. Verificar configuração do banco
    print("\n🗄️  Configuração do Banco de Dados")
    print("Certifique-se de que:")
    print("- XAMPP está rodando")
    print("- MySQL está ativo")
    print("- Banco 'relatorio_system' foi criado no phpMyAdmin")
    
    input("\nPressione Enter quando estiver pronto para continuar...")
    
    # 5. Executar migrações
    print("\n🔄 Executando migrações...")
    try:
        subprocess.check_call([sys.executable, 'manage.py', 'makemigrations'])
        subprocess.check_call([sys.executable, 'manage.py', 'migrate'])
        print("✅ Migrações executadas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao executar migrações")
        print("💡 Verifique se o banco MySQL está rodando e acessível")
    
    # 6. Criar superusuário
    print("\n👤 Criação de Superusuário")
    resposta = input("Deseja criar um superusuário agora? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        try:
            subprocess.check_call([sys.executable, 'manage.py', 'createsuperuser'])
            print("✅ Superusuário criado com sucesso")
        except subprocess.CalledProcessError:
            print("❌ Erro ao criar superusuário")
    
    # 7. Instruções finais
    print("\n🎉 Configuração concluída!")
    print("=" * 60)
    print("Para iniciar o servidor de desenvolvimento:")
    print("python manage.py runserver")
    print("\nPara acessar o sistema:")
    print("http://localhost:8000")
    print("\nPara acessar o admin:")
    print("http://localhost:8000/admin")
    print("\n💡 Consulte o arquivo SETUP_AMBIENTES.md para mais informações")

if __name__ == "__main__":
    main() 