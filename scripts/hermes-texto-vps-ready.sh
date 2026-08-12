#!/usr/bin/env bash
# Deixa /salvar-texto pronto no Hermes da VPS (env + script + skill + quick command).
# Uso (root na VPS):
#   bash hermes-texto-vps-ready.sh
#   bash hermes-texto-vps-ready.sh /caminho/para/hermes/docker-compose.yml
set -euo pipefail

TEXTO_URL="${N8N_LINKEDIN_TEXTO_WEBHOOK_URL:-https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-texto}"
COMPOSE="${1:-/docker/hermes/docker-compose.yml}"

echo "==> 1) Garante URL do texto no .env do volume Hermes"
if docker ps --format '{{.Names}}' | grep -qx hermes; then
  docker exec hermes sh -c "
    touch /opt/data/.env
    grep -vE '^N8N_LINKEDIN_TEXTO_WEBHOOK_URL=' /opt/data/.env > /opt/data/.env.tmp || true
    mv /opt/data/.env.tmp /opt/data/.env
    printf 'N8N_LINKEDIN_TEXTO_WEBHOOK_URL=%s\n' '$TEXTO_URL' >> /opt/data/.env
  "
else
  echo "AVISO: container hermes nao esta running — ajuste N8N_LINKEDIN_TEXTO_WEBHOOK_URL manualmente no volume."
fi

echo "==> 2) Confere secret (nao imprime valor)"
if docker exec hermes sh -c 'test -n "${N8N_HERMES_WEBHOOK_SECRET:-}" || grep -qE "^N8N_HERMES_WEBHOOK_SECRET=.+" /opt/data/.env'; then
  echo "Secret presente."
else
  echo 'AVISO: N8N_HERMES_WEBHOOK_SECRET ausente no .env — copie o mesmo do fluxo /postar'
fi

echo "==> 3) Escreve salvar-texto-linkedin.sh + skill + quick command /salvar-texto"
docker exec hermes sh -c '
mkdir -p /opt/data/bin /opt/data/skills/social-media/linkedin-texto-n8n
cat > /opt/data/bin/salvar-texto-linkedin.sh <<'"'"'EOF'"'"'
#!/usr/bin/env sh
set -eu
URL="${N8N_LINKEDIN_TEXTO_WEBHOOK_URL:-https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-texto}"
SECRET="${N8N_HERMES_WEBHOOK_SECRET:-}"
TEXTO=""; FILE=""; TEMA="Post Telegram"
for candidate in /opt/data/.env /data/.env; do
  if [ -f "$candidate" ]; then
    if [ -z "$SECRET" ]; then
      SECRET=$(grep -E "^N8N_HERMES_WEBHOOK_SECRET=" "$candidate" | head -1 | cut -d= -f2- || true)
    fi
    if [ -z "${N8N_LINKEDIN_TEXTO_WEBHOOK_URL:-}" ]; then
      FROM_ENV=$(grep -E "^N8N_LINKEDIN_TEXTO_WEBHOOK_URL=" "$candidate" | head -1 | cut -d= -f2- || true)
      if [ -n "$FROM_ENV" ]; then URL="$FROM_ENV"; fi
    fi
    break
  fi
done
usage() { echo "Uso: salvar-texto-linkedin.sh --texto TEXTO [--tema TEMA] | --file PATH"; }
while [ $# -gt 0 ]; do
  case "$1" in
    --texto|-x|--text) TEXTO="$2"; shift 2 ;;
    --file|-f) FILE="$2"; shift 2 ;;
    --tema|--caption|-c) TEMA="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) if [ -z "$TEXTO" ]; then TEXTO="$1"; else TEXTO="$TEXTO $1"; fi; shift ;;
  esac
done
if [ -z "$SECRET" ]; then echo "ERRO: defina N8N_HERMES_WEBHOOK_SECRET"; exit 1; fi
if [ -n "$FILE" ]; then
  if [ ! -f "$FILE" ]; then echo "ERRO: arquivo nao encontrado"; exit 1; fi
  TEXTO=$(cat "$FILE")
fi
TEXTO=$(printf "%s" "$TEXTO" | sed "s/\r$//")
if [ -z "$TEXTO" ]; then echo "ERRO: --texto ou --file"; usage; exit 1; fi
LEN=$(printf "%s" "$TEXTO" | wc -c | tr -d " ")
if [ "$LEN" -lt 50 ]; then echo "ERRO: texto curto ($LEN)"; exit 1; fi
if [ "$LEN" -gt 3000 ]; then echo "ERRO: texto longo ($LEN)"; exit 1; fi
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else echo "ERRO: python necessario"; exit 1; fi
echo "Enfileirando texto..."
RESP=$(POST_TEXT="$TEXTO" TEMA_TXT="$TEMA" "$PY" -c "import json,os; print(json.dumps({\"source\":\"hermes\",\"command\":\"salvar-texto\",\"postText\":os.environ[\"POST_TEXT\"],\"tema\":os.environ.get(\"TEMA_TXT\",\"Post Telegram\")[:200]},ensure_ascii=False,separators=(\",\",\":\")))" | curl -sS -X POST "$URL" -H "Content-Type: application/json; charset=utf-8" -H "X-Hermes-Secret: $SECRET" --data-binary @- -w "\nHTTP_CODE:%{http_code}" --max-time 30) || { echo "ERRO webhook"; exit 1; }
HTTP_CODE=$(printf "%s" "$RESP" | sed -n "s/^HTTP_CODE://p" | tail -1)
BODY=$(printf "%s" "$RESP" | sed "/^HTTP_CODE:/d")
echo "HTTP ${HTTP_CODE:-?}"
echo "$BODY"
case "${HTTP_CODE:-}" in
  200|201)
    case "$BODY" in
      *"\"ok\":true"*|*"\"ok\": true"*) echo "OK texto enfileirado."; exit 0 ;;
    esac
    ;;
esac
echo "ERRO: n8n nao confirmou."; exit 1
EOF
chmod +x /opt/data/bin/salvar-texto-linkedin.sh
cat > /opt/data/skills/social-media/linkedin-texto-n8n/SKILL.md <<'"'"'EOF'"'"'
---
name: salvar-texto
description: Salva texto validado no n8n Textos Agenda ready.
---

OBRIGATORIO: /salvar-texto ou "salva este texto" =>
/opt/data/bin/salvar-texto-linkedin.sh --texto "<TEXTO>"
Proibido inventar curl/JSON manual. Destino: LinkedIn Textos Agenda status=ready.
EOF
if [ -f /opt/data/config.yaml ] && ! grep -qE "^[[:space:]]*salvar-texto:" /opt/data/config.yaml; then
  printf "\n  salvar-texto:\n    type: exec\n    description: Enfileirar texto Telegram para o proximo post\n    show_in_telegram_menu: true\n    command: /opt/data/bin/salvar-texto-linkedin.sh\n" >> /opt/data/config.yaml
fi
if [ -f /opt/data/SOUL.md ] && ! grep -q "salvar-texto-linkedin" /opt/data/SOUL.md; then
  printf "\n\n## LinkedIn salvar texto (OBRIGATORIO)\nQuando Eduardo validar o texto e pedir salvar/enviar (/salvar-texto, salva este texto):\n1. SEMPRE rode /opt/data/bin/salvar-texto-linkedin.sh --texto \"<TEXTO>\"\n2. NUNCA invente curl/JSON manual.\n3. So confirme apos ver OK texto ready.\n" >> /opt/data/SOUL.md
fi
ls -la /opt/data/bin/salvar-texto-linkedin.sh /opt/data/skills/social-media/linkedin-texto-n8n/SKILL.md
'

echo "==> 4) Reinicia Hermes para recarregar skills/config (compose: $COMPOSE)"
if [ -f "$COMPOSE" ]; then
  docker compose -f "$COMPOSE" up -d --force-recreate hermes || docker restart hermes || true
else
  docker restart hermes || true
fi

echo "==> 5) Smoke checks"
docker exec hermes sh -c 'test -x /opt/data/bin/salvar-texto-linkedin.sh'
docker exec hermes sh -c 'grep -q N8N_LINKEDIN_TEXTO_WEBHOOK_URL /opt/data/.env'
docker exec hermes sh -c '/opt/data/bin/salvar-texto-linkedin.sh --help >/dev/null'

echo "Pronto. No Telegram: valide o texto e peca /salvar-texto; depois /salvar-foto (opcional) e /postar."
