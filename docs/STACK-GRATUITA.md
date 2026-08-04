# Stack 100% gratuita — Post diário LinkedIn (**opcional / legado**)

Timezone: **America/Sao_Paulo**  
Workflow: [LinkedIn Post Diario Texto](https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo) (`ysHFWIV0tGWJbhjo`)

> **Status (2026-08-04):** isto **não** é o default.  
> Em produção o post diário usa **Alibaba Qwen-Plus + qwen-image-2.0** (cota gratuita Singapore).  
> Use este doc só se a cota Alibaba acabar e precisar de fallback com catálogo de imagens.

## O que “tudo gratuito” significa na prática

| Peça | Caminho catálogo (legado) | Produção atual (cota Alibaba) |
|------|---------------------------|-------------------------------|
| Texto | Template no n8n **ou** Gemini free tier | Qwen-Plus |
| Imagem | Catálogo `LinkedIn Imagens Agenda` (URL pública) | qwen-image-2.0 |
| Alertas | Telegram (já no fluxo) | Telegram |

## Comparação rápida (2 opções legadas)

### A — Template + catálogo
- **Prós:** zero chave nova; imagem com qualidade controlada (você gera offline).
- **Contras:** texto menos “único” que LLM; exige URLs públicas na agenda.
- **Quando usar:** cota Alibaba esgotada/`Unpurchased` e precisa publicar amanhã.

### B — Gemini free + catálogo
- **Prós:** texto mais variado; ainda free (cota Google AI Studio).
- **Contras:** precisa credencial `googlePalmApi`; cota free pode 429.
- **Quando usar:** depois de criar a key em [Google AI Studio](https://aistudio.google.com/apikey).

## Fluxo legado (modo free)

```
08:00
  → anti-dupe (LinkedIn Posts Diario)
  → Build Theme Context (Dia N = tema N, 30/mês)
  → Generate Post Text Free (template Code)
  → Sanitize Post Text
  → Get Catalog Images (LinkedIn Imagens Agenda)
  → Pick Catalog Image
       tem URL? → Download → Post With Image
       sem URL? → Post Text Only
  → Save + Telegram
```

No modo free, os nós pagos/LLM de imagem (`Generate Post Text` / `Generate Cover Qwen Image`) ficam **desligados**.

## Setup (só se religar o modo free)

### 1) Imagens no catálogo

1. Gerar/exportar PNGs 1:1 (capa editorial sem texto — ver [IMAGENS-LOTE.md](IMAGENS-LOTE.md)).
2. Hospedar em URL **pública HTTPS**.
3. Preencher a data table **LinkedIn Imagens Agenda** (`iuKvPfKaSd77gl4H`).

Sem `imageUrl`, o fluxo publica **só texto**.

Arquivos locais em `assets/posts/` **não** entram sozinhos no LinkedIn — o n8n na VPS precisa de URL baixável.

### 2) (Opcional) Gemini free para texto

1. Criar API key em https://aistudio.google.com/apikey  
2. No n8n: Credentials → **Google Gemini (PaLM) API**  
3. Trocar o node de texto template por Gemini Flash  
4. Manter Sanitize + Telegram + catálogo de imagem  
5. **Publish** o draft

## Como validar (modo free)

1. Na data table, garantir 1 linha com `imageUrl` válida para a data de teste.
2. Executar manualmente o workflow.
3. Conferir Telegram: sucesso com capa do catálogo ou aviso só texto.
4. Segunda execução no mesmo dia → skip + Telegram anti-dupe.

## Riscos / cuidados

- Religar free **desliga** DeepSeek/FLUX — documente a troca e publique o draft.
- URL de imagem precisa permitir GET anônimo.
- Não commitar API keys.

## Scripts (recriar nós free se precisar)

- `scripts/n8n-generate-post-text-free.js` → Generate Post Text Free  
- `scripts/n8n-pick-catalog-image.js` → Pick Catalog Image  
- `scripts/n8n-check-catalog-image.js` → Check Cover Ready (legado catálogo)  

## Estado

- **Default em produção:** DeepSeek + FLUX.2 Pro (OpenRouter) — ver [FLUXO.md](FLUXO.md).
- Este arquivo permanece como runbook do caminho gratuito, não como arquitetura ativa.
