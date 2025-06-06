-- ============================================================================
-- SCRIPT FINAL - INSERIR USUÁRIOS NO BANCO POSTGRESQL
-- Execute este script no pgAdmin para criar os usuários
-- ============================================================================

-- 1. REMOVER USUÁRIOS EXISTENTES (se houver)
DELETE FROM authentication_user WHERE username IN ('admin', 'teste');

-- 2. INSERIR ADMIN COM SENHA TEMPORÁRIA
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
    'admin',
    'pbkdf2_sha256$720000$temp123$hash123456789012345678901234567890123456789012345678901234567890=',
    'admin@sistema.com',
    'Administrador',
    'Sistema',
    TRUE,
    TRUE,
    TRUE,
    '',
    'TI',
    'Administrador',
    '',
    TRUE,
    NOW(),
    NOW(),
    NOW()
);

-- 3. INSERIR USUÁRIO DE TESTE
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
    'pbkdf2_sha256$720000$temp456$hash987654321098765432109876543210987654321098765432109876543210=',
    'teste@sistema.com',
    'Usuário',
    'Teste',
    FALSE,
    FALSE,
    TRUE,
    '',
    'Geral',
    'Teste',
    '',
    FALSE,
    NOW(),
    NOW(),
    NOW()
);

-- 4. VERIFICAR INSERÇÃO
SELECT 'USUÁRIOS INSERIDOS:' AS status;
SELECT id, username, email, is_superuser, is_staff, departamento 
FROM authentication_user;

-- 5. MENSAGEM FINAL
SELECT '✅ USUÁRIOS CRIADOS!' AS resultado;
SELECT '⚠️ IMPORTANTE: Redefina as senhas via Django Admin' AS aviso;
SELECT 'Acesse: /admin e use "Esqueci minha senha"' AS instrucao; 