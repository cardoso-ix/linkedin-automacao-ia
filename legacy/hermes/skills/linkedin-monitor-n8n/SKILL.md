---
name: monitorar
description: Registra URL/URN de post LinkedIn (manual) na Data Table LinkedIn Posts Monitor via webhook n8n. Use quando Eduardo colar o link do post ou pedir para monitorar/acompanhar comentários.
---

# LinkedIn monitorar via n8n

## Regra obrigatória

Se Eduardo **postou manualmente** (app LinkedIn) e manda o link / pede para monitorar / acompanhar comentários:

1. **SEMPRE** rode o script de registro.
2. O destino é a Data Table **LinkedIn Posts Monitor** (`status=monitoring`).
3. **Nunca** só confirme verbalmente sem chamar o webhook — sem a linha na tabela o reply automático não cobre o post.

## Quando usar

- `/monitorar <url>`
- "monitora este post", "acompanha os comentários", "salva o link", "registra no monitor"
- Mensagem que contém `linkedin.com/posts/` ou `linkedin.com/feed/update/` ou `urn:li:activity:`

## Quando NÃO usar

- Pedido de **criar/publicar** post novo → use a skill `postar` (`/postar` / `/postar-texto`). O workflow de post **já** grava no Monitor sozinho.

## Execução

1. Extraia a URL (ou URN) da mensagem.
2. Rode: `/opt/data/bin/monitorar-linkedin.sh "<URL>"`
3. Opcional: `--tema "..."` / `--texto "..."` se Eduardo passar contexto.
4. Responda só com o resultado (ok / erro). Não invente curl com secret.

## Não fazer

- Não pular o registro "porque o post já existe no LinkedIn".
- Não gerar reply de comentário no Hermes — o n8n (`LinkedIn Resposta Comentarios Post`) faz isso.
- Não expor `N8N_HERMES_WEBHOOK_SECRET`.
