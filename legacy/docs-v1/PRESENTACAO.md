# Apresentação — Automação LinkedIn (didático)

Timezone: **America/Sao_Paulo**  
Em produção: **Hermes (assistente Telegram)** + **n8n** (post sob comando + reply automático).

## Dor (30s)

Especialista em IA precisa de presença constante no LinkedIn, mas escrever, diagramar, publicar e ainda responder comentários todo dia não escala. Sem sistema, a frequência cai e o engajamento esfria.

## Arquitetura

| Camada | O que faz |
|--------|-----------|
| **Hermes** | Assistente no Telegram: `/postar` ou `/postar-texto` dispara o pipeline |
| **n8n Post** | Tema Dia N → DeepSeek → (opcional) FLUX capa → LinkedIn → Telegram |
| **n8n Reply ~2 min** | Sheets → HTML → DeepSeek → reply LinkedIn |

**Sem cron de post às 08:00** — você decide quando publicar.

```
Telegram → Hermes → webhook n8n (ysHFWIV0tGWJbhjo)
         anti-dupe → Dia N → DeepSeek → capa ou só texto → LinkedIn

*/2m   Resposta Comentarios (q28d2xJlAgvMpZ9Z)
         Sheets → HTML → DeepSeek → reply
```

> **Fora do portfólio:** Resposta via Gmail — arquivado.  
> Detalhe do assistente: [HERMES-ASSISTENTE.md](HERMES-ASSISTENTE.md)

## O que abrir na tela

1. Post: https://srv1897392.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo  
2. Reply: https://srv1897392.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z  
3. Data Table **LinkedIn Posts Diario** (anti-dupe)  
4. Telegram Hermes + post/replies no LinkedIn (prova final)

## Fala-chave (1 min)

> “Desenhei o sistema no Cursor. Em produção, o Hermes no Telegram é meu assistente: eu mando postar e ele dispara o n8n. O n8n escolhe o tema do dia, gera o texto com DeepSeek-V4-Flash via OpenRouter e, se eu pedir o post completo, uma capa editorial com FLUX.2 Pro — sem tipografia na arte. Também posso pedir só texto. Em paralelo, a cada dois minutos o segundo fluxo lê comentários e responde com o mesmo DeepSeek. Não tem post automático de manhã — eu controlo o timing pelo Telegram.”

## Como testar o post

1. No Telegram: `/postar` (completo) ou `/postar-texto`  
2. Conferir LinkedIn + alerta Telegram  
3. n8n Executions com origem **webhook**

## Como testar a resposta a comentários

1. Abrir [Resposta Comentarios Post](https://srv1897392.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z)  
2. **Generate Reply Text** = DeepSeek-V4-Flash  
3. Comentar em post monitorado ou **Execute once**  
4. Em ~2 min: reply + mark done no Sheets

## Stack em uma linha

Hermes (Telegram) · n8n (VPS) · OpenRouter DeepSeek-V4-Flash · FLUX.2 Pro · LinkedIn · Sheets · Telegram alerta
