# Fluxo — arquitetura ativa (Hermes + n8n)

Timezone: **America/Sao_Paulo**

## Modelo operacional

| Camada | Papel |
|--------|--------|
| **Hermes** (Telegram) | Assistente: você comanda; ele enfileira texto/foto e dispara o post |
| **n8n** | Braço operacional: publica no LinkedIn, responde comentários automaticamente |

**Post sob comando (Hermes no Telegram).** Schedule 08:00 **OFF**.

## Workflows ativos (n8n)

| Workflow | ID | Disparo |
|----------|-----|---------|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | Webhook Hermes (schedule OFF) |
| LinkedIn Salvar Texto Hermes | `aPTD3w3uZCuz11tP` | Webhook (texto da fila) |
| LinkedIn Salvar Foto Hermes | `HIlMXIjvjjxwcGlo` | Webhook (foto da fila) |
| LinkedIn Registrar Post Monitor | `1tqbFp0ft3GsxTgK` | Webhook (monitorar post manual) |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | Schedule ~2 min (automático) |

## 1) Post LinkedIn (schedule + comando)

**Workflow:** LinkedIn Post Diario Texto · ID `ysHFWIV0tGWJbhjo`

**Disparos:** Hermes → webhook (schedule 08:00 OFF).

```
Telegram /postar (via Hermes)
  → Lê texto ready em LinkedIn Textos Agenda
  → Se não houver texto → aborta + alerta Telegram
  → Anti-dupe (bypass se force=1)
  → IF Text Only Mode
       text_only / sem_imagem → Post Text Only
       full → Lê foto ready em LinkedIn Imagens Agenda
              → foto encontrada → Post With Image
              → sem foto → Post Text Only (fallback)
  → Marca texto/foto como "used"
  → Registra no LinkedIn Posts Monitor (auto-monitor)
  → Notifica Telegram (sucesso / erro)
```

- **Texto:** fila `ready` em LinkedIn Textos Agenda (texto validado pelo usuário, sem LLM)
- **Imagem:** foto própria criada pelo usuário, enviada via Telegram
- **Reply model:** DeepSeek-V4-Flash via API LinkedIn

## 2) Salvar texto (Hermes → fila)

**Workflow:** LinkedIn Salvar Texto Hermes · ID `aPTD3w3uZCuz11tP`

```
Telegram → Hermes → POST /webhook/hermes-linkedin-texto
  → Valida secret + texto (50–3000 chars)
  → Supersede ready anterior (source=hermes)
  → Insert LinkedIn Textos Agenda (status=ready)
  → Responde { ok: true, charCount }
```

## 3) Salvar foto (Hermes → fila)

**Workflow:** LinkedIn Salvar Foto Hermes · ID `HIlMXIjvjjxwcGlo`

```
Telegram → Hermes → POST /webhook/hermes-linkedin-foto
  → Valida secret + base64
  → Grava imagem no disco n8n
  → Insert LinkedIn Imagens Agenda (status=ready)
  → Responde { ok: true, filePath }
```

## 4) Registrar post manual para monitorar

**Workflow:** LinkedIn Registrar Post Monitor · ID `1tqbFp0ft3GsxTgK`

```
Telegram → Hermes → POST /webhook/hermes-linkedin-monitor
  → Parse URL/URN do LinkedIn
  → Upsert LinkedIn Posts Monitor (status=monitoring)
  → Responde { ok: true, postUrl }
```

## 5) Resposta a comentários (automático)

**Workflow:** LinkedIn Resposta Comentarios Post · ID `q28d2xJlAgvMpZ9Z`

```
Every 2 min (schedule)
  → Lê LinkedIn Posts Monitor (frescos < 48h)
  → Busca comentários via API LinkedIn (HTML)
  → Filtra novos (não respondidos)
  → DeepSeek-V4-Flash gera reply
  → Posta reply no LinkedIn
  → Marca como respondido
```

Não passa pelo Hermes. Prompt: [`prompts/resposta-comentario.json`](../prompts/resposta-comentario.json).

## Data Tables (n8n)

| Tabela | Função |
|--------|--------|
| **LinkedIn Textos Agenda** | Fila de textos (`ready` → `used`) |
| **LinkedIn Imagens Agenda** | Fila de fotos (`ready` → `used`) |
| **LinkedIn Posts Monitor** | Posts monitorados para auto-reply |
| **LinkedIn Posts Diario** | Histórico / anti-dupe |

## Diagrama geral

```
Você (Telegram)
  → Hermes (assistente)
      → /salvar-texto  → webhook → Textos Agenda (ready)
      → /salvar-foto   → webhook → Imagens Agenda (ready)
      → /postar        → webhook → texto ready + foto ready → LinkedIn
      → /monitorar URL → webhook → Posts Monitor

(sem schedule automático — post só via comando Hermes)

*/2m (automático, sem Hermes):
  Posts Monitor → API LinkedIn → parse comentários
  → DeepSeek-V4-Flash → reply LinkedIn
```

## Stack

| Camada | Tecnologia |
|--------|------------|
| Assistente | Hermes Agent (Docker na VPS) + Telegram |
| Orquestração | n8n (VPS Hostinger KVM 2) |
| Reply IA | DeepSeek-V4-Flash via API LinkedIn |
| Publicação | LinkedIn OAuth + REST |
| Memória | Data Tables n8n |
| Alertas | Telegram Bot |
