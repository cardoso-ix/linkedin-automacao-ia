# Automação LinkedIn — Hermes v2 + Playwright + n8n

Sistema avançado de automação humanizada para o LinkedIn, integrando **Telegram Bot**, **Playwright em modo persistente (Docker + Xvfb)** e **n8n** na nuvem (VPS).

O objetivo central é alavancar impressões, autoridade profissional e atração de oportunidades para quem atua com **Engenharia de Automação & IA Agêntica**, eliminando marcas artificiais de IA e protegendo a integridade da conta com risco zero de banimento.

---

## Destaques da Versão 2.0

* **Zero Risco de Banimento:** O Playwright roda com Chromium em contexto persistente (`session/profile`), preservando cookies de autenticação reais, com emulação completa de hardware e cabeçalhos reais.
* **Anti-IA Editorial Rigoroso:** Configurado no [CONTEXT.md](CONTEXT.md) com proibição de emojis corporativos saturados, travessões artificiais (`—`) e fechamentos apelativos.
* **Dupla Proposta Inteligente (`/post`):** Cada comando gera simultaneamente uma variação de *Storytelling & Bastidores de Produção* e outra de *Arquitetura & Engenharia*, permitindo aprovação com 1 clique no Telegram.
* **Gerador de Prompts para Meta AI:** prompts calibrados para imagens panorâmicas 16:9 em estética dark mode com diagramas de processos e infográficos técnicos **100% em Português do Brasil (PT-BR)**.
* **Monitor de Comentários Human-in-the-Loop:** n8n a cada 30 minutos + DeepSeek v4.1 sugerindo réplicas técnicas inteligentes para aprovação com botões interativos no Telegram.
* **Monitor de Visitantes do Perfil (LinkedIn Premium):** n8n a cada 4 horas escaneando visualizações de perfil, classificando recrutadores e tomadores de decisão, e sugerindo abordagens elegantes com link direto.

---

## Arquitetura do Sistema

```
                      +-----------------------------+
                      |   Telegram: Eduardo Cardoso |
                      |    (@funcionario_vip_bot)   |
                      +--------------+--------------+
                                     |
              +----------------------+----------------------+
              |                                             |
              v                                             v
+-------------------------------+             +-------------------------------+
|  Bridge LinkedIn (FastAPI)    |             |          Servidor n8n         |
|  - Playwright + Xvfb          |             |  - Monitor Comentários (30m)  |
|  - Sessão persistente         |             |  - Monitor Visitantes (4h)    |
|  - Endpoints REST             |<----------->|  - DeepSeek v4.1 Integration  |
|  - Telegram Bot Daemon        |             |  - Deduplicação de alertas    |
+-------------------------------+             +-------------------------------+
              |
              v
+-------------------------------+
|       LinkedIn Web App        |
|  (Feed, Posts, Analytics)     |
+-------------------------------+
```

---

## Comandos do Bot no Telegram

| Comando | Descrição |
|---------|-----------|
| `/menu` | Abre o painel interativo de botões para ações rápidas com 1 toque. |
| `/post <tema>` | Gera 2 variações completas de post + prompt de imagem para o Meta AI. |
| `/visitantes` | Consulta sob demanda os visitantes recentes do seu perfil (LinkedIn Premium). |
| `/status` | Diagnóstico de saúde da sessão do LinkedIn, IA DeepSeek e servidor. |
| `/ajuda` | Manual de instruções e orientações operacionais. |

---

## Estrutura do Repositório

```
├── CONTEXT.md                    # Manual editorial de persona, voz e regras anti-IA
├── README.md                     # Documentação principal da solução
├── docs/
│   ├── FLUXO.md                  # Mapeamento do fluxo operacional passo a passo
│   ├── HANDOFF-Eduardo-Ops.md    # Handoff operacional e histórico de contexto
│   └── adr/
│       ├── 0001-human-engine.md  # ADR do motor de postagem humanizada
│       └── 0002-bridge-views.md  # ADR do bridge Playwright e monitor Premium
├── infra/
│   ├── docker-compose.yml        # Orquestração do bridge e n8n na VPS
│   └── .env.example              # Exemplo de variáveis de ambiente
├── worker/
│   ├── app.py                    # FastAPI bridge + Playwright automator
│   ├── telegram_bot.py           # Daemon do bot Telegram com botões e drafts
│   ├── Dockerfile                # Imagem Docker com Playwright + Python + Xvfb
│   ├── start.sh                  # Inicializador do Xvfb e servidor Uvicorn
│   └── requirements.txt          # Dependências Python
├── workflows/
│   ├── linkedin_comment_monitor.json       # Workflow n8n de comentários
│   └── linkedin_profile_views_monitor.json # Workflow n8n de visitantes Premium
└── scripts/
    └── vps_client.py             # Cliente seguro de automação e deploy via SSH/SFTP
```

---

## Como Fazer Deploy na VPS

1. Clone o repositório na sua VPS:
   ```bash
   git clone https://github.com/cardoso-ix/linkedin-automacao-ia.git /opt/linkedin-automation
   cd /opt/linkedin-automation
   ```

2. Configure o arquivo `.env`:
   ```bash
   cp infra/.env.example infra/.env
   nano infra/.env
   ```

3. Suba os containers com Docker Compose:
   ```bash
   docker compose -f infra/docker-compose.yml up -d --build
   ```

4. Acesse o n8n no navegador em `http://<IP_DA_VPS>:5678` e importe os workflows da pasta `workflows/`.

---

## Licença e Segurança

Este repositório não contém senhas, chaves de API ou cookies de sessão. Todas as credenciais são injetadas estritamente por variáveis de ambiente locais ou arquivos `.env` ignorados pelo controle de versão.
