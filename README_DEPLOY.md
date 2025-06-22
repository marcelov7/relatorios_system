# 🚀 Deploy do Sistema de Relatórios - Guia Completo

Este guia te ajudará a fazer o deploy completo do sistema no seu servidor `31.97.168.137`, incluindo a migração dos dados existentes.

## 📋 Resumo do Processo

1. **Preparar o servidor** (instalar Docker, Git, etc.)
2. **Configurar o projeto** (clonar repositório, configurar ambiente)
3. **Fazer deploy** (subir containers, configurar banco)
4. **Migrar dados existentes** (do SQLite para PostgreSQL)
5. **Configurações finais** (segurança, backups)

## 🎯 Instruções Passo a Passo

### 1. Conectar ao Servidor
```bash
ssh root@31.97.168.137
```

### 2. Preparar o Servidor
Execute estes comandos no servidor:

```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Instalar Git
apt install git -y

# Verificar instalação
docker --version
docker-compose --version
```

### 3. Clonar e Configurar o Projeto

```bash
# Ir para diretório de aplicações
cd /opt

# Clonar o repositório (substitua pela URL do seu repositório)
git clone https://github.com/SEU_USUARIO/DjangoSistem.git
cd DjangoSistem

# Criar arquivo de ambiente
cp env.production.example .env

# Editar configurações
nano .env
```

**Configurações importantes no `.env`:**
```env
SECRET_KEY=sua-chave-secreta-muito-segura-aqui-123456789
DEBUG=False
ALLOWED_HOSTS=31.97.168.137,localhost,127.0.0.1
POSTGRES_DB=relatorio_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SenhaMuitoSegura123!
```

### 4. Fazer Deploy Automatizado

```bash
# Tornar script executável
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

**OU fazer deploy manual:**

```bash
# Construir e subir containers
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Aguardar PostgreSQL ficar pronto
sleep 30

# Executar migrações
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Coletar arquivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Criar superusuário
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 5. Migrar Dados Existentes (Se Aplicável)

Se você tem dados no SQLite que quer migrar:

```bash
# Copiar arquivo SQLite para o servidor (do seu computador local)
scp db.sqlite3 root@31.97.168.137:/opt/DjangoSistem/

# No servidor, executar migração
cd /opt/DjangoSistem
docker-compose -f docker-compose.prod.yml exec web python migrate_existing_data.py
```

### 6. Configurações de Segurança

```bash
# Configurar firewall
ufw allow 22   # SSH
ufw allow 80   # HTTP
ufw allow 443  # HTTPS (futuro)
ufw enable

# Criar script de backup
cat > backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p /opt/backups
docker-compose -f /opt/DjangoSistem/docker-compose.prod.yml exec -T db pg_dump -U postgres relatorio_system > /opt/backups/db_backup_$DATE.sql
echo "Backup criado: /opt/backups/db_backup_$DATE.sql"
EOF

chmod +x backup_db.sh

# Backup automático diário (2h da manhã)
echo "0 2 * * * /opt/DjangoSistem/backup_db.sh" >> /etc/crontab
```

## 🌐 Acessar o Sistema

Após o deploy:
- **Sistema Principal**: http://31.97.168.137
- **Área Administrativa**: http://31.97.168.137/admin

## 📊 Comandos Úteis

### Verificar Status
```bash
cd /opt/DjangoSistem
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

### Backup Manual
```bash
./backup_db.sh
```

### Atualizar Sistema
```bash
cd /opt/DjangoSistem
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Troubleshooting
```bash
# Reiniciar todos os serviços
docker-compose -f docker-compose.prod.yml restart

# Ver logs específicos
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs db

# Acessar container para debug
docker-compose -f docker-compose.prod.yml exec web bash
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d relatorio_system
```

## ⚠️ Problemas Comuns e Soluções

### 1. Container web não inicia
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs web

# Possíveis soluções:
# - Verificar se SECRET_KEY está configurada no .env
# - Verificar se banco está acessível
# - Executar migrações novamente
```

### 2. Banco de dados não conecta
```bash
# Verificar se PostgreSQL está rodando
docker-compose -f docker-compose.prod.yml logs db

# Reiniciar apenas o banco
docker-compose -f docker-compose.prod.yml restart db
```

### 3. Permissões de arquivo
```bash
# Ajustar permissões dos volumes
docker-compose -f docker-compose.prod.yml exec web chown -R app:app /app/media
```

## 🔐 Segurança Adicional

Para aumentar a segurança:

1. **Alterar porta SSH padrão**
2. **Configurar certificado SSL com Let's Encrypt**
3. **Configurar fail2ban**
4. **Usar senha forte para PostgreSQL**
5. **Configurar monitoramento de logs**

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs dos containers
2. Confirme se todas as configurações estão corretas
3. Teste a conectividade do banco de dados
4. Verifique se todas as migrações foram executadas

---

**✅ Após seguir este guia, seu sistema estará rodando em produção com banco PostgreSQL e todos os dados migrados!**
