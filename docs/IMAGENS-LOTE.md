# Imagens — capa editorial (padrão ativo) + catálogo (opcional)

Timezone: **America/Sao_Paulo**

## Decisão de produto (padrão ativo)

A arte do post **não** deve parecer “foto/surreal de IA genérica” (estilo Google LLM / cyberpunk).  
O padrão ativo é **capa editorial sem texto, letras nem números** (ilustração abstrata tech/corporativa) com **rotação de 8 estilos**, vinculada à newsletter *Previsibilidade na Prática*.

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
| Texto/labels/letras/números na imagem | **Proibido absoluto** — sem tipografia, letras, dígitos ou labels em qualquer idioma |
| Molde 3 cards glass (legado) | Capa editorial abstrata do estilo da rodada |
| Retrato / robô humanoide | Formas geométricas, fluxos, circuitos, nós |
| Cyberpunk / colagem | Minimalismo de revista tech / relatório corporativo |

Stack free / catálogo (**opcional, não default**): [`STACK-GRATUITA.md`](STACK-GRATUITA.md)

## Fluxo ativo no n8n (foto Hermes; sem FLUX)

```
Sanitize Post Text
  → IF Text Only Mode
       text_only → Post Text Only
       full → Get Ready Photo (Imagens Agenda, status=ready, source=hermes)
            → tem foto? Read → Prepare → Post With Image (marca used)
            → sem foto? Post Text Only (+ aviso no Telegram)
```

Foto Hermes: disco n8n + Data Table **LinkedIn Imagens Agenda**. Nós FLUX permanecem no canvas **desabilitados** (legado).

## Fluxo opcional (catálogo URL pública — legado)

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

Sem foto `ready` na fila (ou `/postar-texto`), o fluxo publica **só o texto**. O Telegram reflete isso (“Somente texto”).

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
