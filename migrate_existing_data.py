#!/usr/bin/env python3
"""
Script para migrar dados existentes do SQLite para PostgreSQL
Execute este script APÓS o deploy inicial para importar dados existentes
"""

import os
import sys
import django
import sqlite3
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'relatorio_system.settings')
django.setup()

from authentication.models import User
from reports.models import Report, ReportCategory
from locations.models import Local, Equipamento
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import json

def migrate_users_from_sqlite():
    """Migrar usuários do SQLite para PostgreSQL"""
    print("🔄 Migrando usuários...")
    
    if not os.path.exists('db.sqlite3'):
        print("❌ Arquivo db.sqlite3 não encontrado!")
        return
    
    # Conectar ao SQLite
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Buscar usuários no SQLite
        cursor.execute("""
            SELECT username, email, first_name, last_name, password, 
                   is_active, is_staff, is_superuser, date_joined,
                   telefone, departamento, cargo, is_manager
            FROM authentication_user
        """)
        
        users_data = cursor.fetchall()
        migrated_count = 0
        
        for user_data in users_data:
            username, email, first_name, last_name, password, is_active, is_staff, is_superuser, date_joined, telefone, departamento, cargo, is_manager = user_data
            
            # Verificar se usuário já existe
            if User.objects.filter(username=username).exists():
                print(f"⚠️  Usuário {username} já existe, pulando...")
                continue
            
            # Criar usuário
            user = User.objects.create(
                username=username,
                email=email or f"{username}@sistema.local",
                first_name=first_name or '',
                last_name=last_name or '',
                password=password,  # Senha já está hasheada
                is_active=bool(is_active),
                is_staff=bool(is_staff),
                is_superuser=bool(is_superuser),
                telefone=telefone or '',
                departamento=departamento or '',
                cargo=cargo or '',
                is_manager=bool(is_manager),
            )
            
            migrated_count += 1
            print(f"✅ Usuário {username} migrado com sucesso")
        
        print(f"📊 Total de usuários migrados: {migrated_count}")
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao migrar usuários: {e}")
    finally:
        conn.close()

def migrate_categories_from_sqlite():
    """Migrar categorias de relatórios"""
    print("🔄 Migrando categorias...")
    
    if not os.path.exists('db.sqlite3'):
        print("❌ Arquivo db.sqlite3 não encontrado!")
        return
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name, description, color, is_active, created_at
            FROM reports_reportcategory
        """)
        
        categories_data = cursor.fetchall()
        migrated_count = 0
        
        for cat_data in categories_data:
            name, description, color, is_active, created_at = cat_data
            
            if ReportCategory.objects.filter(name=name).exists():
                print(f"⚠️  Categoria {name} já existe, pulando...")
                continue
            
            category = ReportCategory.objects.create(
                name=name,
                description=description or '',
                color=color or '#007bff',
                is_active=bool(is_active),
            )
            
            migrated_count += 1
            print(f"✅ Categoria {name} migrada com sucesso")
        
        print(f"📊 Total de categorias migradas: {migrated_count}")
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao migrar categorias: {e}")
    finally:
        conn.close()

def migrate_reports_from_sqlite():
    """Migrar relatórios"""
    print("🔄 Migrando relatórios...")
    
    if not os.path.exists('db.sqlite3'):
        print("❌ Arquivo db.sqlite3 não encontrado!")
        return
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT title, description, content, status, priority,
                   created_by_id, category_id, created_at, updated_at, file
            FROM reports_report
        """)
        
        reports_data = cursor.fetchall()
        migrated_count = 0
        
        for report_data in reports_data:
            title, description, content, status, priority, created_by_id, category_id, created_at, updated_at, file = report_data
            
            # Buscar usuário criador
            try:
                created_by = User.objects.get(id=created_by_id) if created_by_id else None
            except User.DoesNotExist:
                print(f"⚠️  Usuário ID {created_by_id} não encontrado, pulando relatório {title}")
                continue
            
            # Buscar categoria
            try:
                category = ReportCategory.objects.get(id=category_id) if category_id else None
            except ReportCategory.DoesNotExist:
                category = None
            
            report = Report.objects.create(
                title=title,
                description=description or '',
                content=content or '',
                status=status or 'draft',
                priority=priority or 'medium',
                created_by=created_by,
                category=category,
                file=file or '',
            )
            
            migrated_count += 1
            print(f"✅ Relatório {title} migrado com sucesso")
        
        print(f"📊 Total de relatórios migrados: {migrated_count}")
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao migrar relatórios: {e}")
    finally:
        conn.close()

def migrate_locations_from_sqlite():
    """Migrar locais e equipamentos"""
    print("🔄 Migrando locais e equipamentos...")
    
    if not os.path.exists('db.sqlite3'):
        print("❌ Arquivo db.sqlite3 não encontrado!")
        return
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Migrar locais
        cursor.execute("""
            SELECT nome, endereco, cidade, cep, responsavel_id, ativo
            FROM locations_local
        """)
        
        locations_data = cursor.fetchall()
        loc_migrated = 0
        
        for loc_data in locations_data:
            nome, endereco, cidade, cep, responsavel_id, ativo = loc_data
            
            if Local.objects.filter(nome=nome).exists():
                print(f"⚠️  Local {nome} já existe, pulando...")
                continue
            
            # Buscar responsável
            try:
                responsavel = User.objects.get(id=responsavel_id) if responsavel_id else None
            except User.DoesNotExist:
                responsavel = None
            
            local = Local.objects.create(
                nome=nome,
                endereco=endereco or '',
                cidade=cidade or '',
                cep=cep or '',
                responsavel=responsavel,
                ativo=bool(ativo),
            )
            
            loc_migrated += 1
            print(f"✅ Local {nome} migrado com sucesso")
        
        # Migrar equipamentos
        cursor.execute("""
            SELECT patrimonio, tipo, modelo, status_operacional, data_instalacao,
                   observacoes, local_id, responsavel_id
            FROM locations_equipamento
        """)
        
        equipment_data = cursor.fetchall()
        eq_migrated = 0
        
        for eq_data in equipment_data:
            patrimonio, tipo, modelo, status, data_instalacao, observacoes, local_id, responsavel_id = eq_data
            
            if Equipamento.objects.filter(patrimonio=patrimonio).exists():
                print(f"⚠️  Equipamento {patrimonio} já existe, pulando...")
                continue
            
            # Buscar local
            try:
                local = Local.objects.get(id=local_id) if local_id else None
            except Local.DoesNotExist:
                local = None
            
            # Buscar responsável
            try:
                responsavel = User.objects.get(id=responsavel_id) if responsavel_id else None
            except User.DoesNotExist:
                responsavel = None
            
            equipamento = Equipamento.objects.create(
                patrimonio=patrimonio,
                tipo=tipo or '',
                modelo=modelo or '',
                status_operacional=status or 'funcionando',
                data_instalacao=data_instalacao,
                observacoes=observacoes or '',
                local=local,
                responsavel=responsavel,
            )
            
            eq_migrated += 1
            print(f"✅ Equipamento {patrimonio} migrado com sucesso")
        
        print(f"📊 Total de locais migrados: {loc_migrated}")
        print(f"📊 Total de equipamentos migrados: {eq_migrated}")
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao migrar locais/equipamentos: {e}")
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 Iniciando migração de dados do SQLite para PostgreSQL")
    print("=" * 60)
    
    if not os.path.exists('db.sqlite3'):
        print("❌ Arquivo db.sqlite3 não encontrado no diretório atual!")
        print("💡 Certifique-se de que o arquivo SQLite está no mesmo diretório deste script")
        return
    
    try:
        # Verificar conexão com PostgreSQL
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Conexão com PostgreSQL estabelecida")
        
        # Executar migrações
        migrate_users_from_sqlite()
        print("-" * 40)
        migrate_categories_from_sqlite()
        print("-" * 40)
        migrate_reports_from_sqlite()
        print("-" * 40)
        migrate_locations_from_sqlite()
        
        print("\n🎉 Migração concluída com sucesso!")
        print("=" * 60)
        print("📋 Próximos passos:")
        print("1. Verifique os dados migrados no admin Django")
        print("2. Teste o login com os usuários migrados")
        print("3. Faça backup do banco PostgreSQL")
        print("4. Remova o arquivo db.sqlite3 se tudo estiver correto")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        print("💡 Verifique se:")
        print("  - O PostgreSQL está rodando")
        print("  - As migrações do Django foram executadas")
        print("  - As configurações do banco estão corretas")

if __name__ == "__main__":
    main() 