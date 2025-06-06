# 🔑 Corrigir Senhas Inválidas

## ❌ Problema Identificado
- ✅ Usuários existem no banco
- ❌ Login falha: "credenciais inválidas"
- 🎯 **Causa**: Senhas hash inseridas via SQL estão incorretas

## ✅ Solução RÁPIDA (Console do Render)

### 1️⃣ Acesse o Console do Render
1. [Render Dashboard](https://dashboard.render.com)
2. Clique no seu serviço "relatorio-system"
3. Vá em **Shell**

### 2️⃣ Execute Comandos Python
Cole este código no console:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Resetar senha do admin
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.is_superuser = True
admin.is_staff = True
admin.save()
print("✅ Admin senha resetada")

# Resetar senha do teste  
teste = User.objects.get(username='teste')
teste.set_password('teste123')
teste.save()
print("✅ Teste senha resetada")

print("🔑 Use: admin / admin123")
```

### 3️⃣ Teste o Login
1. Acesse sua URL do Render
2. Vá para `/admin`
3. Login: **admin** / **admin123**

## 🚀 Solução Alternativa (Comando Django)

No console do Render:
```bash
python manage.py changepassword admin
```
Digite a nova senha quando solicitado.

## 🔍 Verificar Usuários Existentes

Console Python:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

for user in User.objects.all():
    print(f"{user.username} - Superuser: {user.is_superuser}")
```

## 🎯 Por que Aconteceu?

**Senhas via SQL são problemáticas:**
- Django usa hash específico (PBKDF2)
- Salt randômico para cada senha
- Inserção manual via SQL gera hash inválido

**Solução correta:**
- Sempre usar Django ORM: `user.set_password()`
- Nunca inserir hash manualmente

## 📋 Credenciais Após Correção

- **Admin**: admin / admin123
- **Teste**: teste / teste123
- **Marcelo**: marcelo / marcelo123 (se existir)

## 🆘 Se Ainda Não Funcionar

1. **Criar novo admin**:
```bash
python manage.py createsuperuser
```

2. **Verificar configuração**:
```python
from django.conf import settings
print(settings.AUTH_USER_MODEL)
```

3. **Último recurso** - deletar e recriar:
```python
User.objects.filter(username='admin').delete()
User.objects.create_superuser('admin', 'admin@sistema.com', 'admin123')
``` 