# OpenCode Go — texto LLM (n8n + Hermes)

## O que mudou

Texto/LLM passou de OpenRouter (e tentativa Zen) para **OpenCode Go**.

| Destino | Config |
|--------|--------|
| API base | `https://opencode.ai/zen/go/v1` |
| Auth | `Authorization: Bearer <OPENCODE_GO_API_KEY>` |
| Modelo texto | `deepseek-v4-flash` (chat/completions) |
| Hermes provider | `opencode-go` |
| n8n nós | `OpenCode Go DeepSeek` (`lmChatOpenAi` + `options.baseURL`) |

Imagens/FLUX continuam na credencial **OpenRouter account** (não misturar).

## Já feito neste workspace

1. **Hermes local** (`%LOCALAPPDATA%\hermes`):
   - `.env`: `OPENCODE_GO_API_KEY` + `OPENCODE_GO_BASE_URL`
   - `config.yaml`: `provider: opencode-go`, `default: deepseek-v4-flash`
2. **n8n** (publicado):
   - Post `ysHFWIV0tGWJbhjo` e Reply `q28d2xJlAgvMpZ9Z` usam nó OpenAI-compatible apontando para Go
3. **docker-compose Hermes**: env `OPENCODE_GO_*` + defaults `HERMES_INFERENCE_PROVIDER=opencode-go`
4. **Cursor MCP** `opencode`: `OPENCODE_DEFAULT_PROVIDER=opencode-go`

## Passos manuais restantes

### 1) Credencial n8n (obrigatório)

O MCP não grava o secret da credencial. Na UI:

1. Abra Credentials → **OpenAI account** em `https://srv1897392.hstgr.cloud`
2. Cole a chave OpenCode Go no campo **API Key**
3. Salve (URL custom fica no nó via `baseURL`; se a credencial tiver campo URL, use `https://opencode.ai/zen/go/v1`)

Sem isso, os nós `OpenCode Go DeepSeek` falham com 401.

### 2) Hermes na VPS

SSH/console como root:

```bash
export OPENCODE_GO_API_KEY='sua-chave'
bash scripts/set-opencode-go-hermes-vps.sh
```

Ou no `.env` do compose da VPS defina `OPENCODE_GO_API_KEY` e rode `docker compose up -d` no diretório Hermes.

### 3) Reiniciar gateway Hermes local

Depois de mudar `.env`/`config.yaml`, reinicie o gateway Hermes para pegar `opencode-go`.

### 4) Cursor MCP

Reinicie o servidor MCP `opencode` no Cursor para aplicar `OPENCODE_DEFAULT_PROVIDER=opencode-go`.

## Validação rápida

- n8n: teste o nó `OpenCode Go DeepSeek` ou um post `text_only` via Hermes
- Hermes: mande “responda só OK” no chat e confira logs sem erro de provider
- Não commitar chaves (`.env`, `mcp.json` com secrets)

## Referência

- Docs Go: https://opencode.ai/docs/go/
- Models: `GET https://opencode.ai/zen/go/v1/models`
