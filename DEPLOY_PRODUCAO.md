# Guia de Deploy em Produção

Este guia detalha como fazer o deploy do Sistema de Relatórios em um servidor Ubuntu usando Docker.

## 🔧 Pré-requisitos no Servidor

### 1. Acesso SSH
```bash
ssh root@31.97.168.137
```

### 2. Instalar Docker e Docker Compose
```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

### 3. Instalar Git
```bash
apt install git -y
```

## 📁 Configuração do Projeto

### 1. Clonar o Repositório
```bash
cd /opt
git clone https://github.com/SEU_USUARIO/DjangoSistem.git
cd DjangoSistem
```

### 2. Criar Arquivo de Ambiente de Produção
```bash
cp env.production.example .env
```

### 3. Configurar Variáveis de Ambiente
Edite o arquivo `.env`:
```bash
nano .env
```

Configure as seguintes variáveis:
```env
# Configurações básicas do Django
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
ENVIRONMENT=production

# Hosts permitidos (substitua pelo IP/domínio do seu servidor)
ALLOWED_HOSTS=31.97.168.137,localhost,127.0.0.1

# Configurações do banco PostgreSQL
POSTGRES_DB=relatorio_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha_segura_123
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (opcional - configure se precisar de notificações por email)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=Sistema de Relatórios <seu-email@gmail.com>

# Configurações de segurança
SECURE_SSL_REDIRECT=False
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
```

## 🚀 Deploy da Aplicação

### 1. Construir e Subir os Containers
```bash
# Construir as imagens
docker-compose -f docker-compose.prod.yml build

# Subir os serviços
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Verificar Status dos Containers
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 3. Configurar Banco de Dados

#### Aguardar PostgreSQL ficar pronto
```bash
# Aguardar alguns segundos para o PostgreSQL inicializar
sleep 30

# Verificar logs do banco
docker-compose -f docker-compose.prod.yml logs db
```

#### Executar Migrações
```bash
# Executar migrações do Django
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Coletar arquivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

#### Criar Superusuário
```bash
# Opção 1: Interativo
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Opção 2: Usando script (recomendado para automação)
docker-compose -f docker-compose.prod.yml exec web python create_superuser.py
```

#### Popular Banco com Dados Iniciais (Opcional)
```bash
# Executar comando de setup inicial
docker-compose -f docker-compose.prod.yml exec web python manage.py setup_initial_data
```

## 🛡️ Configurações de Segurança

### 1. Configurar Firewall
```bash
# Permitir apenas portas necessárias
ufw allow 22   # SSH
ufw allow 80   # HTTP
ufw allow 443  # HTTPS (se configurar SSL)
ufw enable
```

### 2. Configurar Nginx (Opcional - para SSL)
Se quiser usar SSL, crie um arquivo nginx personalizado:
```bash
nano nginx-ssl.conf
```

### 3. Backup do Banco de Dados
```bash
# Criar script de backup
cat > backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f /opt/DjangoSistem/docker-compose.prod.yml exec -T db pg_dump -U postgres relatorio_system > /opt/backups/db_backup_$DATE.sql
EOF

chmod +x backup_db.sh

# Criar diretório de backups
mkdir -p /opt/backups

# Adicionar ao crontab para backup automático (diário às 2h)
echo "0 2 * * * /opt/DjangoSistem/backup_db.sh" >> /etc/crontab
```

## 📊 Monitoramento e Logs

### Visualizar Logs
```bash
# Logs de todos os serviços
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml logs nginx
```

### Status dos Serviços
```bash
# Status dos containers
docker-compose -f docker-compose.prod.yml ps

# Uso de recursos
docker stats
```

## 🔄 Atualizações

### Para atualizar o sistema:
```bash
cd /opt/DjangoSistem

# Baixar atualizações
git pull origin main

# Reconstruir imagens
docker-compose -f docker-compose.prod.yml build

# Atualizar containers
docker-compose -f docker-compose.prod.yml up -d

# Executar migrações se necessário
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Coletar arquivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 🆘 Troubleshooting

### Se algo der errado:
```bash
# Parar todos os serviços
docker-compose -f docker-compose.prod.yml down

# Limpar volumes (CUIDADO: remove dados)
docker-compose -f docker-compose.prod.yml down -v

# Reiniciar do zero
docker-compose -f docker-compose.prod.yml up -d
```

### Acessar container para debug:
```bash
# Acessar container web
docker-compose -f docker-compose.prod.yml exec web bash

# Acessar banco de dados
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d relatorio_system
```

## 🌐 Acesso ao Sistema

Após o deploy, acesse:
- **Sistema**: http://31.97.168.137
- **Admin Django**: http://31.97.168.137/admin

## 📝 Notas Importantes

1. **Backup**: Configure backups automáticos do banco de dados
2. **SSL**: Configure certificado SSL para produção real
3. **Monitoramento**: Considere usar ferramentas como Sentry para monitoramento de erros
4. **Performance**: Para alta carga, considere usar mais workers do Gunicorn
5. **Segurança**: Mantenha o sistema sempre atualizado

## 🔐 Credenciais Padrão

Se usar o script de criação automática:
- **Usuário**: admin
- **Senha**: admin123
- **Email**: admin@sistema.com

**⚠️ IMPORTANTE**: Altere essas credenciais após o primeiro login! 