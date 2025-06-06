# 🗄️ Guia: Configurar Banco via pgAdmin

## 📋 Passo a Passo para Corrigir o Banco PostgreSQL

### 1️⃣ Preparação

**No seu computador local:**
1. Execute o gerador de senhas:
   ```bash
   python generate_password_hashes.py
   ```
2. Copie os hashes gerados (você vai precisar deles)

### 2️⃣ Conectar no pgAdmin

**Configuração da conexão:**
- **Host**: `dpg-d10oti95pdvs73acede0-a.oregon-postgres.render.com`
- **Port**: `5432`
- **Database**: `dbrelatorio_rqkg`
- **Username**: `dbrelatorio_rqkg_user`
- **Password**: `CJZUYC4FeqPg3FfSZDVu75oSaXhpzPwV`

### 3️⃣ Executar Script SQL

1. **Abra o Query Tool** no pgAdmin (botão SQL ou F5)
2. **Copie o conteúdo** do arquivo `setup_quick.sql`
3. **Atualize as senhas** na seção do admin:
   ```sql
   -- Troque esta linha:
   'pbkdf2_sha256$600000$temp$hash',
   
   -- Por uma das senhas geradas pelo script Python:
   'pbkdf2_sha256$600000$...',  -- Hash real aqui
   ```
4. **Execute o script** (F5 ou botão Execute)

### 4️⃣ Verificar Resultado

**O script deve mostrar:**
- ✅ Tabelas criadas
- ✅ Usuários inseridos  
- ✅ Categorias criadas
- ✅ Configuração concluída

### 5️⃣ Teste de Acesso

1. **Acesse sua URL do Render**
2. **Faça login** com: `admin` / `admin123`
3. **Se funcionar**: ✅ Sucesso!
4. **Se não funcionar**: Execute script de correção de senha (próximo passo)

### 6️⃣ Corrigir Senha (se necessário)

Se a senha não funcionar, execute este comando SQL:

```sql
-- Atualizar senha do admin
UPDATE authentication_user 
SET password = 'HASH_GERADO_PELO_SCRIPT_PYTHON'
WHERE username = 'admin';
```

### 7️⃣ Scripts Disponíveis

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `setup_quick.sql` | Configuração rápida e básica | Primeira vez / Teste rápido |
| `setup_production_database.sql` | Configuração completa | Configuração definitiva |
| `generate_password_hashes.py` | Gerar senhas Django | Antes de executar SQL |

### 🚨 Solução de Problemas

**Erro de conexão:**
- Verifique se as credenciais estão corretas
- Confirme que o banco PostgreSQL está ativo no Render

**Erro nas tabelas:**
- Execute `DROP TABLE` se precisar recomeçar
- Use `IF NOT EXISTS` está nos scripts para evitar conflitos

**Erro de senha:**
- Execute `generate_password_hashes.py` novamente
- Copie o hash completo (incluindo aspas)
- Atualize no SQL e execute novamente

### 🎯 Comandos SQL Úteis

**Verificar tabelas existentes:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

**Verificar usuários:**
```sql
SELECT username, email, is_superuser, is_active 
FROM authentication_user;
```

**Limpar tudo (CUIDADO!):**
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

**Verificar dados:**
```sql
SELECT COUNT(*) as total_users FROM authentication_user;
SELECT COUNT(*) as total_categories FROM reports_reportcategory;
```

### ✅ Resultado Esperado

Após executar com sucesso:

- **Banco**: Tabelas criadas e populadas
- **Admin**: `admin` / `admin123` funcionando
- **Sistema**: Acessível via URL do Render
- **Categorias**: 6 categorias criadas
- **Pronto**: Para uso em produção

### 📞 Próximos Passos

1. **Teste o sistema** completo
2. **Crie usuários** reais via Django Admin
3. **Configure backup** do banco
4. **Monitore logs** do Render 