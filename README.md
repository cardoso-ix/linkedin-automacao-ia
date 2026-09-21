# Automação LinkedIn — Telegram + n8n + Playwright Bridge

Sistema avançado de automação humanizada para o LinkedIn, integrando **Telegram Bot**, **Playwright em modo persistente (Docker + Xvfb)** e **n8n** na nuvem (VPS).

O objetivo central é alavancar impressões, autoridade profissional e atração de oportunidades para quem atua com **Engenharia de Automação & IA Agêntica**, eliminando marcas artificiais de IA e protegendo a integridade da conta com risco zero de banimento.

---

## Destaques da Versão 2.0

* **🎯 Radar de Líderes em IA (Sniper Engagement):** Monitoramento contínuo das publicações recentes dos maiores nomes e referências em Inteligência Artificial, LLMs e Automação no Brasil. O sistema varre publicações ativas, gera comentários técnicos e analíticos via DeepSeek v4.1 (sem clichês de IA) e permite curtir e publicar com 1 clique no Telegram, alavancando sua autoridade e alcance orgânico diário.
* **Engajamento Inteligente via Link (Curtir & Comentar sob Demanda):** Cole o link de qualquer post do LinkedIn no Telegram (`linkedin.com/posts/...` ou `lnkd.in/...`). O robô acessa a publicação pelo Playwright, lê o conteúdo e o autor, o DeepSeek v4.1 gera um comentário técnico sem clichês, e você aprova a curtida e o envio com 1 toque no botão `[✅ Curtir e Comentar Post]`.
* **Zero Risco de Banimento:** O Playwright roda com Chromium em contexto persistente (`session/profile`), preservando cookies de autenticação reais, com emulação completa de hardware e digitação humanizada com atrasos variáveis.
* **Anti-IA Editorial Rigoroso:** Configurado no [CONTEXT.md](CONTEXT.md) com proibição de emojis corporativos saturados, travessões artificiais (`—`), listas automáticas e fechamentos apelativos.
* **Dupla Proposta Inteligente (`/post`):** Cada comando gera simultaneamente uma variação de *Storytelling & Bastidores de Produção* e outra de *Arquitetura & Engenharia*, permitindo aprovação com 1 clique no Telegram.
* **Gerador de Prompts para Meta AI:** prompts calibrados para imagens panorâmicas 16:9 em estética dark mode com diagramas de processos e infográficos técnicos **100% em Português do Brasil (PT-BR)**.
* **Monitor de Comentários Human-in-the-Loop:** n8n a cada 30 minutos + DeepSeek v4.1 sugerindo réplicas técnicas inteligentes para novos comentários nos seus posts com aprovação no Telegram.
* **Monitor de Visitantes do Perfil (LinkedIn Premium):** n8n a cada 4 horas escaneando visualizações de perfil, classificando recrutadores e tomadores de decisão, e sugerindo abordagens elegantes com link direto.
* **Governança & Observabilidade com Coolify v4:** Gestão centralizada dos containers Docker na VPS HostGator, com métricas de CPU/RAM em tempo real, checagens nativas de saúde (`healthcheck`), proxy reverso Traefik v3.7 e isolamento em múltiplos ambientes de projetos.
* **📸 Print ao Vivo do Robô (`/tela`):** Captura instantânea em 1080p da sessão ativa do Chromium no servidor direto para o chat do Telegram, com status da URL e botões interativos para reabertura de menu ou nova foto.
* **🚨 Central de Alertas Críticos no Telegram:** Interceptação automática de falhas via nó `errorTrigger` no n8n direcionada para o endpoint `/notify/error` do bridge, avisando você imediatamente no celular se algum workflow quebrar.


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
|  - Análise & Engajamento Links|<----------->|  - DeepSeek v4.1 Integration  |
|  - Endpoints REST             |             |  - Deduplicação de alertas    |
|  - Telegram Bot Daemon        |             |                               |
+-------------------------------+             +-------------------------------+
              |                                             |
              +----------------------+----------------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Coolify v4 Dashboard    |
                      |  (Docker Engine & Traefik)  |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |       LinkedIn Web App      |
                      |  (Feed, Posts, Analytics)   |
                      +-----------------------------+
```

---

## Interações e Comandos no Telegram

| Comando / Ação | O que faz na prática |
|----------------|----------------------|
| **🎯 Radar de Líderes** (`/radar` ou botão) | **Varre os feeds dos maiores líderes de IA monitorados ➔ DeepSeek v4.1 redige comentário sênior anti-IA ➔ Apresenta fila interativa com botões `[✅ Curtir e Comentar Post]`, `[🔄 Gerar Outra Opção]`, `[⏭️ Próximo Post]`. Constrói autoridade diária.** |
| **👥 Líderes Monitorados** (`/lideres`) | Exibe a lista de perfis de referência em IA cadastrados com bio, categoria e link direto. |
| **➕ Adicionar Líder** (`/adicionarlider <url>`) | Cadastra um novo perfil de referência no radar, extraindo nome e headline automaticamente via Playwright. |
| **Colar link do post** (`lnkd.in` ou `linkedin.com/posts/...`) | Lê o post, autor e contexto pelo Playwright ➔ DeepSeek v4.1 gera comentário perspicaz ➔ Bot exibe prévia com aprovação em 1 clique. |
| `/menu` | Abre o painel interativo de botões para ações rápidas com 1 toque. |
| `/tela` (ou `/print`) | Tira um print 1080p em tempo real da tela do navegador no servidor e envia no chat. |
| `/post <tema>` | Gera 2 variações completas de post + prompt de imagem para o Meta AI. |
| `/visitantes` | Consulta sob demanda os visitantes recentes do seu perfil (LinkedIn Premium). |
| `/status` | Diagnóstico de saúde da sessão do LinkedIn, IA DeepSeek e servidor. |
| `/testealerta` | Dispara um teste ponta a ponta do canal de notificações de falhas críticas. |
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
│   ├── app.py                    # FastAPI bridge + Playwright automator + Radar Engine
│   ├── telegram_bot.py           # Daemon do bot Telegram com botões e Radar queue
│   ├── ai_leaders.json           # Watchlist de líderes e referências em IA monitorados
│   ├── Dockerfile                # Imagem Docker com Playwright + Python + Xvfb
│   ├── start.sh                  # Inicializador do Xvfb e servidor Uvicorn
│   └── requirements.txt          # Dependências Python
├── workflows/
│   ├── linkedin_radar_monitor.json         # Workflow n8n diário do Radar de IA (09:30)
│   ├── linkedin_comment_monitor.json       # Workflow n8n de comentários (30m)
│   ├── linkedin_profile_views_monitor.json # Workflow n8n de visitantes Premium (4h)
│   └── n8n_error_handler.json              # Workflow n8n interceptor e notificador de erros
├── legacy/                       # Códigos e docs legados arquivados
└── scripts/
    ├── vps_client.py             # Cliente seguro de automação e deploy via SSH/SFTP
    ├── deploy_features.py        # Script de deploy e sincronização de containers
    └── verify_deploy.py          # Verificador automatizado de saúde e testes HTTP
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
5. Gerencie, acompanhe métricas de CPU/RAM e visualize logs pelo Coolify v4 em `http://<IP_DA_VPS>:8000`.

---

## Licença e Segurança

Este repositório não contém senhas, chaves de API ou cookies de sessão. Todas as credenciais são injetadas estritamente por variáveis de ambiente locais ou arquivos `.env` ignorados pelo controle de versão.

---

## Créditos & Engenharia Agêntica

* **Autor & Engenheiro Responsável:** [Eduardo Cardoso](https://www.linkedin.com/in/eduardo-cardoso-213a02267) · [Portfólio](https://cardoso-ix.github.io/Portifolio/)
* **Pair Programming & Engenharia Agêntica:** Desenvolvido em conjunto com o **Google Antigravity (AGY)** — DeepMind Advanced Agentic Coding Framework, adotando práticas rigorosas de engenharia de software (TDD, Architecture Decision Records, isolamento de segredos e revisão de conformidade anti-IA).
