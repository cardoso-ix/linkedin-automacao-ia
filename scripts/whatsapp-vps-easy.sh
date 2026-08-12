#!/usr/bin/env bash
# Caminho fácil: liga WhatsApp Cloud no Hermes da VPS (token do wizard).
# Uso (NA VPS, como root):
#   export WHATSAPP_CLOUD_ACCESS_TOKEN='...'
#   export WHATSAPP_CLOUD_APP_SECRET='...'
#   export WHATSAPP_CLOUD_VERIFY_TOKEN='...'
#   export WHATSAPP_CLOUD_ALLOWED_USERS='55DDD9XXXXXXXX'
#   bash whatsapp-vps-easy.sh
set -euo pipefail

PHONE_ID="${WHATSAPP_CLOUD_PHONE_NUMBER_ID:-1164738343399026}"
APP_ID="${WHATSAPP_CLOUD_APP_ID:-2842287619460178}"
WABA_ID="${WHATSAPP_CLOUD_WABA_ID:-1318156490102575}"
ACCESS_TOKEN="${WHATSAPP_CLOUD_ACCESS_TOKEN:?defina WHATSAPP_CLOUD_ACCESS_TOKEN}"
APP_SECRET="${WHATSAPP_CLOUD_APP_SECRET:?defina WHATSAPP_CLOUD_APP_SECRET}"
VERIFY_TOKEN="${WHATSAPP_CLOUD_VERIFY_TOKEN:?defina WHATSAPP_CLOUD_VERIFY_TOKEN}"
ALLOWED="${WHATSAPP_CLOUD_ALLOWED_USERS:?defina WHATSAPP_CLOUD_ALLOWED_USERS}"

COMPOSE="/docker/hermes/docker-compose.yml"
CADDY="/opt/n8n/Caddyfile"

echo "==> 1) Porta 8090 no compose Hermes"
if ! grep -q '8090:8090' "$COMPOSE"; then
  # Insere após a linha 8642
  sed -i 's|"127.0.0.1:8642:8642"|"127.0.0.1:8642:8642"\n      - "127.0.0.1:8090:8090"|' "$COMPOSE"
  echo "porta 8090 adicionada"
else
  echo "porta 8090 já existe"
fi

echo "==> 2) Vars no .env do volume Hermes"
docker exec hermes sh -c "
set -e
ENV=/opt/data/.env
touch \"\$ENV\"
# remove chaves antigas WHATSAPP_CLOUD_
grep -vE '^WHATSAPP_CLOUD_' \"\$ENV\" > /tmp/hermes.env.tmp || true
mv /tmp/hermes.env.tmp \"\$ENV\"
cat >> \"\$ENV\" <<EOF
WHATSAPP_CLOUD_PHONE_NUMBER_ID=${PHONE_ID}
WHATSAPP_CLOUD_APP_ID=${APP_ID}
WHATSAPP_CLOUD_WABA_ID=${WABA_ID}
WHATSAPP_CLOUD_ACCESS_TOKEN=${ACCESS_TOKEN}
WHATSAPP_CLOUD_APP_SECRET=${APP_SECRET}
WHATSAPP_CLOUD_VERIFY_TOKEN=${VERIFY_TOKEN}
WHATSAPP_CLOUD_ALLOWED_USERS=${ALLOWED}
WHATSAPP_CLOUD_WEBHOOK_PORT=8090
WHATSAPP_CLOUD_WEBHOOK_PATH=/whatsapp/webhook
EOF
echo 'env atualizado (secrets omitidos no log)'
"

echo "==> 3) Caddy: proxy /whatsapp/* -> Hermes 8090"
if ! grep -q 'whatsapp' "$CADDY"; then
  # Insere handle antes do reverse_proxy do n8n, se possível; senão append no site
  if grep -q 'reverse_proxy' "$CADDY"; then
    # Bloco simples no início do site (primeira linha que começa com hostname ou :)
    cp "$CADDY" "${CADDY}.bak.$(date +%s)"
    # Adiciona após a linha de abertura do site (primeira linha não vazia típica)
    awk '
      BEGIN{done=0}
      /^[a-zA-Z0-9].*\{/ && done==0 {
        print
        print "  handle /whatsapp/* {"
        print "    reverse_proxy 127.0.0.1:8090"
        print "  }"
        done=1
        next
      }
      {print}
    ' "$CADDY" > /tmp/Caddyfile.new && mv /tmp/Caddyfile.new "$CADDY"
    echo "Caddy atualizado (backup .bak.*)"
  else
    echo "ERRO: Caddyfile sem reverse_proxy — edite manualmente"
    exit 1
  fi
else
  echo "Caddy já menciona whatsapp"
fi

echo "==> 4) Recriar Hermes + reload Caddy"
cd /docker/hermes
docker compose up -d
docker exec n8n-caddy-1 caddy reload --config /etc/caddy/Caddyfile 2>/dev/null \
  || docker restart n8n-caddy-1

sleep 3
echo "==> 5) Health local"
curl -sS -m 5 http://127.0.0.1:8090/health || echo "(health ainda subindo — confira logs: docker logs hermes --tail 50)"

echo
echo "Pronto. No Meta:"
echo "  Callback URL: https://srv1897392.hstgr.cloud/whatsapp/webhook"
echo "  Verify Token: (o mesmo WHATSAPP_CLOUD_VERIFY_TOKEN)"
echo "  Subscribe: messages"
echo "Depois: mande oi no WhatsApp Business e /postar-texto"
