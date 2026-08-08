# Setup — Hermes + n8n (VPS)

Este projeto roda em dois containers na VPS Hostinger: **Hermes** (assistente Telegram) e **n8n** (pipeline LinkedIn).

## Passos

1. Abrir https://srv1824850.hstgr.cloud/ (n8n)
2. Confirmar credencial **LinkedIn account**
3. Confirmar credencial **OpenRouter account** — texto (DeepSeek), capa (FLUX) e reply (DeepSeek)
4. Fluxos: ver [FLUXO.md](FLUXO.md) · Assistente: [HERMES-ASSISTENTE.md](HERMES-ASSISTENTE.md)
5. Workflow **Post**: Active; nó **Daily 8h Sao Paulo** **desabilitado**
6. Workflow **Reply**: Active (poll ~2 min)
7. Manter **Resposta via Gmail** arquivado
8. Hermes: Telegram pareado + script `/opt/data/bin/postar-linkedin.sh` + env do webhook

## Workflows ativos

| Nome | ID | URL |
|------|-----|-----|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z |

## Modelos / geração

| Uso | Stack |
|-----|--------|
| Post (texto) | OpenRouter **`deepseek/deepseek-v4-flash`** |
| Post (capa, mode=full) | OpenRouter **`black-forest-labs/flux.2-pro`** |
| Reply comentário | OpenRouter **`deepseek/deepseek-v4-flash`** |

## Validação rápida

1. No Telegram: `/postar` (completo) ou `/postar-texto` (só texto).
2. Conferir Telegram de alerta: ok com capa, só texto, skip (anti-dupe) ou fail.
3. n8n Executions: origem **webhook**.
4. Reply: Generate Reply Text com DeepSeek → reply no LinkedIn (~2 min).

Detalhes de VPS: [VPS.md](VPS.md) · Tutorial: [TUTORIAL.md](TUTORIAL.md)  
Stack free (**opcional / legado**): [STACK-GRATUITA.md](STACK-GRATUITA.md)
