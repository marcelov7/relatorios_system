# 🚨 Solução Rápida - Erro de Constraint

## ❌ Problema Identificado
```
ERROR: null value in column "telefone" violates not-null constraint
```

## ✅ 3 Soluções (escolha uma):

### 🎯 Solução 1: Script SQL Corrigido (RECOMENDADO)
Execute no pgAdmin:
```sql
-- Deletar usuário com problema
DELETE FROM authentication_user WHERE username = 'admin';

-- Inserir corretamente
INSERT INTO authentication_user (
    username, password, email, first_name, last_name,
    is_superuser, is_staff, is_active,
    telefone, departamento, cargo, foto_perfil, is_manager
) VALUES (
    'admin',
    'pbkdf2_sha256$720000$temp$hashabcdef123456789',
    'admin@sistema.com',
    'Administrador', 'Sistema',
    TRUE, TRUE, TRUE,
    '', 'TI', 'Administrador', '', TRUE
);
```

### 🌐 Solução 2: Console do Render (MAIS FÁCIL)
1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique no seu serviço "relatorio-system"
3. Vá em "Shell"
4. Execute:
```bash
python manage.py shell
```
5. Cole este código Python:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Deletar admin antigo
User.objects.filter(username='admin').delete()

# Criar novo admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@sistema.com', 
    password='admin123',
    first_name='Administrador',
    last_name='Sistema',
    departamento='TI',
    cargo='Administrador'
)
print("Admin criado: admin / admin123")
```

### 🔧 Solução 3: Comando Django
No console do Render:
```bash
python manage.py createsuperuser
```
E preencha os dados quando solicitado.

## 📋 Verificar se Funcionou

1. **Acesse sua URL do Render**
2. **Vá para `/admin`**  
3. **Faça login** com `admin` / `admin123`
4. **Se funcionar**: ✅ Problema resolvido!

## 🎯 Causa do Problema

O campo `telefone` na tabela `authentication_user` foi definido como `NOT NULL DEFAULT ''`, mas na inserção não especificamos valor, então tentou inserir `NULL`.

## 💡 Prevenção Futura

Sempre especificar valores para campos obrigatórios:
- `telefone` → `''` (string vazia)
- `foto_perfil` → `''` (string vazia)
- `departamento` → valor válido
- `cargo` → valor válido

## 🆘 Se Nada Funcionar

Execute este comando no pgAdmin para limpar tudo:
```sql
DELETE FROM authentication_user;
```

Depois use a **Solução 2** (Console do Render) que é a mais confiável. 