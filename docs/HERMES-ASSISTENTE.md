# Hermes assistente — post LinkedIn sob comando

O **Hermes** no Telegram (`@funcionario_vip_bot`) é o assistente: você manda o comando e ele dispara o n8n.

O schedule **Daily 8h Sao Paulo (08:00)** está **ATIVO**. Post diário automático + disparo manual via comando.

## Papéis

| Quem | Função |
|------|--------|
| Você | Valida texto e foto no Telegram; decide **quando** postar; em post manual, cola o link para monitorar |
| Hermes | Ajuda a escrever no chat; dispara webhooks de fila/post sem perguntar tema/canal |
| n8n | **Só fila + publicar + reply**: guarda texto/foto, publica no `/postar`, grava no Posts Monitor, responde comentários |

## Como pedir (Telegram / WhatsApp)

### 1) Enfileirar texto (obrigatório antes do `/postar`)

| Comando / frase | O que faz |
|-----------------|-----------|
| Validar o texto no chat + "salva este texto" / "envia pro n8n" / `/salvar-texto` | Cria linha `status=ready` em **LinkedIn Textos Agenda** |

### 2) Enfileirar foto (opcional)

| Comando / frase | O que faz |
|-----------------|-----------|
| Enviar foto + "salva esta foto" / "usa no próximo post" / `/salvar-foto` | Grava a imagem e cria linha `status=ready` em **LinkedIn Imagens Agenda** |

### 3) Comandos de post

| Comando | Mode | O que faz |
|---------|------|-----------|
| `/postar` | `full` (default) | Usa **texto ready** + **foto ready** (se houver); sem foto → só texto; sem texto → aborta + aviso |
| `/postar-texto` | `text_only` | Usa **texto ready**; **ignora** a fila de foto |

**Ordem típica:** `/salvar-texto` → (opcional) `/salvar-foto` → `/postar` no dia seguinte ou quando quiser.

### 4) Comando de monitor (post manual)

| Comando | O que faz |
|---------|-----------|
| `/monitorar <url>` | Upsert do link na Data Table **LinkedIn Posts Monitor** (`status=monitoring`) |

Frases equivalentes: `monitora este post`, `acompanha os comentários`, `salva o link`, ou só colar a URL `linkedin.com/posts/...`.

**Regra:** post manual + pedido ao Hermes ⇒ **sempre** gravar na tabela. Sem a linha, o reply automático não cobre aquele post.

### Frases → full (texto da fila + foto da fila)

- `posta agora`
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
Telegram (texto)        → salvar-texto-linkedin.sh     → webhook hermes-linkedin-texto
                                                         → Textos Agenda (ready)
Telegram (foto)         → salvar-foto-linkedin.sh      → webhook hermes-linkedin-foto
                                                         → disco n8n + Imagens Agenda (ready)
Telegram /postar        → postar-linkedin.sh full      → webhook hermes-linkedin-post
                                                         → texto ready + foto ready (senão só texto)
Telegram /postar-texto  → postar-linkedin.sh text_only → webhook hermes-linkedin-post
Telegram /monitorar URL → monitorar-linkedin.sh URL    → webhook hermes-linkedin-monitor
                                                         → Data Table LinkedIn Posts Monitor
                                                         → (poll) LinkedIn Resposta Comentarios Post
```

### Post (`ysHFWIV0tGWJbhjo`)

1. Webhook valida secret  
2. Anti-dupe do dia (`force=1` bypass)  
3. Lê texto `ready` em **LinkedIn Textos Agenda** (sem LLM) — se não houver, aborta + aviso  
4. IF Text Only Mode → Post Text Only **ou** Get Ready Photo → (foto Hermes → Post With Image; **senão** Post Text Only)  
5. Marca texto/foto usados (`status=used`)  
6. **Save Posts Monitor** (upsert `postUrl` / URN, `status=monitoring`)  
7. Notify Telegram (`Texto fila + foto Hermes` ou `Somente texto da fila`)

### Salvar texto (`aPTD3w3uZCuz11tP`)

1. Webhook `POST /webhook/hermes-linkedin-texto` + header `X-Hermes-Secret`  
2. Valida secret (length ≥ 16) + texto (50–3000 chars)  
3. Supersede ready anterior (`source=hermes`)  
4. Insert em **LinkedIn Textos Agenda** (`status=ready`)  
5. Responde `{ ok: true, status: "ready", charCount, tema }`

### Salvar foto (`HIlMXIjvjjxwcGlo`)

1. Webhook `POST /webhook/hermes-linkedin-foto` + header `X-Hermes-Secret`  
2. Valida secret (length ≥ 16) + base64  
3. Converte → grava arquivo sob `/home/node/.n8n/`  
4. Insert em **LinkedIn Imagens Agenda** (`status=ready`)  
5. Responde `{ ok: true, filePath, ... }`

### Registrar post manual (`1tqbFp0ft3GsxTgK`)

1. Webhook `POST /webhook/hermes-linkedin-monitor` + header `X-Hermes-Secret`  
2. Parse URL/URN  
3. Upsert em **LinkedIn Posts Monitor**  
4. Responde `{ ok: true, postUrl, postUrn, ... }`

## Webhooks n8n

### Post

| Item | Valor |
|------|--------|
| Workflow | LinkedIn Post Diario Texto (`ysHFWIV0tGWJbhjo`) |
| Método | `POST` |
| URL produção | `https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-post` |
| Auth | Header `X-Hermes-Secret` |
| Secret | `N8N_HERMES_WEBHOOK_SECRET` no `.env` do Hermes — **não** versionar |

Body:

```json
{"source":"hermes","command":"postar","force":1,"mode":"full","sem_imagem":false}
```

```json
{"source":"hermes","command":"postar","force":1,"mode":"text_only","sem_imagem":true}
```

### Foto (fila)

| Item | Valor |
|------|--------|
| Workflow | LinkedIn Salvar Foto Hermes (`HIlMXIjvjjxwcGlo`) |
| Método | `POST` |
| URL produção | `https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-foto` |
| Auth | Header `X-Hermes-Secret` (mesmo secret; length ≥ 16) |
| Env Hermes | `N8N_LINKEDIN_FOTO_WEBHOOK_URL` |

Body:

```json
{"source":"hermes","command":"salvar-foto","imageBase64":"<base64>","mimeType":"image/jpeg","caption":"Foto Telegram","tema":"Foto Telegram"}
```

### Texto (fila)

| Item | Valor |
|------|--------|
| Workflow | LinkedIn Salvar Texto Hermes (`aPTD3w3uZCuz11tP`) |
| Método | `POST` |
| URL produção | `https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-texto` |
| Auth | Header `X-Hermes-Secret` (mesmo secret; length ≥ 16) |
| Env Hermes | `N8N_LINKEDIN_TEXTO_WEBHOOK_URL` |
| Data Table | **LinkedIn Textos Agenda** (`m1I5Y0xmJEGCsdIM`) |

Body:

```json
{"source":"hermes","command":"salvar-texto","postText":"Texto final validado no Telegram...","tema":"Post Telegram"}
```

### Monitor (manual)

| Item | Valor |
|------|--------|
| Workflow | LinkedIn Registrar Post Monitor (`1tqbFp0ft3GsxTgK`) |
| Método | `POST` |
| URL produção | `https://srv1897392.hstgr.cloud/webhook/hermes-linkedin-monitor` |
| Auth | Header `X-Hermes-Secret` (mesmo secret) |
| Env Hermes | `N8N_LINKEDIN_MONITOR_WEBHOOK_URL` |

Body:

```json
{"source":"hermes","command":"monitorar","postUrl":"https://www.linkedin.com/posts/...activity-123...","tema":"Post manual","postText":""}
```

No n8n, o nó Code **não** lê `$env` nesta instância (`access to env vars denied`). Auth dos webhooks Hermes: secret com comprimento ≥ 16. Bootstrap VPS: `scripts/hermes-foto-vps-ready.sh`, `scripts/hermes-texto-vps-ready.sh`, `scripts/hermes-monitorar-vps-ready.sh`.

## Arquivos no repo (`hermes/`)

| Repo | Destino na VPS |
|------|----------------|
| `hermes/bin/postar-linkedin.sh` | `/opt/data/bin/postar-linkedin.sh` |
| `hermes/bin/salvar-texto-linkedin.sh` | `/opt/data/bin/salvar-texto-linkedin.sh` |
| `hermes/bin/salvar-foto-linkedin.sh` | `/opt/data/bin/salvar-foto-linkedin.sh` |
| `hermes/bin/monitorar-linkedin.sh` | `/opt/data/bin/monitorar-linkedin.sh` |
| `hermes/skills/linkedin-post-n8n/SKILL.md` | `/opt/data/skills/social-media/linkedin-post-n8n/SKILL.md` |
| `hermes/skills/linkedin-texto-n8n/SKILL.md` | `/opt/data/skills/social-media/linkedin-texto-n8n/SKILL.md` |
| `hermes/skills/linkedin-foto-n8n/SKILL.md` | `/opt/data/skills/social-media/linkedin-foto-n8n/SKILL.md` |
| `hermes/skills/linkedin-monitor-n8n/SKILL.md` | `/opt/data/skills/social-media/linkedin-monitor-n8n/SKILL.md` |
| `hermes/SOUL-FRAGMENT-LINKEDIN.md` | mesclar em `/opt/data/SOUL.md` |
| `hermes/docker-compose.yml` | referência do stack Hermes |

Env na VPS: `N8N_LINKEDIN_POST_WEBHOOK_URL`, `N8N_LINKEDIN_TEXTO_WEBHOOK_URL`, `N8N_LINKEDIN_FOTO_WEBHOOK_URL`, `N8N_LINKEDIN_MONITOR_WEBHOOK_URL`, `N8N_HERMES_WEBHOOK_SECRET`, OpenRouter/OpenCode Go, Telegram.

## Reply automático a comentários

Workflow `q28d2xJlAgvMpZ9Z` — **automático** (não passa pelo Hermes):

- Poll a cada **~2 min**
- Data Table **LinkedIn Posts Monitor** (`status=monitoring`, frescos 48h) + HTML → DeepSeek → reply LinkedIn
- Sem Gmail

## Comportamento importante

1. Pedidos de post → disparo imediato (sem esclarecimento).  
2. Anti-dupe: sem `force=1`, skip se já houver post no dia.  
3. Hermes envia `"force": 1` (pode republicar no mesmo dia se pedir de novo).  
4. Schedule 08:00 do POST está **ON** (diário automático).  
5. Post via `/postar` já entra no Monitor — **não** chamar `/monitorar` de novo.  
6. Post **manual** → Hermes **deve** chamar `/monitorar` (gravar na tabela).  
7. Texto validado → Hermes **deve** chamar `/salvar-texto` antes do `/postar`.  
8. Foto real → Hermes **deve** chamar `/salvar-foto` (enfileirar) antes do `/postar` com imagem.

## Como validar

1. Validar texto no Telegram → `/salvar-texto` → Hermes confirma fila (`ok` / `status=ready`).  
2. (Opcional) Enviar foto → `/salvar-foto` → `ok` / `ready`.  
3. `/postar` → notificação com texto da fila (+ foto se houver) + linha no Posts Monitor; linhas da Agenda viram `used`.  
4. `/postar` sem texto na fila → aborta + aviso no Telegram.  
5. `/postar-texto` → texto da fila, foto ignorada.  
6. Postar no app LinkedIn → colar URL no Hermes (`monitora https://...`) → `ok: true` + linha no Monitor.  
7. n8n Executions: origem **webhook**.

## Riscos

- Pedir 2× com force → dois posts no mesmo dia.  
- Secret vazado → qualquer um dispara o pipeline; rotacionar no n8n e no `.env`.  
- URL manual sem `activity-<id>` / URN → falha `missing_postUrn` (cole o link completo do post).  
- Janela de reply: posts com mais de **48h** saem do poll mesmo com link salvo.  
- Foto grande demais pode estourar timeout/body do webhook — prefira JPEG razoável.
