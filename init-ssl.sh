#!/bin/bash
# init-ssl.sh - Initial SSL certificate acquisition for macroglance.com
# Run this script ONCE on first deployment to obtain Let's Encrypt certificates

set -e

DOMAIN="macroglance.com"
EMAIL="alex58020@gmail.com"
DATA_PATH="/data/certbot"

echo "=== SSL Certificate Setup for $DOMAIN ==="

# Create required directories
echo "Creating directories..."
mkdir -p "$DATA_PATH/conf"
mkdir -p "$DATA_PATH/www"

# Download recommended TLS parameters
if [ ! -e "$DATA_PATH/conf/options-ssl-nginx.conf" ]; then
    echo "Downloading recommended TLS parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"
fi

# Create a temporary self-signed certificate so nginx can start
echo "Creating temporary self-signed certificate..."
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
if [ ! -e "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" ]; then
    openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
        -keyout "$DATA_PATH/conf/live/$DOMAIN/privkey.pem" \
        -out "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" \
        -subj "/CN=localhost"
fi

echo "Starting nginx..."
docker compose up -d nginx

echo "Waiting for nginx to be ready..."
sleep 5

# Delete temporary certificate
echo "Removing temporary certificate..."
rm -rf "$DATA_PATH/conf/live/$DOMAIN"

# Build email argument (use --register-unsafely-without-email if no email provided)
if [ -n "$EMAIL" ]; then
    EMAIL_ARG="--email $EMAIL"
else
    EMAIL_ARG="--register-unsafely-without-email"
fi

# Request real certificate from Let's Encrypt
echo "Requesting Let's Encrypt certificate for $DOMAIN..."
docker compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    $EMAIL_ARG \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "Reloading nginx with new certificate..."
docker compose exec nginx nginx -s reload

echo ""
echo "=== SUCCESS ==="
echo "SSL certificate obtained for $DOMAIN"
echo "Certificate will auto-renew via the certbot container."
echo ""
echo "Next steps:"
echo "1. Test HTTPS: https://$DOMAIN"
echo "2. Run 'docker compose up -d' to start all services"
