# VPS — Hostinger KVM 2

Servidor Hostinger usado pela automação LinkedIn (Hermes + n8n).

## Dados da VPS

| Item | Valor |
|------|--------|
| **Plano** | KVM 2 (8 GB RAM, 2 vCPUs, 100 GB NVMe) |
| **ID Hostinger** | `1897392` |
| **Hostname** | `srv1897392.hstgr.cloud` |
| **Data Center** | Campinas, BR |
| **SO** | Ubuntu 24.04 LTS com Docker |
| **n8n URL** | https://srv1897392.hstgr.cloud/ |
| **SSH** | `ssh root@srv1897392.hstgr.cloud` (chave `cursor-eduardo-hostinger`) |

> Login n8n: usuário/senha definidos na instalação — **não** versionados neste repo.

---

## Containers em produção

| Container | Imagem | Função |
|-----------|--------|--------|
| `n8n` | `n8nio/n8n:2.28.6` | Automação LinkedIn (webhooks + schedule + reply) |
| `caddy` | `caddy:2-alpine` | Reverse proxy HTTPS (portas 80/443/5678) |
| `hermes` | `nousresearch/hermes-agent:latest` | Assistente Telegram — dispara webhooks |

---

## Estrutura de diretórios

```
Docker Manager (Hostinger):
  projeto "n8n"    → n8n + caddy + volumes
  projeto "hermes" → hermes agent + volume

Volumes:
  n8n_data     → /home/node/.n8n (workflows, credenciais, Data Tables)
  caddy_data   → certificados HTTPS
  caddy_config → config Caddy
  hermes-data  → /opt/data (skills, scripts, SOUL.md)
```

---

## Backups

Backups automáticos habilitados na Hostinger (snapshots periódicos da VPS).

---

## Segurança

- **Firewall**: portas 80, 443, 5678, 22 abertas; demais bloqueadas.
- **SSH**: apenas via chave pública (`cursor-eduardo-hostinger`); senha root desabilitada para login remoto.
- **HTTPS**: Caddy gera e renova certificados Let's Encrypt automaticamente.
- **Secrets**: todos em `.env` no servidor — **nunca** versionados no Git.

---

## Env vars (referência — sem valores)

### n8n (`.env`)

| Variável | Função |
|----------|--------|
| `N8N_HOST` | Hostname público do n8n |
| `N8N_PROTOCOL` | `https` |
| `WEBHOOK_URL` | Base URL dos webhooks |
| `N8N_ENCRYPTION_KEY` | Chave de criptografia das credenciais n8n |
| `GENERIC_TIMEZONE` | `America/Sao_Paulo` |

### Hermes (`.env`)

| Variável | Função |
|----------|--------|
| `OPENROUTER_API_KEY` | Acesso à API OpenRouter |
| `TELEGRAM_BOT_TOKEN` | Token do bot Telegram |
| `HERMES_MODEL` | Modelo de inferência |
| `HERMES_INFERENCE_PROVIDER` | Provider do modelo |
| `N8N_LINKEDIN_FOTO_WEBHOOK_URL` | Webhook de fila de fotos |
| `N8N_LINKEDIN_TEXTO_WEBHOOK_URL` | Webhook de fila de textos |

> Para a lista completa, veja o Docker Compose de referência em `hermes/docker-compose.yml`.

---

## Manutenção

```bash
# Ver containers ativos
docker ps

# Atualizar n8n (via Docker Manager ou manual)
docker compose pull && docker compose up -d

# Logs n8n
docker logs n8n --tail 100 -f

# Logs Hermes
docker logs hermes --tail 100 -f

# Backup manual do volume n8n
docker run --rm -v n8n_n8n_data:/data -v /opt/backups:/backup alpine \
  tar czf /backup/n8n-data-$(date +%Y%m%d).tar.gz -C /data .
```

---

## Projetos neste Git vs VPS

| Onde | O quê |
|------|--------|
| Repo `linkedin-automacao-ia` | Workflows (JSON), prompts, docs, skills, scripts de referência |
| VPS (n8n) | Runtime: executa workflows, guarda credenciais e Data Tables |
| VPS (Hermes) | Runtime: recebe comandos Telegram, dispara webhooks |

> API keys, tokens e senhas existem **apenas** no `.env` do servidor. Este repositório **não contém secrets**.
