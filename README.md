# Automação LinkedIn — Hermes + n8n

Sistema em produção: o **Hermes** (Telegram) é o assistente operacional; o **n8n** (VPS) executa geração e publicação no LinkedIn.

| Papel | O que faz |
|-------|-----------|
| **Hermes** (`@funcionario_vip_bot`) | Recebe comandos no Telegram e dispara o pipeline |
| **n8n** | Gera texto/capa, publica no LinkedIn, responde comentários |

**Não há post automático às 08:00.** O schedule diário está **desativado**. Você escolhe quando postar pelo Telegram.

| Fluxo | Disparo | Stack |
|-------|---------|--------|
| **Post LinkedIn** | Telegram → Hermes → webhook n8n | DeepSeek-V4-Flash + FLUX.2 Pro (ou só texto) |
| **Resposta a comentários** | n8n a cada ~2 min (automático) | DeepSeek-V4-Flash |

Roteiro da demo: [docs/PRESENTACAO.md](docs/PRESENTACAO.md) · Assistente: [docs/HERMES-ASSISTENTE.md](docs/HERMES-ASSISTENTE.md)

**Portfólio** — [cardoso-ix.github.io/Portifolio](https://cardoso-ix.github.io/Portifolio/) · **LinkedIn** — [eduardo-cardoso](https://www.linkedin.com/in/eduardo-cardoso-213a02267)

## Como postar (Telegram)

| Comando / frase | Resultado |
|-----------------|-----------|
| `/postar` · `gera texto, imagem e posta` · `post completo` | Texto + capa FLUX |
| `/postar-texto` · `posta só texto` · `sem imagem` | Só texto (sem capa) |

Hermes **não pergunta** tema/canal — dispara o n8n na hora. O n8n notifica no Telegram ao terminar.

## Arquitetura

| Workflow | ID | URL |
|----------|----|-----|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z |

> Resposta via Gmail (`5xkPzzTcKwdsPymn`) — **arquivado**.

```
Você (Telegram) → Hermes (assistente)
                    → webhook n8n (mode=full | text_only)
                    → anti-dupe (force=1 bypass)
                    → Dia N (tema 1–30) → DeepSeek-V4-Flash
                    → IF text_only? → Post Text Only
                      senão → capa FLUX.2 Pro → Post With Image
                    → Data Table + Telegram alerta

*/2m   Resposta Comentarios (automático, sem Hermes):
         Sheets → HTML → parse → DeepSeek → reply LinkedIn
```

Timezone: **America/Sao_Paulo**.

## Docs

| Doc | Conteúdo |
|-----|----------|
| [docs/HERMES-ASSISTENTE.md](docs/HERMES-ASSISTENTE.md) | Comandos Telegram, webhook, modes full/text_only |
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
| `hermes/bin/postar-linkedin.sh` | Dispara webhook (`full` / `text_only`) |
| `hermes/skills/linkedin-post-n8n/SKILL.md` | Skill do assistente |
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
- Capa **sem texto/letras/números** na arte

## Stack

| Camada | Tecnologia |
|--------|------------|
| Assistente | Hermes Agent (Docker na VPS) + Telegram |
| Orquestração | n8n (VPS Hostinger) |
| Texto do post | OpenRouter **DeepSeek-V4-Flash** |
| Imagem do post | OpenRouter **FLUX.2 Pro** |
| Reply | OpenRouter **DeepSeek-V4-Flash** |
| Publicação | LinkedIn OAuth + REST comments |
| Memória de posts | Data Table `LinkedIn Posts Diario` |
| Alertas | Telegram (ok / skip / fail) |

## Como validar

1. Telegram `/postar` → texto + capa (ou `/postar-texto` → só texto).
2. Conferir Executions no n8n (origem **webhook**, não schedule).
3. Confirmar nó **Daily 8h Sao Paulo** **desabilitado**.
4. Reply: aguardar poll ~2 min após comentário em post monitorado.

> Mudanças no canvas ficam em **draft** até **Publish**. Este repositório **não** contém API keys.
