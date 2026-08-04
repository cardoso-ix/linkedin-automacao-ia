# Tutorial rápido — LinkedIn automação (Alibaba)

## O que o sistema faz

1. Post automático às **08:00** (texto Qwen-Plus + capa qwen-image-2.0; fallback só texto)
2. Resposta automática a comentários (Sheets + HTML, poll 2 min) com **Qwen-Flash**

## Post diário

1. Abra https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo
2. Confira credenciais **Alibaba Model Studio** (texto + imagem) + **LinkedIn**
3. **Execute once** (teste) — deve gerar texto com `qwen-plus`, capa com `qwen-image-2.0` e publicar
4. Se já postou hoje → Telegram **skip**
5. Se a capa falhar → publica só texto (fallback)

## Resposta a comentários

1. Abra https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z
2. Confira **Generate Reply Text** → modelo Alibaba `qwen-flash`
3. Credencial **Alibaba Model Studio** + LinkedIn
4. Comente em um post monitorado ou Execute once
5. Em ~2 min: reply + mark done no Sheets

## Se der erro `AccessDenied.Unpurchased`

1. Console Alibaba → Model Studio **Singapore**
2. Liberar o modelo na cota gratuita
3. Retestar no n8n

## Lembretes

- Credencial Alibaba cobre texto do post, capa e reply
- Sempre **Publish** depois de editar o canvas
- API key fica só no n8n — nunca no repositório
- Detalhes: [SETUP.md](SETUP.md) · [FLUXO.md](FLUXO.md)
