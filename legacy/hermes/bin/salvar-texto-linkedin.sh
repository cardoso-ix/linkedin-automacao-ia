#!/usr/bin/env sh
# Enfileira texto validado no Telegram no n8n (LinkedIn Textos Agenda, status=ready).
set -eu

URL="${N8N_LINKEDIN_TEXTO_WEBHOOK_URL:-https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-texto}"
SECRET="${N8N_HERMES_WEBHOOK_SECRET:-}"
TEXTO=""
FILE=""
TEMA="Post Telegram"
ENV_FILE=""

usage() {
  echo "Uso: salvar-texto-linkedin.sh --texto TEXTO [--tema TEMA] | --file PATH [--tema TEMA]"
}

# Carrega secret/URL do .env do volume se o processo nao exportou as vars
for candidate in /opt/data/.env /data/.env; do
  if [ -f "$candidate" ]; then
    ENV_FILE="$candidate"
    break
  fi
done
if [ -n "$ENV_FILE" ]; then
  if [ -z "$SECRET" ]; then
    SECRET=$(grep -E '^N8N_HERMES_WEBHOOK_SECRET=' "$ENV_FILE" | head -1 | cut -d= -f2- || true)
  fi
  if [ -z "${N8N_LINKEDIN_TEXTO_WEBHOOK_URL:-}" ]; then
    FROM_ENV=$(grep -E '^N8N_LINKEDIN_TEXTO_WEBHOOK_URL=' "$ENV_FILE" | head -1 | cut -d= -f2- || true)
    if [ -n "$FROM_ENV" ]; then
      URL="$FROM_ENV"
    fi
  fi
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --texto|-x|--text)
      TEXTO="$2"
      shift 2
      ;;
    --file|-f)
      FILE="$2"
      shift 2
      ;;
    --tema|--caption|-c)
      TEMA="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      if [ -z "$TEXTO" ]; then TEXTO="$1"; else TEXTO="$TEXTO $1"; fi
      shift
      ;;
  esac
done

if [ -z "$SECRET" ]; then
  echo "ERRO: defina N8N_HERMES_WEBHOOK_SECRET no .env do Hermes."
  exit 1
fi

if [ -n "$FILE" ]; then
  if [ ! -f "$FILE" ]; then
    echo "ERRO: arquivo nao encontrado: $FILE"
    exit 1
  fi
  TEXTO=$(cat "$FILE")
fi

TEXTO=$(printf '%s' "$TEXTO" | sed 's/\r$//')
if [ -z "$TEXTO" ]; then
  echo "ERRO: informe o texto com --texto ou --file"
  usage
  exit 1
fi

LEN=$(printf '%s' "$TEXTO" | wc -c | tr -d ' ')
if [ "$LEN" -lt 50 ]; then
  echo "ERRO: texto muito curto ($LEN chars; minimo 50)."
  exit 1
fi
if [ "$LEN" -gt 3000 ]; then
  echo "ERRO: texto muito longo ($LEN chars; maximo 3000)."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  echo "ERRO: python3/python necessario para montar JSON do texto."
  exit 1
fi

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

echo "Enfileirando texto no LinkedIn Textos Agenda (status=ready)..."
# Pipe JSON direto no curl (evita --data-binary @arquivo quebrado)
RESP=$(
  POST_TEXT="$TEXTO" TEMA_TXT="$TEMA" "$PY" -c \
    'import json,os; print(json.dumps({"source":"hermes","command":"salvar-texto","postText":os.environ["POST_TEXT"],"tema":os.environ.get("TEMA_TXT","Post Telegram")[:200]},ensure_ascii=False,separators=(",",":")))' \
  | curl -sS -X POST "$URL" \
      -H "Content-Type: application/json; charset=utf-8" \
      -H "X-Hermes-Secret: $SECRET" \
      --data-binary @- \
      -w "\nHTTP_CODE:%{http_code}" \
      --max-time 30
) || {
  echo "ERRO: falha ao chamar webhook de texto."
  exit 1
}

HTTP_CODE=$(printf '%s' "$RESP" | sed -n 's/^HTTP_CODE://p' | tail -1)
BODY=$(printf '%s' "$RESP" | sed '/^HTTP_CODE:/d')
echo "HTTP ${HTTP_CODE:-?}"
echo "$BODY"

case "${HTTP_CODE:-}" in
  200|201)
    case "$BODY" in
      *'"ok":true'*|*'"ok": true'*)
        echo "OK texto enfileirado (status=ready). Proximo /postar usa este texto."
        exit 0
        ;;
    esac
    ;;
esac
echo "ERRO: n8n nao confirmou o salvamento (HTTP ${HTTP_CODE:-?})."
exit 1
