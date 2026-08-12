#!/usr/bin/env bash
# Deixa /monitorar pronto no Hermes da VPS (env + script + skill + quick command).
# Uso (NA VPS, como root):
#   bash hermes-monitorar-vps-ready.sh
# Opcional: passar compose atualizado do repo:
#   bash hermes-monitorar-vps-ready.sh /caminho/para/hermes/docker-compose.yml
set -euo pipefail

MONITOR_URL="${N8N_LINKEDIN_MONITOR_WEBHOOK_URL:-https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-monitor}"
POST_URL_DEFAULT="https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-post"
COMPOSE_SRC="${1:-}"
COMPOSE_DST="/docker/hermes/docker-compose.yml"

echo "==> 1) Confere container hermes"
docker ps --format '{{.Names}}' | grep -qx hermes || {
  echo "ERRO: container hermes nao esta rodando"
  exit 1
}

echo "==> 2) Upsert env no volume (/opt/data/.env) sem expor secrets"
docker exec hermes sh -c "
set -e
ENV=/opt/data/.env
touch \"\$ENV\"
# remove so as chaves que vamos reescrever
grep -vE '^(N8N_LINKEDIN_MONITOR_WEBHOOK_URL|N8N_LINKEDIN_POST_WEBHOOK_URL)=' \"\$ENV\" > /tmp/hermes.env.tmp || true
mv /tmp/hermes.env.tmp \"\$ENV\"
# garante POST URL se ausente (nao sobrescreve secret existente)
if ! grep -qE '^N8N_LINKEDIN_POST_WEBHOOK_URL=' \"\$ENV\"; then
  printf 'N8N_LINKEDIN_POST_WEBHOOK_URL=%s\n' '${POST_URL_DEFAULT}' >> \"\$ENV\"
fi
printf 'N8N_LINKEDIN_MONITOR_WEBHOOK_URL=%s\n' '${MONITOR_URL}' >> \"\$ENV\"
# secret: so avisa se faltar (NAO inventa)
if ! grep -qE '^N8N_HERMES_WEBHOOK_SECRET=.+' \"\$ENV\"; then
  echo 'AVISO: N8N_HERMES_WEBHOOK_SECRET ausente no .env — copie o mesmo do fluxo /postar'
  exit 2
fi
echo 'env ok (MONITOR URL + POST URL + SECRET presente)'
# mascara: so mostra se as chaves existem
grep -E '^(N8N_LINKEDIN_MONITOR_WEBHOOK_URL|N8N_LINKEDIN_POST_WEBHOOK_URL|N8N_HERMES_WEBHOOK_SECRET)=' \"\$ENV\" | sed -E 's/(SECRET=).*/\1***redacted***/; s/(URL=).*/\1…/' 
"

echo "==> 3) Escreve monitorar-linkedin.sh + skill + quick command /monitorar"
docker exec hermes sh -c "
set -e
mkdir -p /opt/data/bin /opt/data/skills/social-media/linkedin-monitor-n8n
cat > /opt/data/bin/monitorar-linkedin.sh <<'MONEOF'
#!/usr/bin/env sh
set -eu
URL=\"\${N8N_LINKEDIN_MONITOR_WEBHOOK_URL:-}\"
SECRET=\"\${N8N_HERMES_WEBHOOK_SECRET:-}\"
POST_URL=\"\"
TEMA=\"Post manual\"
POST_TEXT=\"\"
usage() { echo \"Uso: monitorar-linkedin.sh <postUrl> [--url URL] [--tema TEXTO] [--texto TEXTO]\"; }
while [ \$# -gt 0 ]; do
  case \"\$1\" in
    --url|-u) POST_URL=\"\$2\"; shift 2 ;;
    --tema|-t) TEMA=\"\$2\"; shift 2 ;;
    --texto|-x) POST_TEXT=\"\$2\"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    http://*|https://*|urn:li:*) POST_URL=\"\$1\"; shift ;;
    *)
      case \"\$1\" in
        *linkedin.com*|*urn:li:*)
          POST_URL=\$(printf '%s' \"\$1\" | sed -n 's/.*\\(https\\{0,1\\}:\\/\\/[^[:space:]]*\\).*/\\1/p')
          if [ -z \"\$POST_URL\" ]; then
            POST_URL=\$(printf '%s' \"\$1\" | sed -n 's/.*\\(urn:li:[a-zA-Z]*:[0-9]*\\).*/\\1/p')
          fi
          ;;
      esac
      shift
      ;;
  esac
done
if [ -z \"\$URL\" ] || [ -z \"\$SECRET\" ]; then
  echo \"ERRO: defina N8N_LINKEDIN_MONITOR_WEBHOOK_URL e N8N_HERMES_WEBHOOK_SECRET no .env do Hermes.\"
  exit 1
fi
if [ -z \"\$POST_URL\" ]; then
  echo \"ERRO: informe a URL (ou URN) do post LinkedIn.\"
  usage
  exit 1
fi
json_escape() { printf '%s' \"\$1\" | sed 's/\\\\/\\\\\\\\/g; s/\"/\\\\\"/g'; }
POST_URL_ESC=\$(json_escape \"\$POST_URL\")
TEMA_ESC=\$(json_escape \"\$TEMA\")
POST_TEXT_ESC=\$(json_escape \"\$POST_TEXT\")
BODY=\$(printf '{\"source\":\"hermes\",\"command\":\"monitorar\",\"postUrl\":\"%s\",\"tema\":\"%s\",\"postText\":\"%s\"}' \
  \"\$POST_URL_ESC\" \"\$TEMA_ESC\" \"\$POST_TEXT_ESC\")
echo \"Registrando post no LinkedIn Posts Monitor...\"
RESP=\$(curl -sS -X POST \"\$URL\" \
  -H \"Content-Type: application/json\" \
  -H \"X-Hermes-Secret: \$SECRET\" \
  -d \"\$BODY\" \
  --max-time 25) || { echo \"ERRO: falha ao chamar webhook de monitor.\"; exit 1; }
echo \"\$RESP\"
case \"\$RESP\" in
  *'\"ok\":true'*|*'\\\"ok\\\":true'*|*'\\\"ok\\\": true'*|*'\"ok\": true'*) echo \"OK post registrado (status=monitoring).\"; exit 0 ;;
  *) echo \"ERRO: n8n nao confirmou o registro. Confira URL/URN e o secret.\"; exit 1 ;;
esac
MONEOF
chmod +x /opt/data/bin/monitorar-linkedin.sh
cat > /opt/data/skills/social-media/linkedin-monitor-n8n/SKILL.md <<'SKILLEOF'
---
name: monitorar
description: Registra URL/URN de post LinkedIn (manual) na Data Table LinkedIn Posts Monitor via webhook n8n. Use quando Eduardo colar o link do post ou pedir para monitorar/acompanhar comentarios.
---

# LinkedIn monitorar via n8n

## Regra obrigatoria
Post manual + link/pedido de monitorar => SEMPRE rode /opt/data/bin/monitorar-linkedin.sh \"<URL>\".
Destino: LinkedIn Posts Monitor (status=monitoring). Nunca so confirme no chat.

## Quando usar
/monitorar <url>, \"monitora este post\", \"acompanha os comentarios\", \"salva o link\", URL linkedin.com/posts|feed/update.

## Quando NAO usar
/postar ou /postar-texto (o workflow de post ja grava no Monitor).

## Execucao
1. Extraia a URL/URN.
2. /opt/data/bin/monitorar-linkedin.sh \"<URL>\"
3. Responda so com o resultado. Nao exponha o secret.
SKILLEOF
# quick command
if [ -f /opt/data/config.yaml ] && ! grep -qE '^[[:space:]]*monitorar:' /opt/data/config.yaml; then
  printf '\n  monitorar:\n    type: exec\n    description: Registrar URL LinkedIn no Posts Monitor\n    show_in_telegram_menu: true\n    command: /opt/data/bin/monitorar-linkedin.sh\n' >> /opt/data/config.yaml
fi
if [ -f /opt/data/SOUL.md ] && ! grep -q 'monitorar-linkedin' /opt/data/SOUL.md; then
  printf '\n\n## LinkedIn monitorar (post manual)\nQuando Eduardo colar URL do LinkedIn ou pedir para monitorar/acompanhar comentarios:\n1. SEMPRE rode /opt/data/bin/monitorar-linkedin.sh \"<URL>\"\n2. Isso grava na Data Table LinkedIn Posts Monitor (status=monitoring).\n3. Nao so confirme no chat — sem a linha o reply automatico nao cobre o post.\n4. /postar ja grava no Monitor; nao rode monitorar depois de postar via n8n.\n' >> /opt/data/SOUL.md
fi
echo 'script+skill+config ok'
ls -la /opt/data/bin/monitorar-linkedin.sh /opt/data/skills/social-media/linkedin-monitor-n8n/SKILL.md
"

if [ -n "$COMPOSE_SRC" ] && [ -f "$COMPOSE_SRC" ]; then
  echo "==> 4) Atualiza compose em $COMPOSE_DST e recria"
  cp "$COMPOSE_DST" "${COMPOSE_DST}.bak.$(date +%s)" 2>/dev/null || true
  cp "$COMPOSE_SRC" "$COMPOSE_DST"
  cd /docker/hermes
  docker compose up -d --force-recreate
else
  echo "==> 4) Reinicia hermes para recarregar .env/config"
  docker restart hermes
fi

echo "==> 5) Smoke estrutural (sem registrar post real)"
docker exec hermes sh -c '
set -e
test -x /opt/data/bin/monitorar-linkedin.sh
grep -q N8N_LINKEDIN_MONITOR_WEBHOOK_URL /opt/data/.env
grep -q N8N_HERMES_WEBHOOK_SECRET /opt/data/.env
# dry: ajuda/erro de URL ausente (nao chama n8n)
/opt/data/bin/monitorar-linkedin.sh --help >/dev/null
echo smoke_ok
'

echo "Pronto. No Telegram: /monitorar <url-do-post-linkedin>"
