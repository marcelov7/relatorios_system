-- ============================================================================
-- SCRIPT PARA CORRIGIR INSERÇÃO DO USUÁRIO ADMIN
-- Execute após o erro de constraint NOT NULL
-- ============================================================================

-- 1. VERIFICAR SE O USUÁRIO JÁ EXISTE
SELECT 'Verificando usuários existentes...' AS status;
SELECT username, email, is_superuser FROM authentication_user;

-- 2. DELETAR USUÁRIO ADMIN SE EXISTIR (para recriar corretamente)
DELETE FROM authentication_user WHERE username = 'admin';

-- 3. INSERIR USUÁRIO ADMIN COM TODOS OS CAMPOS OBRIGATÓRIOS
INSERT INTO authentication_user (
    username, 
    password, 
    email, 
    first_name, 
    last_name, 
    is_superuser, 
    is_staff, 
    is_active,
    telefone,           -- Campo obrigatório
    departamento,
    cargo,
    foto_perfil,        -- Campo obrigatório  
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
    '',                 -- telefone vazio (não null)
    'TI',
    'Administrador do Sistema',
    '',                 -- foto_perfil vazio (não null)
    TRUE,
    NOW(),
    NOW(),
    NOW()
);

-- 4. INSERIR USUÁRIO DE TESTE TAMBÉM
INSERT INTO authentication_user (
    username, 
    password, 
    email, 
    first_name, 
    last_name, 
    is_superuser, 
    is_staff, 
    is_active,
    telefone,
    departamento,
    cargo,
    foto_perfil,
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
    '',
    'Geral',
    'Usuário de Teste',
    '',
    FALSE,
    NOW(),
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;

-- 5. VERIFICAR SE FOI INSERIDO CORRETAMENTE
SELECT 'RESULTADO:' AS status;
SELECT username, email, telefone, departamento, is_superuser, is_staff 
FROM authentication_user;

SELECT '✅ USUÁRIOS CRIADOS COM SUCESSO!' AS resultado;
SELECT 'Login: admin / admin123' AS credencial_admin;
SELECT 'Login: teste / teste123' AS credencial_teste; 