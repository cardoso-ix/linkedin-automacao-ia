# Automação LinkedIn — Hermes + n8n

Sistema em produção: o **Hermes** (Telegram) é o assistente operacional; o **n8n** (VPS) enfileira e publica no LinkedIn.

| Papel | O que faz |
|-------|-----------|
| **Hermes** (`@funcionario_vip_bot`) | Ajuda a escrever no chat; dispara webhooks de fila/post |
| **n8n** | Guarda texto/foto da fila, publica no LinkedIn, responde comentários |

**Post sob comando via Hermes (Telegram).** Schedule 08:00 está **desativado** — você decide quando postar.

| Fluxo | Disparo | Stack |
|-------|---------|--------|
| **Salvar texto** | Telegram → Hermes → webhook n8n | Data Table LinkedIn Textos Agenda (`ready`) |
| **Salvar foto** | Telegram foto → Hermes → webhook n8n | Data Table LinkedIn Imagens Agenda (`ready`) |
| **Post LinkedIn** | Telegram → Hermes → webhook n8n | Texto + foto da fila (sem LLM/FLUX) |
| **Resposta a comentários** | n8n a cada ~2 min (automático) | DeepSeek-V4-Flash |

Roteiro da demo: [docs/PRESENTACAO.md](docs/PRESENTACAO.md) · Assistente: [docs/HERMES-ASSISTENTE.md](docs/HERMES-ASSISTENTE.md) · Post manual: [docs/POST-MANUAL-AMANHA.md](docs/POST-MANUAL-AMANHA.md)

**Portfólio** — [cardoso-ix.github.io/Portifolio](https://cardoso-ix.github.io/Portifolio/) · **LinkedIn** — [eduardo-cardoso](https://www.linkedin.com/in/eduardo-cardoso-213a02267)

## Como postar (Telegram)

| Comando / frase | Resultado |
|-----------------|-----------|
| Validar texto · `salva este texto` · `/salvar-texto` | Enfileira texto (`status=ready`) |
| Enviar foto · `salva esta foto` · `/salvar-foto` | Enfileira foto (`status=ready`) |
| `/postar` · `posta agora` · `post completo` | **Texto da fila** + foto da fila (+ Monitor). Sem texto → aborta |
| `/postar-texto` · `posta só texto` · `sem imagem` | Texto da fila; **ignora** fila de foto (+ Monitor) |
| `/monitorar <url>` · colar link do post · `monitora este post` | Registra post **manual** no Posts Monitor |

Hermes **não pergunta** tema/canal — dispara o n8n na hora. O n8n notifica no Telegram ao terminar. Geração de texto e capas **FLUX** no n8n foram aposentadas neste path.

**Regra:** post manual via Hermes ⇒ sempre gravar o link na Data Table LinkedIn Posts Monitor (senão o reply de comentários não cobre o post).

## Arquitetura

| Workflow | ID | URL |
|----------|----|-----|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | https://srv1897392.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| LinkedIn Salvar Texto Hermes | `aPTD3w3uZCuz11tP` | https://srv1897392.hstgr.cloud/workflow/aPTD3w3uZCuz11tP |
| LinkedIn Salvar Foto Hermes | `HIlMXIjvjjxwcGlo` | https://srv1897392.hstgr.cloud/workflow/HIlMXIjvjjxwcGlo |
| LinkedIn Registrar Post Monitor | `1tqbFp0ft3GsxTgK` | https://srv1897392.hstgr.cloud/workflow/1tqbFp0ft3GsxTgK |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | https://srv1897392.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z |

> Resposta via Gmail (`5xkPzzTcKwdsPymn`) — **arquivado**.

```
Você (Telegram) → Hermes (assistente)
                    → webhook texto → Textos Agenda (ready)
                    → webhook foto  → Imagens Agenda (ready)
                    → webhook post (mode=full | text_only) → publica + Monitor
                    → webhook monitor (URL manual) → upsert Monitor
                    → anti-dupe (force=1 bypass) no post
                    → texto ready (obrigatorio) + foto ready (opcional)
                    → IF text_only? → Post Text Only
                      senão → foto ready → Post With Image
                      (sem texto → aborta; sem foto → so texto)
                    → Data Table + Telegram alerta

*/2m   Resposta Comentarios (automático, sem Hermes):
         Posts Monitor → HTML → parse → DeepSeek → reply LinkedIn
```

Timezone: **America/Sao_Paulo**.

## Docs

| Doc | Conteúdo |
|-----|----------|
| [docs/HERMES-ASSISTENTE.md](docs/HERMES-ASSISTENTE.md) | Comandos Telegram, webhook, modes full/text_only |
| [docs/WHATSAPP-CLOUD-API.md](docs/WHATSAPP-CLOUD-API.md) | Passo a passo Meta Cloud API → Hermes (com links) |
| [docs/WHATSAPP-PASSO-A-PASSO.md](docs/WHATSAPP-PASSO-A-PASSO.md) | Do zero: token permanente → VPS → webhook (clicar a clicar) |
| [docs/FLUXO.md](docs/FLUXO.md) | Arquitetura nó a nó |
| [docs/TEMAS.md](docs/TEMAS.md) | 30 temas do mês (Dia N = tema N) |
| [docs/IMAGENS-LOTE.md](docs/IMAGENS-LOTE.md) | Spec da capa editorial + 8 estilos |
| [docs/SETUP.md](docs/SETUP.md) | Credenciais e ativação |
| [docs/CHECKLIST.md](docs/CHECKLIST.md) | Checklist antes de ligar |
| [docs/TUTORIAL.md](docs/TUTORIAL.md) | Tutorial rápido |
| [docs/VPS.md](docs/VPS.md) | Hostinger: n8n + Hermes Docker |
| [docs/STACK-GRATUITA.md](docs/STACK-GRATUITA.md) | Modo free opcional / legado |

## Repo Hermes (VPS)

Arquivos em `hermes/` para deploy no container (secrets só no `.env` da VPS):

| Arquivo | Uso |
|---------|-----|
| `hermes/bin/postar-linkedin.sh` | Dispara webhook de post (`full` / `text_only`) |
| `hermes/bin/salvar-foto-linkedin.sh` | Enfileira foto Telegram (`status=ready`) |
| `hermes/bin/monitorar-linkedin.sh` | Dispara webhook de registro no Posts Monitor |
| `hermes/skills/linkedin-post-n8n/SKILL.md` | Skill de postar |
| `hermes/skills/linkedin-foto-n8n/SKILL.md` | Skill de salvar foto |
| `hermes/skills/linkedin-monitor-n8n/SKILL.md` | Skill de monitorar (post manual → tabela) |
| `hermes/SOUL-FRAGMENT-LINKEDIN.md` | Fragmento para `SOUL.md` |
| `hermes/docker-compose.yml` | Compose de referência |

## Prompts e skill Cursor

| Arquivo | Uso |
|---------|-----|
| `prompts/post-texto.json` | Briefing post → DeepSeek |
| `prompts/post-imagem-capa.json` | Capa FLUX.2 Pro (sem tipografia) |
| `prompts/resposta-comentario.json` | Reply a comentários |
| `skills/linkedin-resposta-comentario/` | Skill Cursor da voz de reply |

## Regras do post

- Nicho: IA aplicada, agentes de IA ou IA generativa
- 1000–1800 caracteres (parágrafos corridos)
- Tom humano; sem travessão, emojis ou jargão vazio
- Sem markdown (`**`) e sem URLs
- Entre 3 e 5 hashtags temáticas
- Imagem: foto real enfileirada no Telegram (não FLUX neste path)

## Stack

| Camada | Tecnologia |
|--------|------------|
| Assistente | Hermes Agent (Docker na VPS) + Telegram |
| Orquestração | n8n (VPS Hostinger KVM 2) |
| Texto do post | Fila de textos validados pelo usuário (sem LLM no n8n) |
| Imagem do post | Foto própria criada pelo usuário, via Telegram |
| Reply | DeepSeek-V4-Flash via API LinkedIn |
| Publicação | LinkedIn OAuth + REST comments |
| Memória de posts | Data Table `LinkedIn Posts Diario` |
| Fila de fotos | Data Table `LinkedIn Imagens Agenda` |
| Monitor de comentários | Data Table `LinkedIn Posts Monitor` |
| Alertas | Telegram (ok / skip / fail / sem foto na fila) |

## Como validar

1. Telegram: enviar foto → Hermes enfileira → `/postar` → texto + foto + Monitor.
2. `/postar` sem foto na fila → só texto + aviso Telegram.
3. `/postar-texto` → só texto (fila ignorada).
4. Post manual no LinkedIn → no Hermes: `monitora <url>` → `ok` e linha no Monitor.
5. Conferir Executions no n8n (origem **webhook** ou **schedule**).
6. Reply: aguardar poll ~2 min após comentário em post monitorado (< 48h).

> Mudanças no canvas ficam em **draft** até **Publish**. Este repositório **não** contém API keys.

Bootstrap VPS: `scripts/hermes-texto-vps-ready.sh` e `scripts/hermes-foto-vps-ready.sh` (rodar como root no servidor).
