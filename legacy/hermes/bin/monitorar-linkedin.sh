#!/usr/bin/env sh
# Registra post LinkedIn (manual ou colado) no Posts Monitor via webhook n8n.
# Uso:
#   monitorar-linkedin.sh "https://www.linkedin.com/posts/..."
#   monitorar-linkedin.sh --url "https://www.linkedin.com/feed/update/urn:li:activity:123"
#   monitorar-linkedin.sh --url URL --tema "Post manual" --texto "resumo opcional"

set -eu

URL="${N8N_LINKEDIN_MONITOR_WEBHOOK_URL:-}"
SECRET="${N8N_HERMES_WEBHOOK_SECRET:-}"
POST_URL=""
TEMA="Post manual"
POST_TEXT=""

usage() {
  echo "Uso: monitorar-linkedin.sh <postUrl> [--url URL] [--tema TEXTO] [--texto TEXTO]"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --url|-u)
      POST_URL="$2"
      shift 2
      ;;
    --tema|-t)
      TEMA="$2"
      shift 2
      ;;
    --texto|-x)
      POST_TEXT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    http://*|https://*|urn:li:*)
      POST_URL="$1"
      shift
      ;;
    *)
      # aceita frase com URL embutida
      case "$1" in
        *linkedin.com*|*urn:li:*)
          POST_URL=$(printf '%s' "$1" | sed -n 's/.*\(https\{0,1\}:\/\/[^[:space:]]*\).*/\1/p')
          if [ -z "$POST_URL" ]; then
            POST_URL=$(printf '%s' "$1" | sed -n 's/.*\(urn:li:[a-zA-Z]*:[0-9]*\).*/\1/p')
          fi
          ;;
      esac
      shift
      ;;
  esac
done

if [ -z "$URL" ] || [ -z "$SECRET" ]; then
  echo "ERRO: defina N8N_LINKEDIN_MONITOR_WEBHOOK_URL e N8N_HERMES_WEBHOOK_SECRET no .env do Hermes."
  exit 1
fi

if [ -z "$POST_URL" ]; then
  echo "ERRO: informe a URL (ou URN) do post LinkedIn."
  usage
  exit 1
fi

# Escapa JSON simples (aspas e barras)
json_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

POST_URL_ESC=$(json_escape "$POST_URL")
TEMA_ESC=$(json_escape "$TEMA")
POST_TEXT_ESC=$(json_escape "$POST_TEXT")

BODY=$(printf '{"source":"hermes","command":"monitorar","postUrl":"%s","tema":"%s","postText":"%s"}' \
  "$POST_URL_ESC" "$TEMA_ESC" "$POST_TEXT_ESC")

echo "Registrando post no LinkedIn Posts Monitor..."
RESP=$(curl -sS -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Hermes-Secret: $SECRET" \
  -d "$BODY" \
  --max-time 25) || {
  echo "ERRO: falha ao chamar webhook de monitor."
  exit 1
}

echo "$RESP"
case "$RESP" in
  *'"ok":true'*|*'\"ok\":true'*|*'\"ok\": true'*|*'"ok": true'*)
    echo "OK post registrado (status=monitoring)."
    exit 0
    ;;
  *)
    echo "ERRO: n8n nao confirmou o registro. Confira URL/URN e o secret."
    exit 1
    ;;
esac
