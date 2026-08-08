# Checklist — arquitetura ativa (Hermes + n8n)

## Antes de ativar

- [ ] Workflow **LinkedIn Post Diario Texto** (`ysHFWIV0tGWJbhjo`) — OpenRouter (texto + capa) + LinkedIn
- [ ] Nó **Daily 8h Sao Paulo** **desabilitado** (post só via Hermes)
- [ ] Webhook Hermes + secret alinhado com `.env` do container Hermes
- [ ] Hermes: `/postar` e `/postar-texto` + skill `linkedin-post-n8n`
- [ ] Workflow **LinkedIn Resposta Comentarios Post** (`q28d2xJlAgvMpZ9Z`) — DeepSeek + Sheets/HTML + LinkedIn
- [ ] Credencial **OpenRouter account** (texto, FLUX, reply)
- [ ] Modelos: `deepseek/deepseek-v4-flash` + `black-forest-labs/flux.2-pro`
- [ ] Resposta via Gmail permanece **arquivado**
- [ ] Timezone `America/Sao_Paulo`
- [ ] Data Table **LinkedIn Posts Diario** ok (anti-dupe; `force=1` bypass)
- [ ] Draft publicado (**Publish**) após mudanças no canvas

## Regras do post

- [ ] Sem markdown / asteriscos
- [ ] Sem URLs no corpo
- [ ] 1000–1800 caracteres (parágrafos corridos)
- [ ] Sem travessão / emojis / jargão vazio
- [ ] Entre 3 e 5 hashtags temáticas
- [ ] Fechar com reflexão ou convite leve ao comentário
- [ ] Capa **sem texto, sem letras e sem números** (mode=full; 8 estilos round-robin)

## Respostas a comentários

- [ ] Generate Reply Text = DeepSeek-V4-Flash (OpenRouter)
- [ ] Tom da skill `linkedin-resposta-comentario`
- [ ] Wait 20s entre replies
- [ ] Confirmar reply no LinkedIn + mark done no Sheets

## Validação rápida

1. Telegram `/postar` → texto + capa (ou fallback só texto)
2. Telegram `/postar-texto` → só texto
3. Conferir Executions: origem **webhook**
4. Aguardar poll ~2 min no fluxo de comments (ou Execute once)
5. Mudanças no canvas ficam em **draft** até Publish
