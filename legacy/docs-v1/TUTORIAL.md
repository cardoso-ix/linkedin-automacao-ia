# Tutorial rápido — do zero

## O que você tem

1. **Assistente Hermes** no Telegram — você manda o comando; ele dispara o n8n (**sem** post automático às 08:00)
2. Post LinkedIn: texto DeepSeek + capa FLUX.2 Pro (`/postar`) **ou** só texto (`/postar-texto`)
3. Resposta automática a comentários (Sheets + HTML, poll ~2 min) com DeepSeek-V4-Flash

## Postar pelo Telegram

1. Abra o bot Hermes (`@funcionario_vip_bot`)
2. `/postar` → texto + capa  
   `/postar-texto` → só texto
3. Aguarde a notificação do n8n no Telegram de alerta
4. Confira Executions em [Post Diario Texto](https://srv1897392.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo) (origem webhook)

Detalhes: [HERMES-ASSISTENTE.md](HERMES-ASSISTENTE.md)

## Conferir o workflow de post no n8n

1. Abra [LinkedIn Post Diario Texto](https://srv1897392.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo)
2. Credenciais **OpenRouter** (texto + imagem) + **LinkedIn**
3. Nó **Daily 8h Sao Paulo** deve estar **desabilitado**
4. Workflow **Active** (após Publish do draft)

## Respostas a comentários (sem Gmail)

1. Abra [LinkedIn Resposta Comentarios Post](https://srv1897392.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z)
2. **Generate Reply Text** → `deepseek/deepseek-v4-flash`
3. Credencial **OpenRouter account** + LinkedIn
4. Deixe **Active** (após Publish)
5. Comente em um post monitorado (últimas 48h)
6. Em ~2 min o n8n gera e publica o reply

## Temas

Lista de 30 temas em [TEMAS.md](TEMAS.md). **Dia N = tema N** (`dayOfMonth`; dia 31 → tema 1).

## Cuidados

- Post só sob comando Hermes; schedule 08:00 OFF
- Resposta via Gmail arquivado
- Sempre PT-BR nos posts e replies
- OpenRouter cobre texto, capa e reply
- Stack free (catálogo) é **opcional** — [STACK-GRATUITA.md](STACK-GRATUITA.md)
