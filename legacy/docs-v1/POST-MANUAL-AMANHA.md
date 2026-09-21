# Post manual amanhã → n8n responde comentários

Objetivo: você publica **no app LinkedIn**; o n8n passa a **monitorar o link** e **responder comentários** (~2 min, janela ~48h).

## O que já está pronto (n8n)

| Peça | Status |
|------|--------|
| Webhook registrar link | Ativo: `POST /webhook/hermes-linkedin-monitor` |
| Data Table **LinkedIn Posts Monitor** | Destino do link (`status=monitoring`) |
| Reply automático | Workflow `LinkedIn Resposta Comentarios Post` (~2 min) |

## Bloqueio atual (Hermes Telegram → n8n)

O comando `/monitorar` **ainda não está aplicado no container Hermes da VPS** (sem SSH daqui).  
Por isso o bot no Telegram **ainda não** grava o link sozinho.

## Caminho A — liberar Hermes (1 comando na VPS)

No **console root** do painel Hostinger (Browser terminal):

```bash
# 1) Copie o script do repo para a VPS (ou cole o arquivo), depois:
bash /caminho/para/hermes-monitorar-vps-ready.sh
```

Ou, se o repo já estiver na VPS:

```bash
bash /docker/linkedin-automacao-ia/scripts/hermes-monitorar-vps-ready.sh
# (ajuste o path se o clone estiver em outro lugar)
```

Esperado: `env ok` + `smoke_ok`.

Depois, no Telegram:

```text
/monitorar https://www.linkedin.com/posts/....activity-..........
```

## Caminho B — amanhã sem Hermes (garantido)

1. Publique o post no LinkedIn.
2. Copie o link completo (precisa ter `activity-` + números, ou `urn:li:activity:`).
3. Cole o link **neste chat do Cursor** e peça: `registra no monitor`.
4. Eu gravo via n8n na tabela **LinkedIn Posts Monitor**.
5. Comentários → reply automático do n8n.

## Checklist do link

- Bom: `https://www.linkedin.com/posts/seu-slug_...-activity-7345...-AbCd`
- Bom: `https://www.linkedin.com/feed/update/urn:li:activity:7345...`
- Ruim: link genérico do perfil / feed sem ID do post

## Como validar

1. Data Table **LinkedIn Posts Monitor** → linha com seu `postUrl`, `status=monitoring`.
2. Deixe um comentário de teste (outra conta) no post.
3. Em até ~2–4 min, o workflow de reply deve responder (se o scrape HTML não estiver bloqueado).
