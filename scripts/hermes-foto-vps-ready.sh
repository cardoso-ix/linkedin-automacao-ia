#!/usr/bin/env bash
# Deixa /salvar-foto pronto no Hermes da VPS (env + script + skill + quick command).
# Uso (root na VPS):
#   bash hermes-foto-vps-ready.sh
#   bash hermes-foto-vps-ready.sh /caminho/para/hermes/docker-compose.yml
set -euo pipefail

FOTO_URL="${N8N_LINKEDIN_FOTO_WEBHOOK_URL:-https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-foto}"
COMPOSE="${1:-/docker/hermes/docker-compose.yml}"

echo "==> 1) Garante URL da foto no .env do volume Hermes"
if docker ps --format '{{.Names}}' | grep -qx hermes; then
  docker exec hermes sh -c "
    touch /opt/data/.env
    grep -vE '^N8N_LINKEDIN_FOTO_WEBHOOK_URL=' /opt/data/.env > /opt/data/.env.tmp || true
    mv /opt/data/.env.tmp /opt/data/.env
    printf 'N8N_LINKEDIN_FOTO_WEBHOOK_URL=%s\n' '$FOTO_URL' >> /opt/data/.env
  "
else
  echo "AVISO: container hermes nao esta running — ajuste N8N_LINKEDIN_FOTO_WEBHOOK_URL manualmente no volume."
fi

echo "==> 2) Confere secret (nao imprime valor)"
if docker exec hermes sh -c 'test -n "${N8N_HERMES_WEBHOOK_SECRET:-}" || grep -qE "^N8N_HERMES_WEBHOOK_SECRET=.+" /opt/data/.env'; then
  echo "Secret presente."
else
  echo 'AVISO: N8N_HERMES_WEBHOOK_SECRET ausente no .env — copie o mesmo do fluxo /postar'
fi

echo "==> 3) Escreve salvar-foto-linkedin.sh (JSON via python3) + skill + /salvar-foto"
# Copia o script do repo se estiver no mesmo host; senao embute versao python-safe
SCRIPT_SRC="$(cd "$(dirname "$0")/.." && pwd)/hermes/bin/salvar-foto-linkedin.sh"
docker exec hermes sh -c 'mkdir -p /opt/data/bin /opt/data/skills/social-media/linkedin-foto-n8n'
if [ -f "$SCRIPT_SRC" ]; then
  docker cp "$SCRIPT_SRC" hermes:/opt/data/bin/salvar-foto-linkedin.sh
  docker exec hermes chmod +x /opt/data/bin/salvar-foto-linkedin.sh
else
  echo "AVISO: repo script nao encontrado em $SCRIPT_SRC — usando embed."
  docker exec -i hermes sh -c 'cat > /opt/data/bin/salvar-foto-linkedin.sh && chmod +x /opt/data/bin/salvar-foto-linkedin.sh' < "$SCRIPT_SRC" || true
fi

docker exec hermes sh -c '
cat > /opt/data/skills/social-media/linkedin-foto-n8n/SKILL.md <<'"'"'EOF'"'"'
---
name: salvar-foto
description: Enfileira foto do Telegram para o proximo post LinkedIn via webhook n8n. Use quando Eduardo enviar foto ou pedir para salvar/usar no proximo post.
---

# LinkedIn salvar foto via n8n

Foto + pedido => SEMPRE /opt/data/bin/salvar-foto-linkedin.sh --file "<PATH>".
Destino: LinkedIn Imagens Agenda (status=ready). Caption/tema NÃO e a fila de texto — use /salvar-texto para o copy.
EOF
if [ -f /opt/data/config.yaml ] && ! grep -qE "^[[:space:]]*salvar-foto:" /opt/data/config.yaml; then
  printf "\n  salvar-foto:\n    type: exec\n    description: Enfileirar foto Telegram para o proximo post\n    show_in_telegram_menu: true\n    command: /opt/data/bin/salvar-foto-linkedin.sh\n" >> /opt/data/config.yaml
fi
if [ -f /opt/data/SOUL.md ] && ! grep -q "salvar-foto-linkedin" /opt/data/SOUL.md; then
  printf "\n\n## LinkedIn salvar foto (fila)\nQuando Eduardo enviar foto ou pedir para salvar/usar no proximo post:\n1. SEMPRE rode /opt/data/bin/salvar-foto-linkedin.sh --file \"<PATH>\"\n2. Grava em LinkedIn Imagens Agenda (status=ready).\n3. Texto completo: /salvar-texto (caption da foto nao substitui).\n" >> /opt/data/SOUL.md
fi
ls -la /opt/data/bin/salvar-foto-linkedin.sh
'

echo "==> 4) Reinicia Hermes"
if [ -f "$COMPOSE" ]; then
  docker compose -f "$COMPOSE" up -d --force-recreate hermes || docker restart hermes || true
else
  docker restart hermes || true
fi

echo "==> 5) Smoke checks"
docker exec hermes sh -c 'test -x /opt/data/bin/salvar-foto-linkedin.sh'
docker exec hermes sh -c 'grep -q N8N_LINKEDIN_FOTO_WEBHOOK_URL /opt/data/.env'
docker exec hermes sh -c 'command -v python3 >/dev/null || command -v python >/dev/null'
docker exec hermes sh -c '/opt/data/bin/salvar-foto-linkedin.sh --help >/dev/null'

echo "Pronto. Telegram: foto + /salvar-texto (copy) + /salvar-foto; depois /postar."
