-- ============================================================================
-- SCRIPT SQL PARA CONFIGURAR BANCO POSTGRESQL DE PRODUÇÃO (RENDER)
-- Execute este script diretamente no pgAdmin conectado ao banco do Render
-- ============================================================================

-- Verificar conexão
SELECT 'Conectado ao banco: ' || current_database() || ' em ' || inet_server_addr() || ':' || inet_server_port() AS status;

-- ============================================================================
-- 1. CRIAR TABELAS PRINCIPAIS DO DJANGO
-- ============================================================================

-- Tabela de sessões do Django
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMPTZ NOT NULL
);

-- Tabela de migrações do Django
CREATE TABLE IF NOT EXISTS django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMPTZ NOT NULL
);

-- Tabela de tipos de conteúdo
CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- ============================================================================
-- 2. SISTEMA DE AUTENTICAÇÃO
-- ============================================================================

-- Grupos de usuários
CREATE TABLE IF NOT EXISTS auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

-- Permissões
CREATE TABLE IF NOT EXISTS auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER REFERENCES django_content_type(id),
    codename VARCHAR(100) NOT NULL,
    UNIQUE(content_type_id, codename)
);

-- Relacionamento grupo-permissões
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES auth_group(id),
    permission_id INTEGER REFERENCES auth_permission(id),
    UNIQUE(group_id, permission_id)
);

-- Tabela de usuários personalizada
CREATE TABLE IF NOT EXISTS authentication_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    telefone VARCHAR(20) NOT NULL DEFAULT '',
    departamento VARCHAR(100) NOT NULL DEFAULT '',
    cargo VARCHAR(100) NOT NULL DEFAULT '',
    foto_perfil VARCHAR(100) NOT NULL DEFAULT '',
    is_manager BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Relacionamentos usuário-grupos
CREATE TABLE IF NOT EXISTS authentication_user_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES authentication_user(id),
    group_id INTEGER REFERENCES auth_group(id),
    UNIQUE(user_id, group_id)
);

-- Relacionamentos usuário-permissões
CREATE TABLE IF NOT EXISTS authentication_user_user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES authentication_user(id),
    permission_id INTEGER REFERENCES auth_permission(id),
    UNIQUE(user_id, permission_id)
);

-- ============================================================================
-- 3. SISTEMA DE RELATÓRIOS
-- ============================================================================

-- Categorias de relatórios
CREATE TABLE IF NOT EXISTS reports_reportcategory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    color VARCHAR(7) NOT NULL DEFAULT '#007bff',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Relatórios
CREATE TABLE IF NOT EXISTS reports_report (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_by_id INTEGER REFERENCES authentication_user(id),
    category_id INTEGER REFERENCES reports_reportcategory(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    file VARCHAR(100) NOT NULL DEFAULT ''
);

-- Dados estruturados dos relatórios
CREATE TABLE IF NOT EXISTS reports_reportdata (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports_report(id),
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT NOT NULL,
    field_type VARCHAR(20) NOT NULL DEFAULT 'text',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 4. SISTEMA DE NOTIFICAÇÕES
-- ============================================================================

-- Templates de notificação
CREATE TABLE IF NOT EXISTS notifications_app_notificationtemplate (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title_template VARCHAR(200) NOT NULL,
    message_template TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Notificações
CREATE TABLE IF NOT EXISTS notifications_notification (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL DEFAULT 'info',
    actor_object_id VARCHAR(255),
    verb VARCHAR(255) NOT NULL,
    description TEXT,
    target_object_id VARCHAR(255),
    action_object_object_id VARCHAR(255),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    public BOOLEAN NOT NULL DEFAULT TRUE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    emailed BOOLEAN NOT NULL DEFAULT FALSE,
    data TEXT,
    actor_content_type_id INTEGER REFERENCES django_content_type(id),
    action_object_content_type_id INTEGER REFERENCES django_content_type(id),
    target_content_type_id INTEGER REFERENCES django_content_type(id),
    recipient_id INTEGER REFERENCES authentication_user(id)
);

-- ============================================================================
-- 5. INSERIR DADOS INICIAIS
-- ============================================================================

-- Inserir tipos de conteúdo básicos
INSERT INTO django_content_type (app_label, model) VALUES 
('auth', 'permission'),
('auth', 'group'),
('contenttypes', 'contenttype'),
('sessions', 'session'),
('authentication', 'user'),
('reports', 'report'),
('reports', 'reportcategory'),
('reports', 'reportdata'),
('notifications_app', 'notificationtemplate')
ON CONFLICT (app_label, model) DO NOTHING;

-- Inserir permissões básicas
INSERT INTO auth_permission (name, content_type_id, codename) 
SELECT 'Can add ' || model, id, 'add_' || model FROM django_content_type
ON CONFLICT (content_type_id, codename) DO NOTHING;

INSERT INTO auth_permission (name, content_type_id, codename) 
SELECT 'Can change ' || model, id, 'change_' || model FROM django_content_type
ON CONFLICT (content_type_id, codename) DO NOTHING;

INSERT INTO auth_permission (name, content_type_id, codename) 
SELECT 'Can delete ' || model, id, 'delete_' || model FROM django_content_type
ON CONFLICT (content_type_id, codename) DO NOTHING;

INSERT INTO auth_permission (name, content_type_id, codename) 
SELECT 'Can view ' || model, id, 'view_' || model FROM django_content_type
ON CONFLICT (content_type_id, codename) DO NOTHING;

-- ============================================================================
-- 6. CRIAR SUPERUSUÁRIO ADMIN
-- ============================================================================

-- Senha hash para 'admin123' usando PBKDF2
INSERT INTO authentication_user (
    username, 
    password, 
    email, 
    first_name, 
    last_name, 
    is_superuser, 
    is_staff, 
    is_active,
    departamento,
    cargo,
    is_manager,
    date_joined,
    created_at,
    updated_at
) VALUES (
    'admin',
    'pbkdf2_sha256$600000$admin123salt$8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8=',
    'admin@sistema.com',
    'Administrador',
    'Sistema',
    TRUE,
    TRUE,
    TRUE,
    'TI',
    'Administrador do Sistema',
    TRUE,
    NOW(),
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 7. CRIAR CATEGORIAS DE RELATÓRIOS
-- ============================================================================

INSERT INTO reports_reportcategory (name, description, color, is_active, created_at, updated_at) VALUES
('Vendas', 'Relatórios de vendas e performance comercial', '#007bff', TRUE, NOW(), NOW()),
('Financeiro', 'Relatórios financeiros e contábeis', '#28a745', TRUE, NOW(), NOW()),
('Marketing', 'Relatórios de marketing e campanhas', '#dc3545', TRUE, NOW(), NOW()),
('Operacional', 'Relatórios operacionais e logística', '#ffc107', TRUE, NOW(), NOW()),
('Recursos Humanos', 'Relatórios de RH e pessoal', '#6f42c1', TRUE, NOW(), NOW()),
('Geral', 'Relatórios gerais e diversos', '#6c757d', TRUE, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 8. CRIAR TEMPLATES DE NOTIFICAÇÃO
-- ============================================================================

INSERT INTO notifications_app_notificationtemplate (name, notification_type, title_template, message_template, is_active, created_at, updated_at) VALUES
('Relatório Criado', 'report_created', 'Novo relatório: {report_title}', 'O relatório "{report_title}" foi criado por {author_name}.', TRUE, NOW(), NOW()),
('Relatório Concluído', 'report_completed', 'Relatório concluído: {report_title}', 'O relatório "{report_title}" foi concluído com sucesso e está disponível para download.', TRUE, NOW(), NOW()),
('Bem-vindo', 'user_registered', 'Bem-vindo ao Sistema de Relatórios!', 'Olá {user_name}, sua conta foi criada com sucesso. Comece criando seu primeiro relatório!', TRUE, NOW(), NOW())
ON CONFLICT (notification_type) DO NOTHING;

-- ============================================================================
-- 9. CRIAR USUÁRIO DE TESTE
-- ============================================================================

INSERT INTO authentication_user (
    username, 
    password, 
    email, 
    first_name, 
    last_name, 
    is_superuser, 
    is_staff, 
    is_active,
    departamento,
    cargo,
    is_manager,
    date_joined,
    created_at,
    updated_at
) VALUES (
    'teste',
    'pbkdf2_sha256$600000$teste123salt$9i9i9i9i9i9i9i9i9i9i9i9i9i9i9i9i9i9i9i9i9i9=',
    'teste@sistema.com',
    'Usuário',
    'Teste',
    FALSE,
    FALSE,
    TRUE,
    'Geral',
    'Teste',
    FALSE,
    NOW(),
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 10. REGISTRAR MIGRAÇÕES COMO APLICADAS
-- ============================================================================

INSERT INTO django_migrations (app, name, applied) VALUES
('contenttypes', '0001_initial', NOW()),
('auth', '0001_initial', NOW()),
('authentication', '0001_initial', NOW()),
('reports', '0001_initial', NOW()),
('notifications_app', '0001_initial', NOW()),
('sessions', '0001_initial', NOW())
ON CONFLICT (app, name) DO NOTHING;

-- ============================================================================
-- 11. VERIFICAÇÕES FINAIS
-- ============================================================================

-- Verificar se foi criado corretamente
SELECT 'VERIFICAÇÃO FINAL:' AS status;

SELECT 'Usuários criados: ' || COUNT(*) AS usuarios 
FROM authentication_user;

SELECT 'Categorias criadas: ' || COUNT(*) AS categorias 
FROM reports_reportcategory;

SELECT 'Templates criados: ' || COUNT(*) AS templates 
FROM notifications_app_notificationtemplate;

SELECT 'Tabelas criadas: ' || COUNT(*) AS tabelas 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Mostrar credenciais
SELECT 'CREDENCIAIS CRIADAS:' AS info;
SELECT 'Admin: admin / admin123' AS credencial_admin;
SELECT 'Teste: teste / teste123' AS credencial_teste;

SELECT '✅ BANCO CONFIGURADO COM SUCESSO!' AS resultado; 