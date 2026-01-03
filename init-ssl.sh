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
mkdir -p "$DATA_PATH/www/.well-known/acme-challenge"

# Clean any stale certbot state that might cause issues
echo "Cleaning any stale certbot configuration..."
rm -rf "$DATA_PATH/conf/live/$DOMAIN"
rm -rf "$DATA_PATH/conf/archive/$DOMAIN"
rm -rf "$DATA_PATH/conf/renewal/$DOMAIN.conf"

# Download recommended TLS parameters
if [ ! -e "$DATA_PATH/conf/options-ssl-nginx.conf" ]; then
    echo "Downloading recommended TLS parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"
fi

# Create a temporary self-signed certificate so nginx can start
echo "Creating temporary self-signed certificate..."
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout "$DATA_PATH/conf/live/$DOMAIN/privkey.pem" \
    -out "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=localhost" 2>/dev/null

echo "Starting nginx..."
docker compose up -d nginx

echo "Waiting for nginx to be ready..."
sleep 5

# Test if ACME challenge path is accessible
echo "Testing ACME challenge path..."
echo "test" > "$DATA_PATH/www/.well-known/acme-challenge/test"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/.well-known/acme-challenge/test" || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ ACME challenge path is accessible"
else
    echo "✗ WARNING: ACME challenge path returned HTTP $HTTP_CODE"
    echo "  Make sure DNS is pointing to this server and port 80 is open"
fi
rm -f "$DATA_PATH/www/.well-known/acme-challenge/test"

# Build email argument
if [ -n "$EMAIL" ]; then
    EMAIL_ARG="--email $EMAIL"
else
    EMAIL_ARG="--register-unsafely-without-email"
fi

# Request real certificate from Let's Encrypt
echo ""
echo "Requesting Let's Encrypt certificate for $DOMAIN..."
echo "Running: certbot certonly --webroot -w /var/www/certbot -d $DOMAIN -d www.$DOMAIN"
echo ""

# Remove the temporary certificate before requesting the real one
# (certbot needs the directory to not exist)
rm -rf "$DATA_PATH/conf/live/$DOMAIN"
rm -rf "$DATA_PATH/conf/archive/$DOMAIN"
rm -rf "$DATA_PATH/conf/renewal/$DOMAIN.conf"

docker compose run --rm --entrypoint "" certbot \
    certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    $EMAIL_ARG \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    -v \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo ""
echo "Reloading nginx with new certificate..."
docker compose exec nginx nginx -s reload

echo ""
echo "=== SUCCESS ==="
echo "SSL certificate obtained for $DOMAIN"
echo "Certificate will auto-renew via the certbot container."
echo ""
echo "Next steps:"
echo "1. Test HTTPS: https://www.$DOMAIN"
echo "2. Run 'docker compose up -d' to start all services"
