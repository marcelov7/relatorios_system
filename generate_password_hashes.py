#!/usr/bin/env python3
"""
Script para gerar hashes de senha do Django
Execute para obter os hashes corretos para inserir no banco PostgreSQL
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'relatorio_system.settings')

try:
    import django
    django.setup()
    
    from django.contrib.auth.hashers import make_password
    
    print("🔑 GERADOR DE HASHES DE SENHA DJANGO")
    print("=" * 50)
    
    # Gerar hash para admin123
    admin_hash = make_password('admin123')
    print(f"Hash para 'admin123':")
    print(f"'{admin_hash}'")
    print()
    
    # Gerar hash para teste123
    teste_hash = make_password('teste123')
    print(f"Hash para 'teste123':")
    print(f"'{teste_hash}'")
    print()
    
    # Gerar hash para gerente123
    gerente_hash = make_password('gerente123')
    print(f"Hash para 'gerente123':")
    print(f"'{gerente_hash}'")
    print()
    
    print("=" * 50)
    print("✅ Copie estes hashes para usar no script SQL")
    
except ImportError:
    print("❌ Django não configurado. Execute a partir do diretório do projeto.")
except Exception as e:
    print(f"❌ Erro: {e}") 