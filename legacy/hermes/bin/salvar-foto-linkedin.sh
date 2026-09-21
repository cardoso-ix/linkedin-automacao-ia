#!/usr/bin/env sh
# Enfileira foto do Telegram no n8n (Data Table LinkedIn Imagens Agenda, status=ready).
# Uso:
#   salvar-foto-linkedin.sh --file /caminho/foto.jpg
#   salvar-foto-linkedin.sh --file foto.jpg --tema "Bastidores lab"
#   salvar-foto-linkedin.sh --base64 "...." --mime image/jpeg

set -eu

URL="${N8N_LINKEDIN_FOTO_WEBHOOK_URL:-https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-foto}"
SECRET="${N8N_HERMES_WEBHOOK_SECRET:-}"
FILE=""
B64=""
MIME="image/jpeg"
TEMA="Foto Telegram"
FILENAME="foto-linkedin.jpg"

usage() {
  echo "Uso: salvar-foto-linkedin.sh --file PATH [--tema TEXTO] | --base64 DATA [--mime TYPE] [--tema TEXTO]"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --file|-f)
      FILE="$2"
      shift 2
      ;;
    --base64|-b)
      B64="$2"
      shift 2
      ;;
    --mime|-m)
      MIME="$2"
      shift 2
      ;;
    --tema|-t|--caption|-c)
      TEMA="$2"
      shift 2
      ;;
    --filename|-n)
      FILENAME="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      if [ -z "$FILE" ] && [ -f "$1" ]; then
        FILE="$1"
      fi
      shift
      ;;
  esac
done

if [ -z "$SECRET" ]; then
  echo "ERRO: defina N8N_HERMES_WEBHOOK_SECRET no .env do Hermes."
  exit 1
fi

if [ -z "$B64" ]; then
  if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
    echo "ERRO: informe um arquivo existente com --file PATH"
    usage
    exit 1
  fi
  FILENAME=$(basename "$FILE")
  case "$FILENAME" in
    *.png|*.PNG) MIME="image/png" ;;
    *.webp|*.WEBP) MIME="image/webp" ;;
    *.gif|*.GIF) MIME="image/gif" ;;
    *) MIME="image/jpeg" ;;
  esac
  if command -v base64 >/dev/null 2>&1; then
    B64=$(base64 -w0 "$FILE" 2>/dev/null || base64 "$FILE" | tr -d '\n')
  else
    echo "ERRO: comando base64 nao encontrado."
    exit 1
  fi
fi

B64=$(printf '%s' "$B64" | tr -d '\r\n')
if [ ${#B64} -lt 100 ]; then
  echo "ERRO: imagem base64 vazia ou muito pequena."
  exit 1
fi

TMP=$(mktemp)
# JSON valido via Python (evita 422 por caption com aspas/quebra de linha)
if command -v python3 >/dev/null 2>&1; then
  IMAGE_B64="$B64" MIME_TYPE="$MIME" FILE_NAME="$FILENAME" TEMA_TXT="$TEMA" python3 - <<'PY' > "$TMP"
import json, os
print(json.dumps({
  "source": "hermes",
  "command": "salvar-foto",
  "imageBase64": os.environ["IMAGE_B64"],
  "mimeType": os.environ["MIME_TYPE"],
  "fileName": os.environ["FILE_NAME"],
  "caption": os.environ.get("TEMA_TXT", "Foto Telegram")[:200],
  "tema": os.environ.get("TEMA_TXT", "Foto Telegram")[:200],
}, ensure_ascii=False, separators=(",", ":")))
PY
elif command -v python >/dev/null 2>&1; then
  IMAGE_B64="$B64" MIME_TYPE="$MIME" FILE_NAME="$FILENAME" TEMA_TXT="$TEMA" python - <<'PY' > "$TMP"
import json, os
print(json.dumps({
  "source": "hermes",
  "command": "salvar-foto",
  "imageBase64": os.environ["IMAGE_B64"],
  "mimeType": os.environ["MIME_TYPE"],
  "fileName": os.environ["FILE_NAME"],
  "caption": os.environ.get("TEMA_TXT", "Foto Telegram")[:200],
  "tema": os.environ.get("TEMA_TXT", "Foto Telegram")[:200],
}, ensure_ascii=False, separators=(",", ":")))
PY
else
  echo "ERRO: python3/python necessario para montar JSON da foto (evita 422)."
  rm -f "$TMP"
  exit 1
fi

echo "Enfileirando foto no LinkedIn Imagens Agenda (status=ready)..."
HTTP_CODE=$(curl -sS -o /tmp/hermes-foto-resp.json -w "%{http_code}" -X POST "$URL" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "X-Hermes-Secret: $SECRET" \
  --data-binary @"$TMP" \
  --max-time 90) || {
  rm -f "$TMP"
  echo "ERRO: falha ao chamar webhook de foto."
  exit 1
}
rm -f "$TMP"
RESP=$(cat /tmp/hermes-foto-resp.json 2>/dev/null || true)
rm -f /tmp/hermes-foto-resp.json
echo "HTTP $HTTP_CODE"
echo "$RESP"

case "$HTTP_CODE" in
  200|201)
    case "$RESP" in
      *'"ok":true'*|*'\"ok\":true'*|*'\"ok\": true'*|*'"ok": true'*)
        echo "OK foto enfileirada (status=ready). Proximo /postar usa esta imagem."
        exit 0
        ;;
    esac
    ;;
esac
echo "ERRO: n8n nao confirmou o salvamento (HTTP $HTTP_CODE). Confira secret e o workflow."
exit 1
