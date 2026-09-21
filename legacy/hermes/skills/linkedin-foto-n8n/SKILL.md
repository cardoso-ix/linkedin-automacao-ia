---
name: salvar-foto
description: Enfileira foto do Telegram para o próximo post LinkedIn via webhook n8n. Use quando Eduardo enviar uma foto / pedir para salvar/usar no próximo post.
---

# LinkedIn salvar foto via n8n

## Regra

Quando Eduardo **enviar uma foto** no Telegram (ou pedir "salva esta foto", "usa no próximo post", "enfileira a imagem"):

1. Salve o anexo em disco (caminho local acessível).
2. Rode: `/opt/data/bin/salvar-foto-linkedin.sh --file "<PATH>"` (opcional `--tema "legenda"`).
3. Confirme só o resultado (`ok` / erro). **Não** invente curl com secret.

## Quando usar

- Foto anexada + pedido implícito ou explícito de usar no post
- `/salvar-foto`
- "salva esta foto", "usa no próximo post", "foto para o LinkedIn", "enfileira a imagem"

## Quando NÃO usar

- Pedido de **publicar agora** sem foto nova → skill `postar` (`/postar`)
- Só texto → `/postar-texto` (ignora a fila de foto)

## Fluxo depois

1. n8n grava a foto e cria linha em **LinkedIn Imagens Agenda** com `status=ready`.
2. No `/postar` (mode full), o n8n usa o **texto ready** da fila e anexa a foto `ready` (não gera texto nem FLUX).
3. `/postar-texto` **ignora** a fila de foto.

## Não fazer

- Não gerar capa com IA no Hermes.
- Não expor `N8N_HERMES_WEBHOOK_SECRET`.
- Não postar no LinkedIn neste passo — só enfileirar.
