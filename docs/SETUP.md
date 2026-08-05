# Setup — n8n VPS

Este projeto roda no **n8n** (VPS Hostinger).

## Passos

1. Abrir https://srv1824850.hstgr.cloud/
2. Confirmar credencial **LinkedIn account**
3. Confirmar credencial **OpenRouter account** — texto (DeepSeek), capa (FLUX) e reply (DeepSeek)
4. Fluxos: ver [FLUXO.md](FLUXO.md)
5. Ativar os workflows da tabela abaixo
6. Manter **Resposta via Gmail** arquivado

## Workflows ativos

| Nome | ID | URL |
|------|-----|-----|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z |

## Modelos / geração

| Uso | Stack |
|-----|--------|
| Post diário (texto) | OpenRouter **`deepseek/deepseek-v4-flash`** |
| Post diário (capa) | OpenRouter **`black-forest-labs/flux.2-pro`** (`/api/v1/images`) |
| Reply comentário | OpenRouter **`deepseek/deepseek-v4-flash`** |

## MCP (para o agent editar o canvas de comments)

No workflow **LinkedIn Resposta Comentarios Post** → Settings → **Available in MCP** = ON → Save.

## Validação rápida

1. Execute once no Post Diario (ou esperar 08:00 SP).
2. Conferir Telegram: ok com capa, skip (anti-dupe) ou aviso só texto.
3. No fluxo de comments: Generate Reply Text com DeepSeek → reply no LinkedIn.

Detalhes de VPS: [VPS.md](VPS.md) · Tutorial: [TUTORIAL.md](TUTORIAL.md)  
Stack free (**opcional / legado**): [STACK-GRATUITA.md](STACK-GRATUITA.md)
