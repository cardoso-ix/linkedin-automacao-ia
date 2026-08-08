---
name: postar
description: Dispara o pipeline LinkedIn no n8n (texto+capa ou só texto) via webhook Hermes. Use quando o usuário pedir para postar no LinkedIn.
---

# LinkedIn post via n8n

## Quando usar

Eduardo pede post no LinkedIn pelo Telegram. **Não pergunte** tema, canal, cloud/local/URL — dispare o script.

## Dois modos (ambos válidos)

| Intenção do usuário | Mode | Comando |
|---------------------|------|---------|
| `/postar`, "gera texto, imagem e posta", "post completo", "publica no LinkedIn agora", "roda o post diario agora" | `full` (default) | `/opt/data/bin/postar-linkedin.sh full` |
| "posta só texto", "sem imagem", "apenas texto", "post sem capa", "só texto" | `text_only` | `/opt/data/bin/postar-linkedin.sh text_only` |

Se a frase for ambígua, use **full**.

## Execução

1. Rode o script correspondente (não invente curl com secret).
2. Responda só com o resultado (sucesso / skip anti-dupe / erro / "processando, n8n notifica ao fim").
3. O script já envia `"force": 1` e `"mode": "full"|"text_only"`.

## Não fazer

- Não gerar o texto/imagem no Hermes — o n8n faz isso.
- Não pedir esclarecimentos desnecessários.
- Não expor `N8N_HERMES_WEBHOOK_SECRET`.
