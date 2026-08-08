# Hermes assistente — post LinkedIn sob comando

O **Hermes** no Telegram (`@funcionario_vip_bot`) é o assistente: você manda o comando e ele dispara o n8n.

O schedule **Daily 8h Sao Paulo (08:00)** está **DESATIVADO**. Não há postagem automática diária — só sob comando.

## Papéis

| Quem | Função |
|------|--------|
| Você | Decide **quando** postar e se quer capa ou só texto |
| Hermes | Assistente no Telegram; dispara o webhook sem perguntar tema/canal |
| n8n | Gera texto/capa, publica no LinkedIn, notifica o resultado |

## Como pedir (Telegram)

### Comandos

| Comando | Mode | O que faz |
|---------|------|-----------|
| `/postar` | `full` (default) | Texto + capa FLUX + publica |
| `/postar-texto` | `text_only` | Texto e publica **sem** capa |

### Frases → full (texto + imagem)

- `gera texto, imagem e posta`
- `post completo`
- `publica no LinkedIn agora`
- `roda o post diario agora`

### Frases → text_only (só texto)

- `posta só texto`
- `sem imagem`
- `apenas texto`
- `post sem capa`

Defaults (não perguntar): LinkedIn, tema Dia N automático, PT-BR, secret já no `.env` do Hermes.

## Arquitetura

```
Telegram /postar        → postar-linkedin.sh full      → webhook mode=full
Telegram /postar-texto  → postar-linkedin.sh text_only → webhook mode=text_only
Telegram frase          → skill/SOUL escolhe mode       → mesmo script
```

No n8n (`ysHFWIV0tGWJbhjo`):

1. Webhook valida secret  
2. Anti-dupe do dia (`force=1` bypass)  
3. Gera texto (DeepSeek)  
4. **IF Text Only Mode**  
   - `mode=text_only` **ou** `sem_imagem:true` **ou** `image:false` → **Post Text Only**  
   - `mode=full` (default) → capa FLUX → Post With Image (fallback texto se capa falhar)

## Webhook n8n

| Item | Valor |
|------|--------|
| Workflow | LinkedIn Post Diario Texto (`ysHFWIV0tGWJbhjo`) |
| Método | `POST` |
| URL produção | `https://srv1824850.hstgr.cloud/webhook/hermes-linkedin-post` |
| Auth | Header `X-Hermes-Secret` |
| Secret | `N8N_HERMES_WEBHOOK_SECRET` no `.env` do Hermes (`/opt/data/.env`) — **não** versionar |

Body:

```json
{"source":"hermes","command":"postar","force":1,"mode":"full","sem_imagem":false}
```

```json
{"source":"hermes","command":"postar","force":1,"mode":"text_only","sem_imagem":true}
```

## Arquivos no repo (`hermes/`)

| Repo | Destino na VPS |
|------|----------------|
| `hermes/bin/postar-linkedin.sh` | `/opt/data/bin/postar-linkedin.sh` |
| `hermes/skills/linkedin-post-n8n/SKILL.md` | `/opt/data/skills/social-media/linkedin-post-n8n/SKILL.md` |
| `hermes/SOUL-FRAGMENT-LINKEDIN.md` | mesclar em `/opt/data/SOUL.md` |
| `hermes/docker-compose.yml` | referência do stack Hermes |

Env na VPS: `N8N_LINKEDIN_POST_WEBHOOK_URL`, `N8N_HERMES_WEBHOOK_SECRET`, OpenRouter, Telegram.

## Reply automático a comentários

Workflow `q28d2xJlAgvMpZ9Z` — **automático** (não passa pelo Hermes):

- Poll a cada **~2 min**
- Sheets + HTML → DeepSeek → reply LinkedIn
- Sem Gmail

## Comportamento importante

1. Pedidos de post → disparo imediato (sem esclarecimento).  
2. Anti-dupe: sem `force=1`, skip se já houver post no dia.  
3. Hermes envia `"force": 1` (pode republicar no mesmo dia se pedir de novo).  
4. Schedule 08:00 do POST permanece **OFF**.

## Como validar

1. `/postar` → notificação de texto + capa (ou fallback só texto).  
2. `/postar-texto` → somente texto, sem FLUX.  
3. n8n Executions: origem **webhook**.  
4. Nó **Daily 8h Sao Paulo** disabled.

## Riscos

- Pedir 2× com force → dois posts no mesmo dia.  
- Secret vazado → qualquer um dispara o pipeline; rotacionar no n8n e no `.env`.
