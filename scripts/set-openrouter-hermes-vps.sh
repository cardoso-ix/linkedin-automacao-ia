#!/usr/bin/env bash
# Atualiza OPENROUTER_API_KEY no Hermes (VPS) sem ecoar a chave.
# Uso (console root Hostinger):
#   export OPENROUTER_API_KEY='cole-a-chave-aqui'
#   bash scripts/set-openrouter-hermes-vps.sh
set -euo pipefail
: "${OPENROUTER_API_KEY:?defina OPENROUTER_API_KEY}"
KEY_LEN=${#OPENROUTER_API_KEY}
echo "==> OpenRouter key len=$KEY_LEN"

docker ps --format '{{.Names}}' | grep -qx hermes || {
  echo "ERRO: container hermes nao esta rodando"
  exit 1
}

docker exec -e KEY="$OPENROUTER_API_KEY" hermes sh -c '
set -e
ENV=/opt/data/.env
touch "$ENV"
grep -vE "^#?[[:space:]]*OPENROUTER_API_KEY=" "$ENV" > /tmp/h.env.tmp || true
mv /tmp/h.env.tmp "$ENV"
printf "OPENROUTER_API_KEY=%s\n" "$KEY" >> "$ENV"
python3 -c "import re; t=open(\"/opt/data/.env\").read(); m=re.search(r\"^OPENROUTER_API_KEY=(.*)$\", t, re.M); print(\"hermes_openrouter_len\", len(m.group(1)) if m else 0)"
'

for f in /docker/hermes/.env /opt/hermes/.env; do
  if [ -f "$f" ]; then
    grep -vE '^#?[[:space:]]*OPENROUTER_API_KEY=' "$f" > /tmp/h2.env.tmp || true
    mv /tmp/h2.env.tmp "$f"
    printf 'OPENROUTER_API_KEY=%s\n' "$OPENROUTER_API_KEY" >> "$f"
    echo "updated $f"
  fi
done

docker restart hermes
sleep 2
docker ps --filter name=hermes --format '{{.Names}} {{.Status}}'
echo "Pronto. N8n: atualize a credential OpenRouter account na UI (API Key)."
