# VPS — acesso, n8n e organização

Servidor Hostinger usado pela automação LinkedIn.

## Link de acesso (n8n)

| Item | Valor |
|------|--------|
| **URL pública** | https://srv1824850.hstgr.cloud/ |
| **Post Diario Texto** | https://srv1824850.hstgr.cloud/workflow/ysHFWIV0tGWJbhjo |
| **Resposta Comentarios Post** | https://srv1824850.hstgr.cloud/workflow/q28d2xJlAgvMpZ9Z |
| **SSH (Hostinger)** | `ssh root@srv1824850.hstgr.cloud` (ou usuário do painel) |

Confirmação (2026-07-17): a URL responde com a interface **n8n** (HTTPS ok).  
Login: usuário/senha que você definiu na instalação (não fica neste repo).

> Se a página não abrir: painel Hostinger → VPS → firewall (portas **80/443**) e containers ligados.

---

## O n8n precisa ser Docker?

**Não é obrigatório**, mas **sim, é a forma recomendada** — e é o que costuma estar na Hostinger com n8n + Caddy.

| Forma | Quando usar |
|-------|-------------|
| **Docker (recomendado)** | Isola n8n, fácil atualizar (`docker compose pull`), Caddy/Nginx na frente com HTTPS |
| npm / binário na máquina | Possível, mas mistura com o SO; atualizar e rollback são mais trabalhosos |
| n8n Cloud | Já existe; manter **desligado** para LinkedIn (evitar post duplicado com a VPS) |

Resumo: **deixe n8n em Docker** na VPS. Para um site no futuro, também use Docker (ou um container Nginx/Caddy + app).

Layout típico que você já tinha no histórico do projeto:

```
/opt/n8n/                 # stack n8n
  docker-compose.yml
  .env                    # N8N_HOST, WEBHOOK_URL, chaves — NÃO commitar
```

Containers comuns: `n8n` + `caddy` (ou traefik) na porta 443.

---

## Como organizar a VPS para vários projetos

Objetivo: n8n continua estável; dá para colocar site / API sem bagunçar.

```
/opt/
  n8n/                    # automação (já existe)
  sites/                  # futuros sites
    meuportfolio/         # exemplo
  apps/                   # APIs, bots, etc.
  shared/
    caddy/                # OU um Caddy global
      Caddyfile
  backups/
```

### Regra de ouro

1. **Um projeto = uma pasta em `/opt/...` + um `docker-compose.yml`.**
2. **Um reverse proxy na frente** (Caddy ou Traefik) com HTTPS.
3. **Cada app numa porta interna**; o proxy publica o domínio.
4. **Volumes nomeados** para dados (Postgres do n8n, uploads do site).
5. **`.env` só no servidor** (nunca no GitHub).

### Domínios (futuro)

| Domínio / path | Serviço |
|----------------|---------|
| `srv1824850.hstgr.cloud` | n8n (hoje) |
| `n8n.seudominio.com` | n8n (melhor, quando tiver domínio) |
| `www.seudominio.com` | site |
| `api.seudominio.com` | API |

Enquanto só tiver o hostname Hostinger, o n8n pode ficar na raiz `/`.  
Quando tiver domínio próprio, aponte DNS A → IP da VPS e configure o Caddy.

---

## Checklist de organização (fazer no SSH)

Quando tiver acesso SSH (chave no painel Hostinger):

```bash
# 1) Ver o que está rodando
docker ps
ls -la /opt

# 2) Achar o compose do n8n
find /opt -name 'docker-compose*.yml' 2>/dev/null

# 3) Backup rápido
mkdir -p /opt/backups
# (export workflows pelo n8n UI + backup do volume docker)
```

Ordenar se estiver bagunçado:

```bash
sudo mkdir -p /opt/n8n /opt/sites /opt/apps /opt/backups
# mover compose atual do n8n para /opt/n8n se estiver em outro lugar
```

Não mexer em volumes sem backup.

---

## O que eu (Cursor) preciso para organizar de verdade

Sem SSH daqui só dá para validar a URL. Para aplicar a estrutura no servidor, envie **uma** destas opções:

1. Acesso SSH com chave (adicionar a chave pública da sua máquina no painel Hostinger), ou  
2. Colar a saída de: `docker ps`, `ls -la /opt`, e o `docker-compose.yml` do n8n (sem secrets do `.env`).

Aí dá para: confirmar pastas, documentar o compose real, e preparar o Caddy para um segundo projeto (site) sem derrubar o n8n.

---

## Projetos neste Git vs VPS

| Onde | O quê |
|------|--------|
| Repo `linkedin-automacao-ia` | Workflows, prompts, docs |
| VPS `/opt/n8n` | Runtime n8n + dados |
| Futuro site | Outro repo + `/opt/sites/...` na VPS (ou Vercel, como o Consórcio) |

Site estático/Next pode ir na **Vercel** (mais simples) e a VPS ficar só para **n8n + apps que precisam de servidor 24/7**.

---

## Stack em produção (resumo)

O n8n nesta VPS roda o post diário e o reply a comentários com **OpenRouter DeepSeek-V4-Flash** (capa do post: FLUX.2 Pro). Resposta via Gmail está arquivada. Detalhes: [FLUXO.md](FLUXO.md).

## Resumo

1. **Link n8n:** https://srv1824850.hstgr.cloud/ — **está no ar**.  
2. **Docker:** sim, mantenha n8n em Docker.  
3. **Organização:** `/opt/n8n`, `/opt/sites`, `/opt/apps`, proxy HTTPS único.  
4. **Próximo passo:** liberar SSH (ou mandar `docker ps` + compose) para eu aplicar a estrutura no servidor.
