# Fluxo — arquitetura ativa (Hermes + n8n)

Timezone: **America/Sao_Paulo**

## Modelo operacional

| Camada | Papel |
|--------|--------|
| **Hermes** (Telegram) | Assistente: você comanda; ele dispara o post |
| **n8n** | Braço operacional: gera, publica, responde comentários |

**Post sob comando apenas.** Schedule 08:00 **OFF**. Detalhes: [HERMES-ASSISTENTE.md](HERMES-ASSISTENTE.md).

## Workflows em uso (n8n)

| Workflow | ID | Status |
|----------|-----|--------|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | **ATIVO** — só webhook Hermes (schedule OFF) |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | **ATIVO** — poll ~2 min |

> **Arquivado:** LinkedIn Resposta via Gmail (`5xkPzzTcKwdsPymn`).

## 1) Post LinkedIn sob comando (Hermes → n8n)

**Workflow:** [LinkedIn Post Diario Texto](https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo) · ID `ysHFWIV0tGWJbhjo`

**Disparo:** Telegram → Hermes → webhook. Nó **Daily 8h Sao Paulo** desativado.

```
Telegram ( /postar | /postar-texto | frase )
  → Hermes (script/skill)
  → Hermes Webhook (secret)
  → Get Recent Posts → anti-dupe (bypass se force=1)
  → Build Theme Context (Dia N = tema N; 1–30)
  → Generate Post Text (DeepSeek-V4-Flash) → Sanitize
  → IF Text Only Mode
       text_only / sem_imagem → Post Text Only
       full → Build Cover Prompt → FLUX.2 Pro → Post With Image
              (fallback Post Text Only se capa falhar)
  → Save Posted Row → Telegram alerta
```

- **Texto:** `deepseek/deepseek-v4-flash`  
- **Imagem:** `black-forest-labs/flux.2-pro`  
- Temas: [TEMAS.md](TEMAS.md) · Capas: [IMAGENS-LOTE.md](IMAGENS-LOTE.md)

## 2) Resposta a comentários (automático)

**Workflow:** [LinkedIn Resposta Comentarios Post](https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z)

```
Every 2 min
  → Sheets monitor → HTML → parse comentários
  → DeepSeek-V4-Flash → Post LinkedIn Reply → mark done
```

Não passa pelo Hermes. Prompt: [`prompts/resposta-comentario.json`](../prompts/resposta-comentario.json).

## Data Tables / Sheets

| Recurso | Uso |
|---------|-----|
| **LinkedIn Posts Diario** | Memória / anti-dupe (`force=1` bypass) |
| Google Sheets (monitor + already replied) | Fila do fluxo de comments |

## Legado

Stack gratuita: [STACK-GRATUITA.md](STACK-GRATUITA.md) — **não** é o default.
