#!/bin/bash

# Script de Deploy Automatizado para Produção
# Sistema de Relatórios Django

set -e  # Parar em caso de erro

echo "🚀 Iniciando Deploy do Sistema de Relatórios..."
echo "================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    error "Arquivo manage.py não encontrado. Execute o script na raiz do projeto."
fi

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado. Por favor, instale o Docker primeiro."
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
fi

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    warning "Arquivo .env não encontrado. Criando a partir do template..."
    if [ -f "env.production.example" ]; then
        cp env.production.example .env
        warning "Configure o arquivo .env antes de continuar!"
        echo "Editando .env agora..."
        read -p "Pressione Enter para abrir o editor nano..."
        nano .env
    else
        error "Template env.production.example não encontrado!"
    fi
fi

log "Verificando configurações..."

# Verificar se as variáveis essenciais estão configuradas
source .env
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "sua-chave-secreta-super-segura-aqui" ]; then
    error "SECRET_KEY não está configurada no arquivo .env"
fi

if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "senha_segura_123" ]; then
    warning "POSTGRES_PASSWORD ainda está usando o valor padrão. Considere alterá-la."
fi

log "Parando containers existentes (se houver)..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

log "Construindo imagens Docker..."
docker-compose -f docker-compose.prod.yml build

log "Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

log "Aguardando PostgreSQL ficar pronto..."
sleep 30

# Verificar se o banco está funcionando
for i in {1..10}; do
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres; then
        log "PostgreSQL está pronto!"
        break
    fi
    if [ $i -eq 10 ]; then
        error "PostgreSQL não ficou pronto após 100 segundos"
    fi
    log "Aguardando PostgreSQL... tentativa $i/10"
    sleep 10
done

log "Executando migrações do banco de dados..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

log "Coletando arquivos estáticos..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Verificar se já existe um superusuário
log "Verificando superusuário..."
HAS_SUPERUSER=$(docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "
from authentication.models import User
print(User.objects.filter(is_superuser=True).exists())
" 2>/dev/null | tail -n 1)

if [ "$HAS_SUPERUSER" = "False" ]; then
    log "Criando superusuário..."
    # Tentar usar o script automático primeiro
    if [ -f "create_superuser.py" ]; then
        docker-compose -f docker-compose.prod.yml exec -T web python create_superuser.py 2>/dev/null || {
            warning "Script automático falhou. Criando superusuário manualmente..."
            docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
        }
    else
        docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
    fi
else
    log "Superusuário já existe, pulando criação..."
fi

# Executar setup inicial se disponível
if docker-compose -f docker-compose.prod.yml exec -T web python manage.py help | grep -q "setup_initial_data"; then
    log "Executando setup inicial de dados..."
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py setup_initial_data 2>/dev/null || {
        warning "Setup inicial falhou ou não é necessário"
    }
fi

log "Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

# Verificar se os serviços estão rodando
WEB_STATUS=$(docker-compose -f docker-compose.prod.yml ps web | grep -c "Up" || echo "0")
DB_STATUS=$(docker-compose -f docker-compose.prod.yml ps db | grep -c "Up" || echo "0")
NGINX_STATUS=$(docker-compose -f docker-compose.prod.yml ps nginx | grep -c "Up" || echo "0")

if [ "$WEB_STATUS" -eq 0 ]; then
    error "Container web não está rodando!"
fi

if [ "$DB_STATUS" -eq 0 ]; then
    error "Container db não está rodando!"
fi

if [ "$NGINX_STATUS" -eq 0 ]; then
    error "Container nginx não está rodando!"
fi

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "================================================"
echo -e "${BLUE}Sistema disponível em: http://$(hostname -I | awk '{print $1}')${NC}"
echo -e "${BLUE}Admin Django: http://$(hostname -I | awk '{print $1}')/admin${NC}"
echo ""
echo "📋 Comandos úteis:"
echo "  Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Status: docker-compose -f docker-compose.prod.yml ps"
echo "  Parar: docker-compose -f docker-compose.prod.yml down"
echo "  Backup DB: ./backup_db.sh (se configurado)"
echo ""
echo "⚠️  Lembre-se de:"
echo "  1. Configurar firewall (portas 22, 80, 443)"
echo "  2. Configurar backups automáticos"
echo "  3. Alterar credenciais padrão"
echo "  4. Configurar SSL para produção"
echo ""

# Criar script de backup se não existir
if [ ! -f "backup_db.sh" ]; then
    log "Criando script de backup..."
    cat > backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres relatorio_system > $BACKUP_DIR/db_backup_$DATE.sql
echo "Backup criado: $BACKUP_DIR/db_backup_$DATE.sql"
EOF
    chmod +x backup_db.sh
    log "Script de backup criado: ./backup_db.sh"
fi

echo -e "${GREEN}Deploy finalizado! ✅${NC}"
