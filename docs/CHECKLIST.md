# Checklist — arquitetura ativa (Alibaba Model Studio)

## Antes de ativar

- [ ] Cota gratuita Singapore liberada: `qwen-plus`, `qwen-flash`, `qwen-image-2.0`
- [ ] **Free Quota Only** ligado (opcional, evita cobrança além da cota)
- [ ] Workflow **LinkedIn Post Diario Texto** (`ysHFWIV0tGWJbhjo`) — Alibaba (texto + capa) + LinkedIn
- [ ] Workflow **LinkedIn Resposta Comentarios Post** (`q28d2xJlAgvMpZ9Z`) — Qwen-Flash + Sheets/HTML + LinkedIn
- [ ] Credencial **Alibaba Model Studio** no chat (post e reply) **e** no HTTP da capa
- [ ] Base URL chat: `…/compatible-mode/v1` · imagem: `…/multimodal-generation/generation`
- [ ] Stickies de reply sem menção a GPT-3.5 / OpenRouter / DeepSeek
- [ ] Resposta via Gmail permanece **arquivado**
- [ ] Timezone `America/Sao_Paulo`
- [ ] Schedule post: `0 8 * * *`
- [ ] Data Table **LinkedIn Posts Diario** ok (anti-dupe)
- [ ] Draft publicado (**Publish**) após mudanças no canvas
- [ ] API key **não** está no GitHub (só no n8n)

## Regras do post

- [ ] Sem markdown / asteriscos
- [ ] Sem URLs no corpo
- [ ] 1000–1800 caracteres (parágrafos corridos)
- [ ] Sem travessão / emojis / jargão vazio
- [ ] No máximo 3 hashtags (opcionais)
- [ ] Fechar com reflexão ou convite leve ao comentário
- [ ] Capa **sem texto** na arte (8 estilos round-robin)

## Respostas a comentários

- [ ] Generate Reply Text = Qwen-Flash (Alibaba)
- [ ] Tom da skill `linkedin-resposta-comentario`
- [ ] Wait 20s entre replies
- [ ] Confirmar reply no LinkedIn + mark done no Sheets

## Validação rápida

1. Ping `qwen-plus` no n8n — se `Unpurchased`, liberar no console
2. Executar **Post Diario Texto** (1x) — ou conferir skip se já postou hoje
3. Conferir Telegram: “Texto + capa qwen-image-2.0” (ou aviso só texto se fallback)
4. Executar **Resposta Comentarios Post** (1x) ou aguardar poll 2 min
5. Conferir Executions no n8n
6. Lembrete: mudanças no canvas ficam em **draft** até Publish
