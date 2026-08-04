# Setup — n8n VPS + Alibaba Model Studio (cota gratuita)

Este projeto roda no **n8n** (VPS Hostinger) e gera texto/imagem/reply via **Alibaba Cloud Model Studio** (Singapore).

## 1) Ativar cota gratuita (obrigatório)

Hoje a API key autentica, mas modelos sem liberação retornam `AccessDenied.Unpurchased`.

1. Abra [Model Studio — Singapore](https://modelstudio.console.alibabacloud.com/).
2. Confirme região **Singapore (International)** e aceite o termo se aparecer.
3. Vá em **Model Square** / **Free Quota** e libere (ou confirme cota) destes modelos:
   - `qwen-plus` — texto do post
   - `qwen-flash` — reply de comentários
   - `qwen-image-2.0` — capa
4. (Recomendado) Ative **Free Quota Only** nesses três para não gastar além da cota.
5. Se a key foi exposta em chat/repo público: **regenere** a API key no console e atualize só no n8n.

## 2) Credencial no n8n (sem key no Git)

Crie **uma** credencial reutilizável:

| Campo | Valor |
|-------|--------|
| Nome | `Alibaba Model Studio` |
| Tipo sugerido | OpenAI API **ou** Header Auth |
| API Key | a key da workspace (cola só no n8n) |
| Base URL (chat) | `https://ws-88pwwhzlxkoiwrfh.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` |

Para a capa (HTTP Request DashScope):

| Campo | Valor |
|-------|--------|
| Method | `POST` |
| URL | `https://ws-88pwwhzlxkoiwrfh.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` |
| Header | `Authorization: Bearer <API_KEY>` |
| Body | ver `prompts/post-imagem-capa.json` → `request_body_template` |
| Depois | baixar `output.choices[0].message.content[0].image` → binary → LinkedIn |

## 3) Workflows ativos

| Nome | ID | URL |
|------|-----|-----|
| LinkedIn Post Diario Texto | `ysHFWIV0tGWJbhjo` | https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| LinkedIn Resposta Comentarios Post | `q28d2xJlAgvMpZ9Z` | https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z |

1. Abrir https://srv1824850.hstgr.cloud/
2. Confirmar credencial **LinkedIn account**
3. Confirmar credencial **Alibaba Model Studio** (texto + capa + reply)
4. Trocar nós OpenRouter → Alibaba (modelos da tabela abaixo)
5. **Publish** o draft
6. Manter **Resposta via Gmail** arquivado

## Modelos / geração

| Uso | Stack |
|-----|--------|
| Post diário (texto) | Alibaba **`qwen-plus`** |
| Post diário (capa) | Alibaba **`qwen-image-2.0`** (`multimodal-generation`, `1024*1024`) |
| Reply comentário | Alibaba **`qwen-flash`** |

## MCP (para o agent editar o canvas de comments)

No workflow **LinkedIn Resposta Comentarios Post** → Settings → **Available in MCP** = ON → Save.

## Validação rápida

1. Teste chat no n8n com `qwen-plus` (“Responda OK”). Se vier `Unpurchased`, volte ao passo 1.
2. Execute once no Post Diario (ou esperar 08:00 SP).
3. Conferir Telegram: ok com capa, skip (anti-dupe) ou aviso só texto.
4. No fluxo de comments: Generate Reply Text com `qwen-flash` → reply no LinkedIn.

Detalhes de VPS: [VPS.md](VPS.md) · Tutorial: [TUTORIAL.md](TUTORIAL.md)  
Catálogo de imagens (**legado**): [STACK-GRATUITA.md](STACK-GRATUITA.md)
