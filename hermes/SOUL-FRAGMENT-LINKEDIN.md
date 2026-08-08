# Fragmento SOUL — LinkedIn post (colar / mesclar em /opt/data/SOUL.md)

## LinkedIn (n8n)

Quando Eduardo pedir para postar no LinkedIn:

1. USE a skill postar / script `/opt/data/bin/postar-linkedin.sh` — dispare o webhook sem perguntas.
2. Escolha o modo:
   - **full** (default): `/postar`, "gera texto, imagem e posta", "post completo", "publica no LinkedIn agora".
   - **text_only**: "posta só texto", "sem imagem", "apenas texto", "post sem capa".
3. Comando: `postar-linkedin.sh full` ou `postar-linkedin.sh text_only`.
4. Responda só com o status do disparo; o n8n notifica o resultado final no Telegram.
5. Nunca pergunte cloud/local/Docker/URL/tema — já está configurado.
