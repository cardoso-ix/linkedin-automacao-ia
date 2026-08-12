# WhatsApp permanente na VPS (Telegram + WhatsApp = mesmo Hermes)

Objetivo: **um único Hermes na VPS** entende Telegram e WhatsApp Cloud, com a mesma skill LinkedIn (`/postar`, `/postar-texto`).

```
Telegram  ──┐
            ├──► Hermes (VPS Docker) ──► n8n ──► LinkedIn
WhatsApp ───┘         ▲
                      │ webhook HTTPS /whatsapp/webhook
                      └── Meta Cloud API (token permanente)
```

Na VPS o stack está em:

| Item | Valor real |
|------|------------|
| Compose Hermes | `/docker/hermes/docker-compose.yml` |
| Container | `hermes` (porta hoje só `127.0.0.1:8642`) |
| n8n + Caddy | `/opt/n8n/` (HTTPS em `srv1897392.hstgr.cloud`) |

**Não** use o Hermes do Windows como produção. O PC fica só para teste; a VPS é a fonte da verdade.

IDs do app Charizard:

| Campo | Valor |
|-------|--------|
| App ID | `2842287619460178` |
| Business ID | `196300121382596` |
| Phone Number ID | `1164738343399026` |
| WABA ID | `1318156490102575` |
| VPS | `srv1897392.hstgr.cloud` · VM `1897392` |

Guia completo Meta: [WHATSAPP-CLOUD-API.md](WHATSAPP-CLOUD-API.md)

---

## Parte A — Token permanente (System User)

Você faz no Meta (eu não vejo a senha do Facebook).

1. Abra [System users](https://business.facebook.com/latest/settings/system_users).
2. **Add** → nome `hermes-vps` → role **Admin**.
3. No usuário → **Assign assets**:
   - App **Charizard** (`2842287619460178`) → **Full control** / Manage app
   - Conta WhatsApp (WABA `1318156490102575`) → **Full control** / Manage WhatsApp Business Accounts
4. **Generate token**:
   - App: Charizard
   - Permissões:
     - `business_management`
     - `whatsapp_business_messaging`
     - `whatsapp_business_management`
   - Expiração: **Never** (ou máximo)
5. Copie o token (`EAA…`) **uma vez** → cole **só** na VPS (Parte B).  
   **Não cole no chat nem no GitHub.**

Doc: [Hermes permanent token](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud#permanent-token-production)

---

## Parte B — `.env` na VPS (Hermes)

SSH:

```bash
ssh root@srv1897392.hstgr.cloud
# achar compose / volume do Hermes
docker ps --format '{{.Names}}' | grep -i hermes
```

Edite o `.env` **dentro do volume** do container (caminho típico):

```bash
docker exec -it hermes sh -c 'grep -E "^WHATSAPP_CLOUD_|^TELEGRAM_|^N8N_" /opt/data/.env | sed -E "s/(TOKEN|SECRET|KEY)=.*/\1=<set>/"'
```

Acrescente ou atualize (valores secretos você cola no servidor):

```bash
# IDs (públicos)
WHATSAPP_CLOUD_PHONE_NUMBER_ID=1164738343399026
WHATSAPP_CLOUD_WABA_ID=1318156490102575
WHATSAPP_CLOUD_APP_ID=2842287619460178

# Secrets (colar na VPS, não no Git)
WHATSAPP_CLOUD_ACCESS_TOKEN=EAA...permanent...
WHATSAPP_CLOUD_APP_SECRET=...mesmo_do_Settings_Basic...
WHATSAPP_CLOUD_VERIFY_TOKEN=...mesmo_que_vai_no_Meta_webhook...

# Allowlist: SEU celular, DDI sem +
WHATSAPP_CLOUD_ALLOWED_USERS=55DDD9XXXXXXXX

# Webhook
WHATSAPP_CLOUD_WEBHOOK_PORT=8090
WHATSAPP_CLOUD_WEBHOOK_PATH=/whatsapp/webhook
```

App Secret: [Settings → Basic](https://developers.facebook.com/apps/2842287619460178/settings/basic/?business_id=196300121382596)

Reinicie:

```bash
docker restart hermes
# ou: cd /opt/hermes && docker compose up -d
```

Confirme health **na VPS**:

```bash
curl -sS http://127.0.0.1:8090/health
# espere verify_token_configured / app_secret_configured true (formato Hermes)
```

---

## Parte C — Porta 8090 no Docker + HTTPS no Caddy

No `docker-compose` do Hermes (repo: `hermes/docker-compose.yml`), publique:

```yaml
ports:
  - "127.0.0.1:8642:8642"
  - "127.0.0.1:8090:8090"   # WhatsApp Cloud webhook
```

No Caddy (mesmo proxy do n8n), adicione rota estável, por exemplo:

```caddy
# dentro do site srv1897392.hstgr.cloud
handle_path /whatsapp/* {
    reverse_proxy 127.0.0.1:8090
}
```

Ou path completo `/whatsapp/webhook` → `127.0.0.1:8090/whatsapp/webhook` (ajuste se `handle_path` stripar o prefixo).

**Callback URL no Meta (estável):**

```text
https://srv1897392.hstgr.cloud/whatsapp/webhook
```

Teste:

```bash
VERIFY='seu_verify_token'
curl -i "https://srv1897392.hstgr.cloud/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=$VERIFY&hub.challenge=hello"
# HTTP 200 + body hello
```

---

## Parte D — Webhook no Meta

1. App Charizard → WhatsApp → **Configuration** / Webhooks  
   (atalho UI: [wa-settings](https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-settings/?business_id=196300121382596))
2. Callback URL = URL da Parte C  
3. Verify token = `WHATSAPP_CLOUD_VERIFY_TOKEN` da VPS  
4. **Verify and save**  
5. Subscribe field **`messages`**

---

## Parte E — Mesmo cérebro (Telegram = WhatsApp)

Na VPS o Hermes já deve ter:

| Item | Caminho |
|------|---------|
| Script post | `/opt/data/bin/postar-linkedin.sh` |
| Skill | `/opt/data/skills/social-media/linkedin-post-n8n/SKILL.md` |
| Quick commands | `postar` / `postar-texto` no `config.yaml` |
| SOUL | fragmento LinkedIn (disparar sem perguntar) |

Comandos iguais nos dois canais:

| Comando | Efeito |
|---------|--------|
| `/postar` | texto + capa |
| `/postar-texto` | só texto |

Se o SOUL no PC diverge, ignore o Hermes Windows ou desligue o gateway local para não haver dois bots.

---

## Parte F — Validação

1. WhatsApp (número Business / teste Meta) → `oi` → Hermes VPS responde.  
2. `/postar-texto` → n8n execution (webhook) → alerta Telegram.  
3. Telegram `/postar-texto` → mesmo comportamento.  
4. `docker logs hermes --tail 80` sem erro de token/webhook.

---

## Checklist

- [ ] System User `hermes-vps` + token Never
- [ ] Assets: app + WABA Full control
- [ ] `.env` VPS com token permanente + App Secret + Verify + allowlist
- [ ] App ID `2842287619460178` (corrigir se estava outro)
- [ ] Porta `8090` publicada no container
- [ ] Caddy HTTPS → webhook
- [ ] Meta Verify + subscribe `messages`
- [ ] Skill LinkedIn presente na VPS
- [ ] Teste WhatsApp + Telegram

## Riscos

- Token permanente vazado = revogar no System User e gerar outro.  
- Dois Hermes (PC + VPS) = respostas duplicadas / skill diferente — deixe **só VPS** em produção.  
- Allowlist errado = bot ignora suas mensagens.  
- Token temp do wizard no PC **não** use na VPS; use só o System User.
