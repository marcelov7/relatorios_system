#!/bin/bash

DOMAIN="app.devaxis.com.br"
EMAIL="contato@devaxis.com.br"  # Altere para seu email

echo "=== Configurando SSL para $DOMAIN ==="

# 1. Primeiro, configurar nginx temporário (sem SSL)
cat > nginx_temp.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    upstream app {
        server web:8000;
    }
    
    server {
        listen 80;
        server_name app.devaxis.com.br;
        
        # Let's Encrypt challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Temporário: servir aplicação via HTTP
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# 2. Subir com nginx temporário
echo "Subindo serviços com configuração temporária..."
cp nginx_temp.conf nginx.conf
docker-compose -f docker-compose.prod.yml up -d

# 3. Aguardar nginx subir
echo "Aguardando nginx inicializar..."
sleep 10

# 4. Obter certificado SSL
echo "Obtendo certificado SSL..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# 5. Verificar se certificado foi criado
if [ -d "/var/lib/docker/volumes/relatorios_system_certbot_conf/_data/live/$DOMAIN" ]; then
    echo "✅ Certificado SSL obtido com sucesso!"
    
    # 6. Aplicar configuração final do nginx (com SSL)
    echo "Aplicando configuração final com SSL..."
    
    # Executar o script de configuração de domínio
    bash configure_domain.sh
    
    # Reiniciar nginx com SSL
    docker-compose -f docker-compose.prod.yml restart nginx
    
    echo "🎉 SSL configurado com sucesso!"
    echo "✅ Site disponível em: https://$DOMAIN"
    
else
    echo "❌ Erro ao obter certificado SSL"
    echo "Verifique se:"
    echo "1. DNS está propagado: nslookup $DOMAIN"
    echo "2. Domínio aponta para o servidor: ping $DOMAIN"
    echo "3. Porta 80 está acessível"
fi

# 7. Configurar renovação automática
echo "Configurando renovação automática..."
cat > renew_ssl.sh << 'EOF'
#!/bin/bash
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
EOF

chmod +x renew_ssl.sh

# Adicionar ao crontab (renovar a cada 3 meses)
(crontab -l 2>/dev/null; echo "0 0 1 */3 * cd /opt/relatorios_system && ./renew_ssl.sh") | crontab -

echo "=== Configuração SSL completa! ==="
echo "📝 Para renovar manualmente: ./renew_ssl.sh"
echo "🔄 Renovação automática: configurada no crontab"

# Limpeza
rm nginx_temp.conf 