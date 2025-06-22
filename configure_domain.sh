#!/bin/bash

# Script para configurar domínio no sistema
DOMAIN="app.devaxis.com.br"
SERVER_IP="31.97.168.137"

echo "=== Configurando domínio: $DOMAIN ==="

# 1. Atualizar nginx.conf
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=web:10m rate=10r/s;
    
    upstream app {
        server web:8000;
    }
    
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name app.devaxis.com.br;
        
        # Let's Encrypt challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Redirect all HTTP requests to HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name app.devaxis.com.br;
        
        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/app.devaxis.com.br/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/app.devaxis.com.br/privkey.pem;
        
        # SSL Security
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Rate limiting
        limit_req zone=web burst=20 nodelay;
        
        # Static files
        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
        
        location /media/ {
            alias /app/media/;
            expires 30d;
            add_header Cache-Control "public";
        }
        
        # Django app
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
EOF

# 2. Atualizar docker-compose.prod.yml para incluir Certbot
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-relatorio_system}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 --workers 3 relatorio_system.wsgi:application
    volumes:
      - media_volume:/app/media
      - static_volume:/app/staticfiles
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DEBUG=0
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-app.devaxis.com.br,localhost,127.0.0.1}
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres123}@db:5432/${POSTGRES_DB:-relatorio_system}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - media_volume:/app/media
      - static_volume:/app/staticfiles
      - certbot_conf:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    depends_on:
      - web
    restart: unless-stopped

  certbot:
    image: certbot/certbot
    volumes:
      - certbot_conf:/etc/letsencrypt
      - certbot_www:/var/www/certbot
    command: echo "Certbot ready for SSL certificates"

volumes:
  postgres_data:
  redis_data:
  media_volume:
  static_volume:
  certbot_conf:
  certbot_www:
EOF

# 3. Atualizar .env
sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=app.devaxis.com.br,localhost,127.0.0.1/' .env

echo "=== Configuração atualizada! ==="
echo "1. DNS: Adicione registro A: app -> 31.97.168.137"
echo "2. Aguarde propagação DNS (5-15 minutos)"
echo "3. Execute: docker-compose -f docker-compose.prod.yml up -d"
echo "4. Configure SSL: ./setup_ssl.sh" 