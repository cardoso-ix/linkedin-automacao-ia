# Tutorial rápido — do zero

## O que você tem

1. Post automático às **08:00** (texto DeepSeek + capa FLUX.2 Pro; fallback só texto)
2. Resposta automática a comentários (Sheets + HTML, poll 2 min) com **DeepSeek-V4-Flash**

## Ativar o post diário

1. Abra [LinkedIn Post Diario Texto](https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo)
2. Confira credenciais **OpenRouter** (texto + imagem) + **LinkedIn**
3. **Execute once** (teste) — deve gerar texto com DeepSeek-V4-Flash, capa com FLUX.2 Pro e publicar
4. Se a capa falhar, o fluxo publica só o texto (comportamento esperado)
5. Se ok, deixe o workflow **Active** (após Publish do draft)

## Respostas a comentários (sem Gmail)

1. Abra [LinkedIn Resposta Comentarios Post](https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z)
2. Confira **Generate Reply Text** → modelo OpenRouter `deepseek/deepseek-v4-flash`
3. Credencial **OpenRouter account** + LinkedIn
4. Deixe **Active** (após Publish)
5. Peça a outra pessoa para comentar em um post monitorado (últimas 48h)
6. Em ~2 min o n8n deve gerar e publicar o reply

## Temas

Lista de 30 temas em [TEMAS.md](TEMAS.md). **Dia N = tema N** (`dayOfMonth`; dia 31 → tema 1).

## Cuidados

- Workflows ativos: Post Diario Texto + Resposta Comentarios Post
- Resposta via Gmail está **arquivado**
- Sempre PT-BR nos posts e replies
- Credencial OpenRouter cobre texto do post, capa e reply
- Stack free (catálogo) é **opcional** — ver [STACK-GRATUITA.md](STACK-GRATUITA.md)
