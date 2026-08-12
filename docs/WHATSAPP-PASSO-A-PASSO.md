# WhatsApp Cloud — passo a passo (Eduardo)

**App:** Charizard · **App ID:** `2842287619460178` · **Business:** `196300121382596`  
**VPS:** `srv1897392.hstgr.cloud` · **Webhook:** `https://srv1897392.hstgr.cloud/whatsapp/webhook`  
**Número de teste Meta:** `+1 555-675-6227`  
**Phone Number ID:** confira **na tela** em API Setup (doc antiga: `1164738343399026`; curl/screenshot pode mostrar `118…` — use o valor do rótulo Meta).  
**WABA:** `1318156490102575`

> Nunca cole Access Token, App Secret ou Verify Token no chat/GitHub.  
> **Não** use **Gerar token** (temporário ~24h) na UI Meta — o token permanente do System User **já está na VPS**.

Guia técnico completo: [WHATSAPP-CLOUD-API.md](WHATSAPP-CLOUD-API.md) · Token/VPS: [WHATSAPP-VPS-TOKEN.md](WHATSAPP-VPS-TOKEN.md)

---

## Revalidação rápida (setup quase pronto)

Foque nestes passos se Hermes + Caddy já estão no ar. Objetivo: App Secret certo, allowlist certa, mensagem `oi` pelo celular.

### 1) Abrir o console WhatsApp (Meta)

1. Abra: https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-dev-console/?business_id=196300121382596  
2. Confirme o número de teste **From** = `+1 555-675-6227` (ou o que a Meta mostrar).  
3. Em **From**, copie o **Phone number ID** do rótulo na tela (não invente; ignore IDs divergentes de prints antigos).  
4. **Pule** qualquer botão **Generate access token** / **Gerar token**.

**Por quê:** token temporário da UI expira; produção usa System User na VPS.  
**Esperado:** API Setup aberto, Phone Number ID anotado.  
**Cuidado:** Phone Number ID ≠ número `+1…` / `+55…`.

### 2) Revalidar App Secret (crítico)

1. Abra: https://developers.facebook.com/apps/2842287619460178/settings/basic/?business_id=196300121382596  
2. Em **App secret** → **Show** / **Mostrar** (senha do Facebook se pedir).  
3. Compare com `WHATSAPP_CLOUD_APP_SECRET` no `.env` do Hermes na VPS (só no servidor).  
4. Se diferente: atualize o `.env` na VPS e reinicie o container `hermes`.

**Por quê:** App Secret errado/ausente → Hermes **recusa inbound** (HTTP 503 / mensagem ignorada).  
**Esperado:** secret da Meta = secret da VPS.  
**Cuidado:** não cole o secret no chat.

### 3) Confirmar webhook no Meta

1. Abra: https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-settings/?business_id=196300121382596  
   (se 404: [dashboard](https://developers.facebook.com/apps/2842287619460178/dashboard/?business_id=196300121382596) → WhatsApp → Configuration)  
2. Callback URL deve ser exatamente:

```text
https://srv1897392.hstgr.cloud/whatsapp/webhook
```

3. Verify token = o mesmo de `WHATSAPP_CLOUD_VERIFY_TOKEN` na VPS.  
4. Campo **`messages`** assinado.

**Esperado:** webhook verificado (sem erro vermelho).  
**Cuidado:** path errado ou Hermes off → Verify falha.

### 4) Allowlist — dois formatos

No `.env` do Hermes (`WHATSAPP_CLOUD_ALLOWED_USERS`), inclua **seu** celular com DDI, **sem** `+`/espaços/traços.

Recomendação: listar **ambos** os formatos que a Meta pode enviar (vírgula ou o separador que o Hermes aceitar no projeto), por exemplo:

```text
WHATSAPP_CLOUD_ALLOWED_USERS=5548999999999,48999999999
```

(ajuste para o seu número real). Reinicie `hermes` após editar.

**Por quê:** fora da allowlist o bot **ignora** a mensagem sem erro óbvio.  
**Meta (modo dev):** seu número também precisa estar na whitelist **To** em API Setup (máx. 5).  
**Cuidado:** não coloque o número de teste `+1 555…` como “seu” usuário — esse é o **bot**.

### 5) Hostinger — conferir VPS (rápido)

1. hPanel Hostinger → VPS `srv1897392` (ou VM `1897392`).  
2. Terminal do **servidor** (prompt `root@srv1897392`, **não** o shell do container).  
3. Conferir (sem imprimir secrets):

```bash
docker ps --format '{{.Names}}' | grep -i hermes
curl -sS http://127.0.0.1:8090/health
# opcional: challenge público (substitua VERIFY pelo valor da VPS, só no terminal)
# curl -i "https://srv1897392.hstgr.cloud/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=VERIFY&hub.challenge=hello"
```

**Esperado:** container `hermes` up; health com verify/app_secret configurados; challenge → HTTP 200 + `hello`.  
**Cuidado:** se health falhar, não teste no celular ainda.

### 6) Teste final no celular

1. WhatsApp no **seu** celular (número na allowlist + whitelist Meta).  
2. Conversa com o número de teste: **`+1 555-675-6227`**.  
3. Envie: `oi`.  
4. Hermes na VPS deve responder.  
5. Só depois: `/postar-texto` se quiser disparar LinkedIn de verdade.

Digite no chat só: **OK** ou o sintoma (sem tokens).

---

## Links rápidos

| O quê | Link |
|-------|------|
| API Setup (número / Phone Number ID) | https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-dev-console/?business_id=196300121382596 |
| Settings Basic (App Secret) | https://developers.facebook.com/apps/2842287619460178/settings/basic/?business_id=196300121382596 |
| Webhooks WhatsApp | https://developers.facebook.com/apps/2842287619460178/whatsapp-business/wa-settings/?business_id=196300121382596 |
| Dashboard do app | https://developers.facebook.com/apps/2842287619460178/dashboard/?business_id=196300121382596 |
| System users (só se precisar **novo** token permanente) | https://business.facebook.com/latest/settings/system_users |
| Docs Hermes Cloud | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud |

---

## Se algo falhar

| Sintoma | Ação |
|---------|------|
| Inbound 503 / silêncio | Refazer passo 2 (App Secret) + restart `hermes` |
| Bot ignora `oi` | Passo 4 (allowlist nos **dois** formatos) + whitelist Meta **To** |
| Verify and save falha | Passo 5 (8090 + Caddy) + verify token igual Meta/VPS |
| Token inválido | **Não** Gerar token na UI — renovar System User ([WHATSAPP-VPS-TOKEN.md](WHATSAPP-VPS-TOKEN.md)) |
| Phone Number ID estranho | Copiar de novo do rótulo em API Setup |
| `invalid X-Hub-Signature-256 (header:'', body_len=…)` com body_len pequeno (ex. 2–50) | **Probe** da internet, não a Meta — ignore. POST real da Meta traz `X-Hub-Signature-256: sha256=…` e body JSON bem maior |
| `No env user allowlists configured` | Definir `WHATSAPP_CLOUD_ALLOWED_USERS` no `.env` e reiniciar `hermes` |

### Caddy e o header `X-Hub-Signature-256`

O bloco recomendado **já encaminha** todos os headers (incluindo a assinatura):

```caddy
handle /whatsapp/* {
    reverse_proxy 127.0.0.1:8090
}
```

**Não** use `request_header delete X-Hub-Signature-256` (nem delete genérico de headers). Só adicione `header_up` se algum middleware custom tiver removido o header — no setup padrão do repo/script isso **não** acontece.

---

## Setup do zero (referência)

Se ainda não existir System User / `.env` / Caddy, siga [WHATSAPP-VPS-TOKEN.md](WHATSAPP-VPS-TOKEN.md) e [WHATSAPP-CLOUD-API.md](WHATSAPP-CLOUD-API.md). Resumo: System User `hermes-vps` → token Never → `.env` VPS → porta `8090` → Caddy → webhook Meta → teste `oi`.
