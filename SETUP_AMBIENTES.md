# Configuração de Ambientes - Sistema de Relatórios

Este sistema foi configurado para funcionar em dois ambientes diferentes:

1. **Desenvolvimento Local** (XAMPP com MySQL)
2. **Produção** (Render com PostgreSQL)

## 🖥️ Configuração Local (XAMPP)

### Pré-requisitos
- XAMPP instalado e funcionando
- Python 3.8+ instalado
- Git

### Passos para configuração:

1. **Clone o repositório** (se ainda não fez):
   ```bash
   git clone <url-do-repositorio>
   cd DjangoSistem
   ```

2. **Crie e ative um ambiente virtual**:
   ```bash
   python -m venv .venv
   # No Windows:
   .venv\Scripts\activate
   # No Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados MySQL**:
   - Abra o phpMyAdmin (http://localhost/phpmyadmin)
   - Crie um banco de dados chamado `relatorio_system`
   - Usuário: `root`, Senha: (deixe em branco ou configure conforme seu XAMPP)

5. **Configure as variáveis de ambiente**:
   - Copie o arquivo `env.local.example` para `.env`:
   ```bash
   copy env.local.example .env  # Windows
   # ou
   cp env.local.example .env    # Linux/Mac
   ```
   - Edite o arquivo `.env` se necessário (especialmente se sua senha do MySQL for diferente)

6. **Execute as migrações**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Crie um superusuário**:
   ```bash
   python manage.py createsuperuser
   ```

8. **Execute o servidor**:
   ```bash
   python manage.py runserver
   ```

O sistema estará disponível em http://localhost:8000

## ☁️ Configuração de Produção (Render)

### Pré-requisitos
- Conta no Render.com
- Banco PostgreSQL configurado no Render
- Repositório Git configurado

### Configuração no Render:

1. **Conecte seu repositório** ao Render

2. **Configure as variáveis de ambiente** no painel do Render:
   ```
   ENVIRONMENT=production
   SECRET_KEY=[gere uma chave secreta forte]
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com,.onrender.com
   
   # Banco PostgreSQL (obtido do Render Database)
   DB_NAME=dbrelatorio_rqkg
   DB_USER=dbrelatorio_rqkg_user
   DB_PASSWORD=CJZUYC4FeqPg3FfSZDVu75oSaXhpzPwV
   DB_HOST=dpg-d10oti95pdvs73acede0-a.oregon-postgres.render.com
   DB_PORT=5432
   
   # Email (configure com seu provedor)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=seu-email@gmail.com
   EMAIL_HOST_PASSWORD=sua-senha-de-app
   DEFAULT_FROM_EMAIL=Sistema de Relatórios <seu-email@gmail.com>
   
   # Redis (se usar Celery)
   REDIS_URL=redis://your-redis-url
   ```

3. **Configure o comando de build** no Render:
   ```bash
   pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python manage.py setup_admin && python manage.py create_test_user
   ```

4. **Configure o comando de start**:
   ```bash
   gunicorn relatorio_system.wsgi:application
   ```

## 🔄 Alternando entre Ambientes

O sistema detecta automaticamente o ambiente baseado nas variáveis:

- **Local**: Se `ENVIRONMENT=development` ou se não há `DB_HOST` com `.render.com`
- **Produção**: Se `ENVIRONMENT=production` ou se `DB_HOST` contém `.render.com`

### Principais diferenças entre ambientes:

| Funcionalidade | Local (XAMPP) | Produção (Render) |
|----------------|---------------|-------------------|
| Banco de Dados | MySQL | PostgreSQL |
| Debug | True | False |
| Email | Console | SMTP |
| Arquivos Estáticos | Servidos pelo Django | WhiteNoise |
| Segurança | Relaxada | Configurações seguras |

## 🛠️ Comandos Úteis

### Para desenvolvimento local:
```bash
# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
python manage.py runserver

# Coletar arquivos estáticos
python manage.py collectstatic
```

### Para produção (via Render):
- As migrações são executadas automaticamente no deploy
- Use os comandos de management personalizados no build

## 🚨 Troubleshooting

### Erro de conexão MySQL:
- Verifique se o XAMPP está rodando
- Confirme que o banco `relatorio_system` existe
- Verifique usuário e senha no arquivo `.env`

### Erro no Render:
- Verifique as variáveis de ambiente
- Consulte os logs do Render
- Confirme que o banco PostgreSQL está ativo

### 🔧 Banco de Produção Vazio (Problema Comum):
Se o banco PostgreSQL na hospedagem estiver vazio (sem tabelas), execute:

**Solução 1 - Script Local:**
```bash
python fix_production_db.py
```

**Solução 2 - Via Render Console:**
1. Acesse o Render Dashboard
2. Vá em "Shell" do seu serviço
3. Execute:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py setup_admin
python manage.py setup_initial_data
```

**Solução 3 - Redeploy:**
1. Faça um pequeno commit no seu repositório
2. O Render fará redeploy automático
3. Verifique os logs de build

### Dependências:
```bash
# Se der erro com mysqlclient no Windows:
pip install mysqlclient
# Se não funcionar, tente:
pip install PyMySQL
# E adicione no settings.py:
import pymysql
pymysql.install_as_MySQLdb()
```

## 📝 Notas Importantes

1. **Nunca commite o arquivo `.env`** - ele contém informações sensíveis
2. **Use chaves secretas diferentes** para cada ambiente
3. **Configure backups regulares** para o banco de produção
4. **Teste sempre localmente** antes de fazer deploy
5. **Mantenha as dependências atualizadas** mas teste antes de atualizar em produção 