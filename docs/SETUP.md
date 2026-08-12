# Setup — Hermes + n8n (VPS)

Este projeto roda em dois containers na VPS Hostinger (KVM 2): **Hermes** (assistente Telegram) e **n8n** (pipeline LinkedIn).

## Passos

1. Abrir https://srv1897392.hstgr.cloud/ (n8n)
2. Confirmar credencial **LinkedIn account** (OAuth válido)
3. Confirmar credencial **OpenCode Go** — texto e reply (DeepSeek-V4-Flash)
4. Fluxos: ver [FLUXO.md](FLUXO.md) · Assistente: [HERMES-ASSISTENTE.md](HERMES-ASSISTENTE.md)
5. Workflow **Post Diario Texto**: Active (schedule 08:00 + webhook Hermes)
6. Workflow **Salvar Texto Hermes**: Active
7. Workflow **Salvar Foto Hermes**: Active
8. Workflow **Registrar Post Monitor**: Active
9. Workflow **Resposta Comentarios Post**: Active (poll ~2 min)
10. Hermes: Telegram pareado + scripts em `/opt/data/bin/` + env dos webhooks

## Workflows ativos

| Nome | ID | Tipo |
|------|-----|------|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | Schedule + Webhook |
| LinkedIn Salvar Texto Hermes | `aPTD3w3uZCuz11tP` | Webhook |
| LinkedIn Salvar Foto Hermes | `HIlMXIjvjjxwcGlo` | Webhook |
| LinkedIn Registrar Post Monitor | `1tqbFp0ft3GsxTgK` | Webhook |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | Schedule |

## Modelos / geração

| Uso | Stack |
|-----|--------|
| Post (texto) | Fila de textos (escrito manualmente + Hermes, sem LLM no n8n) |
| Post (imagem) | Foto real enviada via Telegram (fila `ready`) |
| Reply comentário | OpenCode Go `deepseek-v4-flash` |

## Validação rápida

1. No Telegram: `/salvar-texto` → confirma fila.
2. (Opcional) Enviar foto → `/salvar-foto` → confirma fila.
3. `/postar` → texto + foto (ou só texto) + auto-monitor.
4. Conferir Telegram de alerta: ok / skip (anti-dupe) / fail.
5. n8n Executions: origem **webhook** ou **schedule**.
6. Reply: aguardar poll ~2 min após comentário em post monitorado.

Detalhes de VPS: [VPS.md](VPS.md) · Tutorial: [TUTORIAL.md](TUTORIAL.md)
