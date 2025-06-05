#!/usr/bin/env python
"""
Script para criar superusuário automaticamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'relatorio_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    """Cria superusuário se não existir"""
    username = 'admin'
    email = 'admin@sistema.com'
    password = 'admin123'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Administrador',
            last_name='Sistema',
            departamento='TI',
            cargo='Administrador do Sistema',
            is_manager=True
        )
        print(f"✅ Superusuário criado: {username} / {password}")
    else:
        print(f"ℹ️ Superusuário {username} já existe")

if __name__ == "__main__":
    create_superuser() 