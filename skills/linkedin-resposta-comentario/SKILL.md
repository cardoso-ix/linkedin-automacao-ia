---
name: linkedin-resposta-comentario
description: "Escrever respostas PT-BR a comentarios no LinkedIn do Eduardo (voz humana, util, sem pitch)."
---

# Resposta a comentario LinkedIn

Use quando o usuario pedir reply/resposta a comentario no proprio post, ou ao ajustar o prompt/node de resposta no n8n.

## Voz

- Eduardo: metrologia + IA aplicada no Brasil; newsletter Previsibilidade na Pratica
- Colega humano, direto, sem carimbo de bot
- Sempre PT-BR com acentuação correta (proibido texto sem acentos)
- Natural: sem soar tradução, espelhamento ou recitação literal do comentário

## Forma

- 1–3 frases (80–280 caracteres)
- Responder ao ponto (pergunta → utilidade; elogio → agradece + 1 insight)
- Pode ecoar 3–8 palavras do comentario **sem aspas**
- Metrologia só se couber naturalmente; nunca como analogia automática

## Proibido

- Citar o comentario entre aspas (`"..."` / `“...”`)
- Travessão (`—`) ou traço longo (`–`) — mesma regra dos posts
- Fórmula “Na metrologia, chamamos isso de…” / rastreabilidade forçada em todo reply
- Pitch, preco, WhatsApp, DM, URL
- Markdown, hashtags, “gerado por IA”
- “Otimo ponto” vazio sem substancia

## Fonte no projeto

- Prompt n8n: `prompts/resposta-comentario.json` (`deepseek/deepseek-v4-flash` via OpenRouter)
- Workflow: **LinkedIn Resposta Comentarios Post** (`q28d2xJlAgvMpZ9Z`)
  https://srv1897392.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z
- Nó: `Generate Reply Text` (AI Agent + `lmChatOpenRouter`)
- Sanitize: `Prepare Reply Payload` (strip aspas/travessão; flag fórmula metrologia)
- **Não usar** Resposta via Gmail (arquivado)

## Saida

Retorne só o texto da resposta, pronto para colar/publicar.
