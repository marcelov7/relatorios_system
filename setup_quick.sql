-- ============================================================================
-- SCRIPT RÁPIDO - CONFIGURAR BANCO POSTGRESQL (RENDER)
-- Execute este script no pgAdmin conectado ao banco do Render
-- ============================================================================

-- 1. VERIFICAR CONEXÃO
SELECT 'Conectado ao banco PostgreSQL do Render' AS status;

-- 2. CRIAR TABELA DE USUÁRIOS (principal)
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

-- 3. CRIAR TABELA DE CATEGORIAS
CREATE TABLE IF NOT EXISTS reports_reportcategory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    color VARCHAR(7) NOT NULL DEFAULT '#007bff',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. CRIAR TABELA DE RELATÓRIOS
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

-- 5. CRIAR TABELAS DO DJANGO (essenciais)
CREATE TABLE IF NOT EXISTS django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMPTZ NOT NULL
);

-- 6. INSERIR SUPERUSUÁRIO ADMIN
-- NOTA: Execute o script generate_password_hashes.py para obter senhas corretas
-- Por enquanto, usamos um hash temporário (você deve trocar depois)
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
    is_manager
) VALUES (
    'admin',
    'pbkdf2_sha256$600000$temp$hash',  -- TROCAR por hash real
    'admin@sistema.com',
    'Administrador',
    'Sistema',
    TRUE,
    TRUE,
    TRUE,
    'TI',
    'Administrador',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- 7. INSERIR CATEGORIAS
INSERT INTO reports_reportcategory (name, description, color) VALUES
('Vendas', 'Relatórios de vendas', '#007bff'),
('Financeiro', 'Relatórios financeiros', '#28a745'),
('Marketing', 'Relatórios de marketing', '#dc3545'),
('Operacional', 'Relatórios operacionais', '#ffc107'),
('RH', 'Relatórios de RH', '#6f42c1'),
('Geral', 'Relatórios gerais', '#6c757d')
ON CONFLICT (name) DO NOTHING;

-- 8. REGISTRAR MIGRAÇÕES
INSERT INTO django_migrations (app, name, applied) VALUES
('authentication', '0001_initial', NOW()),
('reports', '0001_initial', NOW()),
('contenttypes', '0001_initial', NOW()),
('sessions', '0001_initial', NOW())
ON CONFLICT (app, name) DO NOTHING;

-- 9. VERIFICAR RESULTADO
SELECT 'Tabelas criadas:' AS info;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

SELECT 'Usuários:' AS info;
SELECT username, email, is_superuser FROM authentication_user;

SELECT 'Categorias:' AS info;
SELECT name, color FROM reports_reportcategory;

SELECT '✅ CONFIGURAÇÃO BÁSICA CONCLUÍDA!' AS resultado;
SELECT '⚠️ IMPORTANTE: Atualize a senha do admin usando Django Admin' AS aviso; 