# WhatsApp Cloud API → Hermes (passo a passo)

Guia para ligar o app Meta **Cloud API** ao Hermes na VPS, no mesmo modelo do Telegram: você manda comando no WhatsApp → Hermes dispara o n8n (LinkedIn).

**App Meta (seu):** [Dashboard](https://developers.facebook.com/apps/2842287619460178/dashboard/?business_id=196300121382596)  
**App ID:** `2842287619460178` · **Business ID:** `196300121382596`

> Não cole Access Token nem App Secret completos no chat/GitHub. Só no `.env` da VPS.

---

## Visão rápida

```
Seu WhatsApp → Meta Cloud API → webhook HTTPS → Hermes (VPS)
                                              → skill/script → n8n → LinkedIn
```

Docs oficiais Hermes: [WhatsApp Cloud API](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud) · visão geral [WhatsApp](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp)

---

## Passo 0 — Login no Meta

1. Abra o [dashboard do app](https://developers.facebook.com/apps/2842287619460178/dashboard/?business_id=196300121382596).
2. Se pedir login: [Meta for Developers](https://developers.facebook.com/) → **Continue with Facebook**.
3. Confirme o Business: [Meta Business Suite](https://business.facebook.com/) (portfolio ligado ao `196300121382596`).

**Esperado:** ver o nome do app e o menu lateral (WhatsApp / Settings).  
**Cuidado:** use a conta que criou o app; conta errada = “app not found”.

---

## Passo 1 — Confirmar produto WhatsApp no app

1. No dashboard: [App Dashboard](https://developers.facebook.com/apps/2842287619460178/dashboard/?business_id=196300121382596).
2. Se WhatsApp não aparecer: **Add product** / **Use cases** → *Connect with customers through WhatsApp*.
3. Atalhos úteis (UI Meta muda; se um 404, volte pelo menu):
   - [API Setup](https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-dev-console/?business_id=196300121382596)
   - [Configuration (webhooks)](https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-settings/?business_id=196300121382596)

**Esperado:** página “API Setup” com From / To e token.  
**Cuidado:** ainda não precisa de App Review para testar com até 5 números.

---

## Passo 2 — Anotar Phone Number ID (não é o telefone)

1. Abra [API Setup](https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-dev-console/?business_id=196300121382596).
2. Em **From**, anote o **Phone number ID** (15–17 dígitos).
3. Anote também o **WhatsApp Business Account ID (WABA)**, se aparecer.

**Erro #1 mais comum:** colar o número `+55…` no lugar do Phone Number ID.

Guarde como:

```text
WHATSAPP_CLOUD_PHONE_NUMBER_ID=xxxxxxxxxxxxxxx
WHATSAPP_CLOUD_WABA_ID=xxxxxxxxxxxxxxx   # opcional
WHATSAPP_CLOUD_APP_ID=2842287619460178
```

---

## Passo 3 — Access Token (teste → permanente)

### 3a — Token temporário (só para validar hoje)

1. Em [API Setup](https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-dev-console/?business_id=196300121382596) → **Generate access token**.
2. Copie (começa com `EAA…`). Expira em **~24h**.

### 3b — Token permanente (produção) — obrigatório na VPS

Guia dedicado (System User + Caddy + mesmo cérebro Telegram/WhatsApp):  
**[WHATSAPP-VPS-TOKEN.md](WHATSAPP-VPS-TOKEN.md)**

Resumo:

1. [System users](https://business.facebook.com/latest/settings/system_users) → Add `hermes-vps` → Admin  
2. Assign assets: app `2842287619460178` + WABA `1318156490102575` (Full control)  
3. Generate token: `business_management`, `whatsapp_business_messaging`, `whatsapp_business_management` · Never  
4. Colar **só** no `.env` da VPS (não no chat) · reiniciar container `hermes`

Doc Hermes: [Permanent token](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud#permanent-token-production)

---

## Passo 4 — App Secret

1. [Settings → Basic](https://developers.facebook.com/apps/2842287619460178/settings/basic/?business_id=196300121382596)
2. **Show** ao lado de **App secret** → copiar (32 chars hex).
3. Guardar como `WHATSAPP_CLOUD_APP_SECRET=...`

**Por quê:** sem App Secret o Hermes **recusa** inbound (HTTP 503).  
**Cuidado:** nunca versionar no GitHub.

---

## Passo 5 — Números de teste (lado Meta)

Em modo desenvolvimento, a Meta só deixa falar com números na whitelist:

1. [API Setup](https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-dev-console/?business_id=196300121382596) → **To** → Manage phone number list.
2. Adicione **seu** celular (com DDI, ex. Brasil `55…`).
3. Confirme o código SMS/WhatsApp que a Meta enviar.

Até **5** números em dev. App Review remove o limite depois.

---

## Passo 6 — Verify Token (você inventa)

No PC ou VPS:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Guarde o valor como `WHATSAPP_CLOUD_VERIFY_TOKEN=...`  
O **mesmo** string vai no Meta (Passo 8) e no `.env` do Hermes.

---

## Passo 7 — Hermes na VPS: env + porta do webhook

Na VPS (container Hermes, dados em `/opt/data` ou volume `hermes-data`):

1. Edite `/opt/data/.env` (ou o `.env` do compose Hermes) e acrescente:

```bash
WHATSAPP_CLOUD_PHONE_NUMBER_ID=
WHATSAPP_CLOUD_ACCESS_TOKEN=
WHATSAPP_CLOUD_APP_SECRET=
WHATSAPP_CLOUD_VERIFY_TOKEN=
WHATSAPP_CLOUD_ALLOWED_USERS=55SEUDDDSEUNUMERO
WHATSAPP_CLOUD_APP_ID=2842287619460178
# WHATSAPP_CLOUD_WABA_ID=
WHATSAPP_CLOUD_WEBHOOK_PORT=8090
WHATSAPP_CLOUD_WEBHOOK_PATH=/whatsapp/webhook
```

2. `WHATSAPP_CLOUD_ALLOWED_USERS` = seu número com DDI, **sem** `+`, espaços ou traços (ex. `5548999999999`).
3. Reinicie o gateway Hermes (`docker compose restart hermes` ou equivalente).
4. Wizard opcional (dentro do container): `hermes whatsapp-cloud`  
   Doc: [Quick start](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud#quick-start).

**Expor HTTPS na VPS (recomendado em produção):** no Caddy/Nginx, proxy para `127.0.0.1:8090` em um path/host público, por exemplo:

```text
https://srv1897392.hstgr.cloud/whatsapp/webhook  →  http://127.0.0.1:8090/whatsapp/webhook
```

(Ajuste o path se o proxy strip/prefix for diferente.)

**Alternativa rápida de teste:** [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)  
`cloudflared tunnel --url http://127.0.0.1:8090` → use a URL `https://….trycloudflare.com/whatsapp/webhook`  
**Cuidado:** quick tunnel muda a URL a cada restart.

Compose de referência do projeto: [`hermes/docker-compose.yml`](../hermes/docker-compose.yml).

---

## Passo 8 — Webhook no Meta

1. Abra Configuration / Webhooks do WhatsApp no app (menu lateral → WhatsApp → Configuration), ou tente:  
   [WhatsApp Configuration](https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-settings/?business_id=196300121382596)
2. **Edit** no Webhook:
   - **Callback URL:** `https://SEU-HOST-PUBLICO/whatsapp/webhook`  
     (ex. tunnel ou `https://srv1897392.hstgr.cloud/whatsapp/webhook` se o proxy estiver ok)
   - **Verify token:** o **mesmo** de `WHATSAPP_CLOUD_VERIFY_TOKEN`
3. **Verify and save** — Meta faz GET; Hermes deve ecoar o challenge.
4. **Webhook fields → Manage** → assine **`messages`**.

Teste manual (do seu PC):

```bash
curl -i "https://SEU-HOST/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=SEU_VERIFY&hub.challenge=hello"
# Esperado: HTTP 200 e corpo "hello"
```

Doc: [Configuring the webhook](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud#configuring-the-webhook-on-metas-side).

---

## Passo 9 — Teste ponta a ponta

1. No celular (número da whitelist Meta **e** allowlist Hermes), abra conversa com o **número Business** do app.
2. Envie: `oi` — Hermes deve responder.
3. Envie: `/postar` ou `posta só texto` — mesmo fluxo do Telegram (webhook n8n).  
   Ver: [HERMES-ASSISTENTE.md](HERMES-ASSISTENTE.md).
4. Confira Executions no n8n: [Post Diario Texto](https://srv1897392.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo).

**Não** dispare post de teste no LinkedIn se não quiser republicar hoje (`force=1` bypassa anti-dupe).

---

## Passo 10 — Perfil do bot (opcional)

Nome, foto e about: [WhatsApp Manager → Phone numbers](https://business.facebook.com/wa/manage/phone-numbers)

---

## Checklist final

- [ ] Login no app `2842287619460178`
- [ ] Phone Number ID anotado (não o telefone)
- [ ] Token (temp ok; permanente depois)
- [ ] App Secret no `.env`
- [ ] Seu número na whitelist Meta + `WHATSAPP_CLOUD_ALLOWED_USERS`
- [ ] Hermes reiniciado com vars Cloud
- [ ] HTTPS → porta `8090` path `/whatsapp/webhook`
- [ ] Meta: Verify and save + subscribe `messages`
- [ ] DM de teste ok; `/postar` só quando quiser

---

## Problemas comuns

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| Verify falha no Meta | Verify token diferente / Hermes off / URL errada | Conferir `.env`, `curl` do challenge, logs do gateway |
| Inbound 503 | Sem `WHATSAPP_CLOUD_APP_SECRET` | Colocar App Secret e reiniciar |
| Bot ignora mensagem | Fora do allowlist Hermes | Ajustar `WHATSAPP_CLOUD_ALLOWED_USERS` |
| “Recipient not allowed” | Fora da whitelist Meta (dev) | Passo 5 |
| Token inválido de um dia pro outro | Token temp 24h | Passo 3b (System User) |
| Número errado no env | Colou telefone no Phone Number ID | Passo 2 |

---

## Baileys vs Cloud API

| | Baileys (`hermes whatsapp`) | Cloud API (este guia) |
|--|----------------------------|------------------------|
| Conta | Pessoal + QR | Número Business Meta |
| Webhook público | Não | Sim |
| Risco | Ban (não oficial) | Oficial |
| Seu app Meta | Não usa | Usa `2842287619460178` |

Pode coexistir com números diferentes. Para produção do assistente LinkedIn, use **Cloud API**.

---

## Links úteis (lista)

| O quê | Link |
|-------|------|
| Dashboard do app | https://developers.facebook.com/apps/2842287619460178/dashboard/?business_id=196300121382596 |
| API Setup | https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-dev-console/?business_id=196300121382596 |
| Settings Basic (App Secret) | https://developers.facebook.com/apps/2842287619460178/settings/basic/?business_id=196300121382596 |
| System users (token permanente) | https://business.facebook.com/latest/settings/system_users |
| WhatsApp Manager (números) | https://business.facebook.com/wa/manage/phone-numbers |
| Hermes Cloud API docs | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud |
| n8n Post workflow | https://srv1897392.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| Assistente Hermes (comandos) | [HERMES-ASSISTENTE.md](HERMES-ASSISTENTE.md) |
