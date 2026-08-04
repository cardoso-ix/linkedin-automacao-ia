# Apresentação — Automação LinkedIn (didático)

Timezone: **America/Sao_Paulo**  
Dois fluxos em produção: **post diário** + **resposta a comentários**.

## Dor (30s)

Especialista em IA precisa de presença constante no LinkedIn, mas escrever, diagramar, publicar e ainda responder comentários todo dia não escala. Sem sistema, a frequência cai e o engajamento esfria.

## Arquitetura em 2 fluxos

| Fluxo | O que acontece no n8n |
|-------|------------------------|
| **Post 08:00** | Tema Dia N → Qwen-Plus (texto) → qwen-image-2.0 (capa editorial, 8 estilos, sem texto) → LinkedIn IMAGE ou fallback só texto → Data Table + Telegram |
| **Reply ~2 min** | Sheets monitor → HTML do post → parse de comentários → Qwen-Flash → reply no LinkedIn → mark done |

```
08:00  Post Diario Texto (ysHFWIV0tGWJbhjo)
         anti-dupe → Dia N (1–30) → Qwen-Plus
         → capa qwen-image-2.0 (8 estilos) → LinkedIn
         → Telegram ok / skip / fail

*/2m   Resposta Comentarios Post (q28d2xJlAgvMpZ9Z)
         Sheets → HTML → parse → Qwen-Flash
         → HTTP reply → Sheets tracking
```

> **Fora do portfólio:** Resposta via Gmail — arquivado.

## O que abrir na tela

1. Post: https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo  
2. Reply: https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z  
3. Data Table **LinkedIn Posts Diario** (anti-dupe)  
4. Post + replies no LinkedIn (prova final)

## Fala-chave (1 min)

> “O Cursor foi onde eu desenhei o sistema. Em produção, o n8n orquestra dois fluxos: às 08:00 escolhe o tema do dia, gera o texto com Qwen-Plus na Alibaba Cloud (cota gratuita Singapore) e uma capa editorial com qwen-image-2.0 — ilustração abstrata sem texto, oito estilos em rotação — e publica no LinkedIn. Em paralelo, a cada dois minutos o segundo fluxo monitora posts recentes, lê os comentários no HTML e responde com Qwen-Flash, no tom da newsletter. Se a imagem falhar, o texto sai mesmo assim. Gmail de reply ficou no arquivo.”

## Como testar o post com imagem

1. Garantir que ainda **não** há post do dia em Posts Diario (senão skip)  
2. **Execute once** no workflow (ou esperar 08:00)  
3. Conferir LinkedIn + Telegram “Texto + capa qwen-image-2.0” (ou aviso só texto se fallback)  
4. Referência histórica: execução `5712` · `urn:li:share:7489362507237675008`

## Como testar a resposta a comentários

1. Abrir [Resposta Comentarios Post](https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z)  
2. Confirmar nó **Generate Reply Text** = Qwen-Flash (Alibaba)  
3. Comentar em um post monitorado (últimas 48h) ou **Execute once**  
4. Em ~2 min: reply publicado + linha marcada no Sheets  
5. Prompt: `prompts/resposta-comentario.json` · Skill: `skills/linkedin-resposta-comentario/`

## Stack em uma linha

n8n (VPS) · Alibaba Qwen-Plus · qwen-image-2.0 · Qwen-Flash · LinkedIn OAuth/REST · Sheets · Telegram
