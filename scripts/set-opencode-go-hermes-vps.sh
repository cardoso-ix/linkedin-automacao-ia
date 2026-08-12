#!/usr/bin/env bash
# Atualiza OPENCODE_GO_API_KEY no Hermes (VPS) sem ecoar a chave.
# Uso (console root Hostinger / SSH):
#   export OPENCODE_GO_API_KEY='cole-a-chave-aqui'
#   bash scripts/set-opencode-go-hermes-vps.sh
set -euo pipefail
: "${OPENCODE_GO_API_KEY:?defina OPENCODE_GO_API_KEY}"
BASE_URL="${OPENCODE_GO_BASE_URL:-https://opencode.ai/zen/go/v1}"
KEY_LEN=${#OPENCODE_GO_API_KEY}
echo "==> OpenCode Go key len=$KEY_LEN base=$BASE_URL"

docker ps --format '{{.Names}}' | grep -qx hermes || {
  echo "ERRO: container hermes nao esta rodando"
  exit 1
}

docker exec -e KEY="$OPENCODE_GO_API_KEY" -e BASE_URL="$BASE_URL" hermes sh -c '
set -e
ENV=/opt/data/.env
CFG=/opt/data/config.yaml
touch "$ENV"
grep -vE "^#?[[:space:]]*(OPENCODE_GO_API_KEY|OPENCODE_GO_BASE_URL)=" "$ENV" > /tmp/h.env.tmp || true
mv /tmp/h.env.tmp "$ENV"
printf "OPENCODE_GO_API_KEY=%s\n" "$KEY" >> "$ENV"
printf "OPENCODE_GO_BASE_URL=%s\n" "$BASE_URL" >> "$ENV"
python3 -c "import re; t=open(\"/opt/data/.env\").read(); m=re.search(r\"^OPENCODE_GO_API_KEY=(.*)$\", t, re.M); print(\"hermes_opencode_go_len\", len(m.group(1)) if m else 0)"
if [ -f "$CFG" ]; then
  sed -i "s/provider:[[:space:]]*openrouter/provider: opencode-go/" "$CFG" || true
  sed -i "s/provider:[[:space:]]*opencode-zen/provider: opencode-go/" "$CFG" || true
  sed -i "s/provider:[[:space:]]*nous/provider: opencode-go/" "$CFG" || true
  if grep -qE "^[[:space:]]*provider:" "$CFG"; then
    sed -i "s/^[[:space:]]*provider:.*/  provider: opencode-go/" "$CFG" || true
  fi
  if grep -qE "^[[:space:]]*default:" "$CFG"; then
    sed -i "s|^[[:space:]]*default:.*|  default: deepseek-v4-flash|" "$CFG" || true
  fi
  if grep -qE "^[[:space:]]*base_url:" "$CFG"; then
    sed -i "s|^[[:space:]]*base_url:.*|  base_url: https://opencode.ai/zen/go/v1|" "$CFG" || true
  else
    printf "  base_url: https://opencode.ai/zen/go/v1\n" >> "$CFG"
  fi
  echo "config.yaml provider -> opencode-go"
fi
'

for f in /docker/hermes/.env /opt/hermes/.env; do
  if [ -f "$f" ]; then
    grep -vE '^#?[[:space:]]*(OPENCODE_GO_API_KEY|OPENCODE_GO_BASE_URL|HERMES_INFERENCE_PROVIDER|HERMES_MODEL)=' "$f" > /tmp/h2.env.tmp || true
    mv /tmp/h2.env.tmp "$f"
    printf 'OPENCODE_GO_API_KEY=%s\n' "$OPENCODE_GO_API_KEY" >> "$f"
    printf 'OPENCODE_GO_BASE_URL=%s\n' "$BASE_URL" >> "$f"
    printf 'HERMES_INFERENCE_PROVIDER=opencode-go\n' >> "$f"
    printf 'HERMES_MODEL=deepseek-v4-flash\n' >> "$f"
    echo "updated $f"
  fi
done

docker restart hermes
sleep 2
docker ps --filter name=hermes --format '{{.Names}} {{.Status}}'
echo "Pronto. n8n: credencial OpenAI account = chave OpenCode Go; nos LLM usam baseURL https://opencode.ai/zen/go/v1"
