# Automação LinkedIn — Agentes de IA (n8n)

Sistema em produção que publica um post diário no LinkedIn (texto + capa editorial) e responde comentários nos posts monitorados — orquestrado no **n8n** (VPS).

| Fluxo | O que faz | Stack |
|-------|-----------|--------|
| **Post diário 08:00** | Tema do dia → texto → capa → LinkedIn | OpenRouter **DeepSeek-V4-Flash** + **FLUX.2 Pro** |
| **Resposta a comentários** | Sheets + HTML → reply no post | OpenRouter **DeepSeek-V4-Flash** |

Roteiro da demo: [docs/PRESENTACAO.md](docs/PRESENTACAO.md)

**Portfólio** — [cardoso-ix.github.io/Portifolio](https://cardoso-ix.github.io/Portifolio/) · **LinkedIn** — [eduardo-cardoso](https://www.linkedin.com/in/eduardo-cardoso-213a02267)

## Arquitetura

| Workflow | ID | URL |
|----------|----|-----|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z |

> Resposta via Gmail (`5xkPzzTcKwdsPymn`) — **arquivado** (fora do portfólio).

```
08:00  Post Diario:
         anti-dupe → Dia N (tema 1–30) → DeepSeek-V4-Flash (OpenRouter)
         → sanitize → capa FLUX.2 Pro (8 estilos, sem texto)
         → LinkedIn IMAGE  |  fallback: só texto
         → Data Table + Telegram (ok / skip / fail)

*/2m   Resposta Comentarios Post:
         Sheets monitor → HTML → parse → DeepSeek-V4-Flash → HTTP reply
```

Timezone: **America/Sao_Paulo**.

**Prova recente (post):** execução `5712` — post com imagem `urn:li:share:7489362507237675008`.

## Docs

| Doc | Conteúdo |
|-----|----------|
| [docs/FLUXO.md](docs/FLUXO.md) | Arquitetura ativa nó a nó |
| [docs/TEMAS.md](docs/TEMAS.md) | 30 temas do mês (Dia N = tema N) |
| [docs/IMAGENS-LOTE.md](docs/IMAGENS-LOTE.md) | Spec da capa editorial + 8 estilos |
| [docs/SETUP.md](docs/SETUP.md) | Credenciais e ativação |
| [docs/CHECKLIST.md](docs/CHECKLIST.md) | Checklist antes de ligar |
| [docs/TUTORIAL.md](docs/TUTORIAL.md) | Tutorial rápido |
| [docs/VPS.md](docs/VPS.md) | Acesso Hostinger / Docker |
| [docs/STACK-GRATUITA.md](docs/STACK-GRATUITA.md) | Modo free **opcional / legado** (não é o default) |

## Prompts e skill

| Arquivo | Uso |
|---------|-----|
| `prompts/post-texto.json` | Briefing “Previsibilidade na Prática” → DeepSeek via OpenRouter |
| `prompts/post-imagem-capa.json` | Capa editorial FLUX.2 Pro (sem texto + 8 estilos) |
| `prompts/resposta-comentario.json` | Reply a comentários (DeepSeek via OpenRouter) |
| `skills/linkedin-resposta-comentario/` | Skill Cursor da voz de reply |

## Regras do post

- Nicho: IA aplicada, agentes de IA ou IA generativa
- 1000–1800 caracteres (parágrafos corridos)
- Tom humano; sem travessão, emojis ou jargão vazio
- Sem markdown (`**`) e sem URLs
- No máximo 3 hashtags (opcionais)
- Fechar com reflexão aberta ou convite leve ao comentário

## Stack

| Camada | Tecnologia |
|--------|------------|
| Orquestração | n8n (VPS Hostinger) |
| Texto do post | OpenRouter **DeepSeek-V4-Flash** (`deepseek/deepseek-v4-flash`) |
| Imagem do post | OpenRouter **FLUX.2 Pro** (`black-forest-labs/flux.2-pro`) via `/api/v1/images` |
| Reply de comentário | OpenRouter **DeepSeek-V4-Flash** (mesmo modelo) |
| Credencial | **OpenRouter account** (texto post, capa e reply) |
| Publicação | LinkedIn OAuth (IMAGE ou texto) + REST comments |
| Memória de posts | Data Table `LinkedIn Posts Diario` |
| Monitor de replies | Google Sheets (monitor + already replied) |
| Alertas | Telegram (ok / skip / fail; reflete `hasCover`) |

## Como validar

1. Abrir o workflow Post Diario → **Execute once** (ou esperar 08:00).
2. Se já houver post do dia → Telegram **skip** (anti-dupe).
3. Caso contrário → LinkedIn com capa FLUX; Telegram “Texto + capa FLUX.2 Pro”.
4. Reply: abrir Resposta Comentarios Post → conferir nó **Generate Reply Text** com DeepSeek OpenRouter → Execute once / aguardar poll.
5. Conferir Executions no n8n.

> Mudanças no canvas ficam em **draft** até **Publish**. Este repositório não contém API keys.
