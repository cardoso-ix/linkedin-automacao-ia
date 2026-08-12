---
name: salvar-texto
description: Salva texto validado no n8n Textos Agenda ready.
---

# LinkedIn salvar texto via n8n

## Regra OBRIGATÓRIA

Quando Eduardo **validar o texto** e pedir para salvar/enviar (`/salvar-texto`, `salva este texto`, `envia o texto pro n8n`, `enfileira o post`, `guarda esse copy`):

1. Use o **texto final validado** do chat (não regenere no n8n).
2. **SEMPRE** rode exatamente:
   `/opt/data/bin/salvar-texto-linkedin.sh --texto "<TEXTO>"`
3. Confirme só o resultado (`ok` / erro).

## Proibido

- Inventar `curl` manual com secret/header.
- Montar JSON na mão / arquivos `/tmp/texto_*.txt` improvisados.
- Dizer que salvou sem rodar o script e ver `OK texto enfileirado`.
- Expor `N8N_HERMES_WEBHOOK_SECRET`.
- Publicar neste passo — só enfileirar.

## Fluxo

1. Validar texto no Telegram.
2. `/salvar-texto` → script → Data Table **LinkedIn Textos Agenda** (`status=ready`).
3. (Opcional) `/salvar-foto`.
4. `/postar` → n8n usa a fila (não gera copy).
