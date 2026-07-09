# Setup no Make.com

## Pré-requisitos

- Conta [Make.com](https://www.make.com)
- API key [OpenAI](https://platform.openai.com/api-keys) com crédito
- LinkedIn conectado (OpenID Connect)

## Fluxo

```
Schedule 8h
  → HTTP 3 (texto GPT-4o)
  → Router
       ├─ Charge (qui/dom) → HTTP 6 → OpenAI Image → LinkedIn Article
       └─ Texto (fallback) → LinkedIn Empty
```

## 1. Schedule

| Campo | Valor |
|-------|--------|
| Intervalo | Diário |
| Hora | 08:00 |
| Fuso | America/Sao_Paulo |

## 2. HTTP 3 — Texto

| Campo | Valor |
|-------|--------|
| URL | `https://api.openai.com/v1/chat/completions` |
| Method | POST |
| Auth | No authentication |
| Parse response | Yes |

**Headers**

| Name | Value |
|------|--------|
| Authorization | `Bearer sk-SUA_CHAVE` |
| Content-Type | `application/json` |

**Body:** cole o conteúdo de [`prompts/http3-texto.json`](../prompts/http3-texto.json)

## 3. Router

### Rota 1 — Charge

| Campo | Valor |
|-------|--------|
| Label | Charge - qui e dom |
| Fallback | No |
| Condição | `{{formatDate(now; "dddd")}}` Equal to `Thursday` **OR** Equal to `Sunday` |

(Se o Make usar português: `quinta-feira` / `domingo`)

### Rota 2 — Texto

| Campo | Valor |
|-------|--------|
| Label | Texto - fallback |
| Fallback | **Yes** |
| Condição | vazia |

## 4. Rota Texto — LinkedIn

| Campo | Valor |
|-------|--------|
| Content | HTTP 3 → choices → 1 → message → content |
| Media Type | **Empty** |
| Visibility | Anyone |

## 5. Rota Charge — HTTP 6

Mesma URL/headers do HTTP 3.  
**Body:** [`prompts/http6-imagem.json`](../prompts/http6-imagem.json) — **fixo**, sem mapear HTTP 3.

## 6. Rota Charge — OpenAI Generate Image

| Campo | Valor |
|-------|--------|
| Model | gpt-image-1.5 |
| Prompt | HTTP 6 → choices → 1 → message → content |
| Quality | High |

## 7. Rota Charge — LinkedIn Article

| Campo | Valor |
|-------|--------|
| Content | HTTP 3 → choices → 1 → message → content |
| Media Type | Article |
| URL | `https://www.linkedin.com/in/eduardo-cardoso-213a02267` |
| Title | Agentes de IA · Automacao Inteligente |
| Description | Guia visual sobre agentes de IA e automacao. |
| Thumbnail Data | OpenAI → Response Image Data |
| Thumbnail File name | OpenAI → Response Image Name |
| Visibility | Anyone |

## Teste

1. Run once numa **quarta** → só LinkedIn Empty  
2. Run once numa **quinta** → charge + imagem  
3. Conferir: zero `**` no texto do post
