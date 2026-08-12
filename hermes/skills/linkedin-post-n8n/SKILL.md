---
name: postar
description: Dispara o pipeline LinkedIn no n8n (texto da fila + foto da fila, ou só texto) via webhook Hermes. Use quando o usuário pedir para postar no LinkedIn.
---

# LinkedIn post via n8n

## Quando usar

Eduardo pede post no LinkedIn pelo Telegram. **Não pergunte** tema, canal, cloud/local/URL — dispare o script.

## Pré-requisito

O **texto** deve estar na fila (`/salvar-texto`) **antes** do `/postar`. Sem texto ready, o n8n aborta e avisa no Telegram.

Foto é opcional: `/salvar-foto` antes do `/postar` (mode full).

## Dois modos (ambos válidos)

| Intenção do usuário | Mode | Comando |
|---------------------|------|---------|
| `/postar`, "posta agora", "post completo", "publica no LinkedIn agora", "roda o post diario agora" | `full` (default) | `/opt/data/bin/postar-linkedin.sh full` |
| "posta só texto", "sem imagem", "apenas texto", "post sem capa", "só texto" | `text_only` | `/opt/data/bin/postar-linkedin.sh text_only` |

- **full**: usa texto `ready` da fila + foto `ready` se houver. Sem foto → só texto.
- **text_only**: usa texto `ready`; **ignora** a fila de foto.

Se a frase for ambígua, use **full**.

## Ordem típica

1. Gerar/validar texto no Telegram → `/salvar-texto`
2. (Opcional) foto → `/salvar-foto`
3. `/postar` quando quiser publicar

## Execução

1. Rode o script correspondente (não invente curl com secret).
2. Responda só com o resultado (sucesso / skip anti-dupe / erro / "processando, n8n notifica ao fim").
3. O script já envia `"force": 1` e `"mode": "full"|"text_only"`.

## Depois de postar

O workflow n8n de post **já** faz upsert na Data Table **LinkedIn Posts Monitor**. Não chame `/monitorar` após um `/postar` bem-sucedido.

Para post **manual** (link colado), use a skill `monitorar`.

## Não fazer

- Não gerar o texto no n8n — o texto vem da fila Telegram.
- Não gerar capa FLUX.
- Não pedir esclarecimentos desnecessários.
- Não expor `N8N_HERMES_WEBHOOK_SECRET`.
