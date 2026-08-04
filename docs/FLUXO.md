# Fluxo — arquitetura ativa (post diário + reply a comentários)

Timezone: **America/Sao_Paulo**

## Workflows em uso (n8n)

| Workflow | ID | Status |
|----------|-----|--------|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | **ATIVO** |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | **ATIVO** (texto reply: Qwen-Flash via Alibaba) |

> **Arquivado / fora do portfólio:** LinkedIn Resposta via Gmail (`5xkPzzTcKwdsPymn`).

## 1) Post diário 08:00 (texto + capa Qwen-Image)

**Workflow:** [LinkedIn Post Diario Texto](https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo) · ID `ysHFWIV0tGWJbhjo`

```
08:00
  → Get Recent Posts (LinkedIn Posts Diario)
  → já postou hoje? → skip + Telegram
  → Build Theme Context (Dia N = tema N; 1–30; America/Sao_Paulo)
  → Generate Post Text (Qwen-Plus via Alibaba) → Sanitize
  → Build Cover Prompt (estilo = round-robin dayOfMonth % 8)
  → Generate Cover Qwen Image (DashScope `qwen-image-2.0`)
  → Download Cover From URL → Prepare Cover Binary
  → Check Cover Ready → IF Cover OK
       OK  → Post With Image
       FAIL → Post Text Only
  → Save Posted Row → Telegram (ok / skip / fail; reflete hasCover)
```

- **Texto:** Alibaba `qwen-plus` (OpenAI-compatible `/compatible-mode/v1`)
- **Imagem:** Alibaba `qwen-image-2.0` via HTTP `/api/v1/services/aigc/multimodal-generation/generation`
- Temas: [TEMAS.md](TEMAS.md) · Spec imagens: [IMAGENS-LOTE.md](IMAGENS-LOTE.md)

**Prova histórica:** execução `5712` · `urn:li:share:7489362507237675008` (OpenRouter; revalidar após migração).

## 2) Resposta a comentários (Sheets + HTML — sem Gmail)

**Workflow:** [LinkedIn Resposta Comentarios Post](https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z) · ID `q28d2xJlAgvMpZ9Z`

```
Every 2 min
  → Get Already Replied / Get Monitor Posts (Sheets)
  → Filter Fresh 48h → Loop Posts
  → Fetch Post HTML → Parse HTML Comments
  → Filter New Comments → Loop Comments
  → Generate Reply Text (Qwen-Flash via Alibaba)
  → Prepare Reply Payload → Post LinkedIn Reply
  → Mark Done / Error → Wait 20s
```

- **Texto reply:** Alibaba `qwen-flash`
- **Prompt:** [`prompts/resposta-comentario.json`](../prompts/resposta-comentario.json)
- **Skill:** [`skills/linkedin-resposta-comentario/`](../skills/linkedin-resposta-comentario/)
- **Credencial:** Alibaba Model Studio
- Stickies do canvas: referenciar Qwen-Flash (não GPT-3.5 / não OpenRouter)

> Se o agent MCP não editar o canvas: no workflow → Settings → **Available in MCP** = ON.

## Data Tables / Sheets

| Recurso | Uso |
|---------|-----|
| **LinkedIn Posts Diario** (`mayfOqKniH3iFbiw`) | Memória / anti-dupe do post 08:00 |
| Google Sheets (monitor + already replied) | Fila/dedup do fluxo de comments |

## Legado / opcional

Catálogo de imagens locais (sem LLM de imagem): [STACK-GRATUITA.md](STACK-GRATUITA.md) — **não** é o default.
