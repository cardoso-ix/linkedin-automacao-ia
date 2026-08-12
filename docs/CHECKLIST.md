# Checklist — arquitetura ativa (Hermes + n8n)

## Antes de ativar

- [ ] Workflow **LinkedIn Post Diario Texto** (`ysHFWIV0tGWJbhjo`) — Active
- [ ] Schedule 08:00 (São Paulo) **habilitado** — post diário automático
- [ ] Webhook Hermes + secret alinhado com `.env` do container Hermes
- [ ] Hermes: `/postar`, `/postar-texto`, `/salvar-texto`, `/salvar-foto`, `/monitorar`
- [ ] Workflow **LinkedIn Salvar Texto Hermes** (`aPTD3w3uZCuz11tP`) — Active
- [ ] Workflow **LinkedIn Salvar Foto Hermes** (`HIlMXIjvjjxwcGlo`) — Active
- [ ] Workflow **LinkedIn Registrar Post Monitor** (`1tqbFp0ft3GsxTgK`) — Active
- [ ] Workflow **LinkedIn Resposta Comentarios Post** (`q28d2xJlAgvMpZ9Z`) — Active (poll ~2 min)
- [ ] Credencial **LinkedIn account** (OAuth) — token válido
- [ ] Credencial **OpenCode Go** — modelo `deepseek-v4-flash` (reply de comentários)
- [ ] Timezone `America/Sao_Paulo` configurado no `.env` do n8n
- [ ] Data Tables criadas: Textos Agenda, Imagens Agenda, Posts Monitor, Posts Diario

## Regras do post

- [ ] Sem markdown / asteriscos
- [ ] Sem URLs no corpo
- [ ] 1000–1800 caracteres (parágrafos corridos)
- [ ] Sem travessão / emojis / jargão vazio
- [ ] Entre 3 e 5 hashtags temáticas
- [ ] Fechar com reflexão ou convite leve ao comentário
- [ ] Imagem: foto real (Telegram), não gerada por IA

## Respostas a comentários

- [ ] Modelo: DeepSeek-V4-Flash via OpenCode Go
- [ ] Tom da skill `linkedin-resposta-comentario`
- [ ] Wait entre replies para não flood
- [ ] Posts monitorados < 48h (após isso, saem do poll)

## Validação rápida

1. `/salvar-texto` → fila com `status=ready`
2. `/salvar-foto` → fila com `status=ready`
3. `/postar` → texto + foto (ou só texto) + alerta Telegram + auto-monitor
4. `/postar-texto` → só texto
5. `/monitorar <url>` → linha no Posts Monitor
6. Conferir Executions: origem **webhook** ou **schedule**
7. Aguardar poll ~2 min para reply automático em posts monitorados
