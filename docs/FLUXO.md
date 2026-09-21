# Fluxo Operacional da Automação LinkedIn (v2 — Playwright + Telegram + n8n)

## Visão Geral da Arquitetura

O sistema conecta 3 camadas principais em uma infraestrutura em container na nuvem (VPS):
1. **Bridge LinkedIn (`linkedin-bridge`):** Playwright rodando em Xvfb com Chromium persistente e API FastAPI.
2. **Telegram Bot Daemon:** Interface conversacional com Eduardo (`@funcionario_vip_bot`) operando em tempo real.
3. **Orquestrador n8n (`n8n-server`):** Automações agendadas de comentários e monitoramento analítico de visitantes Premium.

```
+-------------------------------------------------------------------------+
|                              TELEGRAM                                   |
|   /post <tema>  -->  Dual Draft (Story vs Arq)  -->  Meta AI Prompt     |
|   /visitantes   -->  Relatório Instantâneo de Quem Viu seu Perfil       |
|   /status       -->  Diagnóstico de Saúde da Sessão e APIs              |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                    LINKEDIN BRIDGE (FastAPI + Playwright)               |
|   - POST /publish/post          --> Publica post com/sem imagem         |
|   - GET  /profile/views         --> Extrai e classifica visitantes      |
|   - GET  /comments/recent       --> Monitora comentários recentes       |
|   - POST /comments/reply        --> Responde comentários aprovados      |
+------------------------------------+------------------------------------+
                                     ^
                                     |
+------------------------------------+------------------------------------+
|                                  N8N                                    |
|   - Workflow 1 (30 min): Monitor de comentários + DeepSeek + Aprovação |
|   - Workflow 2 (4 h):    Monitor de visitantes Premium + Abordagens     |
+-------------------------------------------------------------------------+
```

## Fluxos Detalhados

### 1. Criação e Publicação Humanizada de Posts (`/post <tema>`)
1. Eduardo envia `/post <tema ou ideia>` no Telegram.
2. O bot consulta o DeepSeek v4.1 usando as regras estritas anti-IA de `CONTEXT.md`.
3. Duas versões são entregues simultaneamente:
   - **Variação 1:** Bastidores & Storytelling Prático.
   - **Variação 2:** Arquitetura & Posicionamento de Engenharia.
4. Ao selecionar uma versão, o bot exibe o prompt calibrado para gerar a imagem no Meta AI (100% PT-BR, 16:9, Dark Mode).
5. Eduardo pode aprovar direto com `[Publicar Agora]` ou enviar a foto gerada antes de confirmar.
6. O worker do Playwright publica no LinkedIn e retorna a confirmação no chat.

### 2. Monitor de Comentários Human-in-the-Loop (n8n a cada 30 min)
1. O n8n consulta `GET /comments/recent` na bridge.
2. Se houver novo comentário de seguidor, o DeepSeek v4.1 gera uma réplica inteligente de colega para colega.
3. Alerta enviado no Telegram com botões: `[✅ Curtir e Responder]` e `[❌ Ignorar]`.
4. Ao clicar no botão, a resposta é publicada diretamente na thread do LinkedIn.

### 3. Monitor de Visitantes LinkedIn Premium (n8n a cada 4 horas)
1. O n8n consulta `GET /profile/views`.
2. Filtra visitantes inéditos via `seen_viewers.json`.
3. O DeepSeek v4.1 elabora abordagem de 2 frases conectando o background do visitante a automações e IA.
4. Notificação detalhada enviada no Telegram destacando recrutadores e tomadores de decisão com link de 1 clique para o perfil.
