# Imagens — capa editorial (padrão ativo) + catálogo (opcional)

Timezone: **America/Sao_Paulo**

## Decisão de produto (padrão ativo)

A arte do post **não** deve parecer “foto/surreal de IA genérica” (estilo Google LLM / cyberpunk).  
O padrão ativo é **capa editorial sem texto** (ilustração abstrata tech/corporativa) com **rotação de 8 estilos**, vinculada à newsletter *Previsibilidade na Prática*.

Prompt: [`prompts/post-imagem-capa.json`](../prompts/post-imagem-capa.json)

Modelo em produção: OpenRouter **`black-forest-labs/flux.2-pro`** via HTTP `/api/v1/images`.

### Estilos (round-robin por `dayOfMonth`)

Seleção estável: `estilos[(dayOfMonth - 1) % 8]` (fuso SP).

| Índice | Estilo |
|-------:|--------|
| 0 | dashboard |
| 1 | rede neural |
| 2 | engrenagem e circuito |
| 3 | fluxo de processo |
| 4 | camadas de dados |
| 5 | grade e nós |
| 6 | ondas de sinal |
| 7 | blocos modulares |

Ex.: Dia 1 → `dashboard`; Dia 2 → `rede neural`; Dia 9 → `dashboard` de novo.

### Regras fixas da arte

| Em vez de… | Preferir… |
|------------|-----------|
| Texto/labels na imagem | **Sem texto** na arte (preferência). Se aparecer texto, **somente PT-BR** acentuado — nunca inglês |
| Molde 3 cards glass (legado) | Capa editorial abstrata do estilo da rodada |
| Retrato / robô humanoide | Formas geométricas, fluxos, circuitos, nós |
| Cyberpunk / colagem | Minimalismo de revista tech / relatório corporativo |

Stack free / catálogo (**opcional, não default**): [`STACK-GRATUITA.md`](STACK-GRATUITA.md)

## Fluxo ativo no n8n (FLUX.2 Pro via OpenRouter)

```
Sanitize Post Text
  → Build Cover Prompt (escolhe estilo + monta briefing)
  → Generate Cover Flux Pro (OpenRouter FLUX.2 Pro, 1:1 png)
  → Prepare Flux Binary
  → Check Cover Ready → IF Cover OK
       OK   → Post With Image
       FAIL → Post Text Only
```

Credencial: **OpenRouter account** (mesma do texto DeepSeek).

## Fluxo opcional (catálogo — gratuito)

```
Sanitize Post Text
  → Get Catalog Images (data table LinkedIn Imagens Agenda)
  → Pick Catalog Image (postDate → themeIndex → rotação)
  → Download Catalog Image (HTTP → binary)
  → sucesso? → Post With Image
  → sem URL / falha download? → Post Text Only
```

Data table: **LinkedIn Imagens Agenda** (`iuKvPfKaSd77gl4H`) — só necessário se religar o modo free.

## Fallback

Se a geração FLUX.2 Pro falhar (créditos OpenRouter, erro de API, etc.), o fluxo publica **só o texto**. O Telegram reflete isso (`hasCover` / “Somente texto”).

## Lote 1 — 30/07 a 03/08/2026 (legado / catálogo)

Referência histórica de imagens pré-geradas para o modo catálogo. **Não** é o caminho ativo.

| Ordem | Data (SP) | Tema # (legado) | Tema | Estilo (legado) | Arquivo | Status |
|------:|-----------|-----------------|------|-----------------|---------|--------|
| 1 | 2026-07-30 | 31 | Por que agentes de IA falham | 3 cards (legado) | `assets/posts/2026-07-30.png` | aguardando |
| 2 | 2026-07-31 | 32 | Human in the loop na IA | 3 cards (legado) | `assets/posts/2026-07-31.png` | arquivo local pronto (falta URL) |
| 3 | 2026-08-01 | 33 | Agentes de IA para marketing e conteúdo | 3 cards (legado) | `assets/posts/2026-08-01.png` | aguardando |
| 4 | 2026-08-02 | 34 | Como medir ROI de inteligência artificial | 3 cards (legado) | `assets/posts/2026-08-02.png` | aguardando |
| 5 | 2026-08-03 | 35 | Futuro do trabalho com IA | 3 cards (legado) | `assets/posts/2026-08-03.png` | aguardando |

Catálogo: [`assets/posts/catalogo-lote-1.json`](../assets/posts/catalogo-lote-1.json)

> Em produção o índice de tema é **Dia N = 1–30** ([TEMAS.md](TEMAS.md)). Os números 31–35 acima são só do lote legado.

## Specs (padrão ativo)

- Formato: **1:1** (png via OpenRouter Image API → LinkedIn feed)
- Texto na arte: **nenhum** (capa editorial)
- Sem watermark / sem logo de marca / sem rostos / sem robôs antropomórficos
- Modelo: **black-forest-labs/flux.2-pro** · aspect **1:1** · png
- Nós n8n: `Build Cover Prompt`, `Generate Cover Flux Pro`, `Prepare Flux Binary`, `Check Cover Ready`, `IF Cover OK`
