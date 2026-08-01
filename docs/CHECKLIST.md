# Checklist — arquitetura ativa

## Antes de ativar

- [ ] Workflow **LinkedIn Post Diario Texto** (`ysHFWIV0tGWJbhjo`) — OpenRouter (texto + capa) + LinkedIn
- [ ] Workflow **LinkedIn Resposta Comentarios Post** (`q28d2xJlAgvMpZ9Z`) — DeepSeek OpenRouter + Sheets/HTML + LinkedIn
- [ ] Credencial **OpenRouter account** no DeepSeek (post e reply) **e** no nó Generate Cover Flux Pro
- [ ] Modelos: `deepseek/deepseek-v4-flash` + `black-forest-labs/flux.2-pro`
- [ ] Stickies de reply sem menção a GPT-3.5 (usar DeepSeek-V4-Flash)
- [ ] Resposta via Gmail permanece **arquivado**
- [ ] Timezone `America/Sao_Paulo`
- [ ] Schedule post: `0 8 * * *`
- [ ] Data Table **LinkedIn Posts Diario** ok (anti-dupe)
- [ ] Draft publicado (**Publish**) após mudanças no canvas

## Regras do post

- [ ] Sem markdown / asteriscos
- [ ] Sem URLs no corpo
- [ ] 1000–1800 caracteres (parágrafos corridos)
- [ ] Sem travessão / emojis / jargão vazio
- [ ] No máximo 3 hashtags (opcionais)
- [ ] Fechar com reflexão ou convite leve ao comentário
- [ ] Capa **sem texto** na arte (8 estilos round-robin)

## Respostas a comentários

- [ ] Generate Reply Text = DeepSeek-V4-Flash (OpenRouter)
- [ ] Tom da skill `linkedin-resposta-comentario`
- [ ] Wait 20s entre replies
- [ ] Confirmar reply no LinkedIn + mark done no Sheets

## Validação rápida

1. Executar **Post Diario Texto** (1x) — ou conferir skip se já postou hoje
2. Conferir Telegram: “Texto + capa FLUX.2 Pro” (ou aviso só texto se fallback)
3. Executar **Resposta Comentarios Post** (1x) ou aguardar poll 2 min
4. Conferir Executions no n8n
5. Lembrete: mudanças no canvas ficam em **draft** até Publish
