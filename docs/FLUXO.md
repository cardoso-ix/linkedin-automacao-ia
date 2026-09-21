# Fluxo Operacional da Automação LinkedIn (v2 — Playwright + Telegram + n8n)

## Visão Geral da Arquitetura

O sistema conecta 3 camadas principais em uma infraestrutura em container na nuvem (VPS):
1. **Bridge LinkedIn (`linkedin-bridge`):** Playwright rodando em Xvfb com Chromium persistente e API FastAPI.
2. **Telegram Bot Daemon:** Interface conversacional com Eduardo (`@funcionario_vip_bot`) operando em tempo real.
3. **Orquestrador n8n (`n8n-server`):** Automações agendadas de comentários e monitoramento analítico de visitantes Premium.

```
+-------------------------------------------------------------------------+
|                              TELEGRAM                                   |
|   - Link do LinkedIn (Post) --> Extração + IA Comentário + 1-Tap Publicação
|   - /post <tema>            --> Dual Draft (Story vs Arq) + Meta AI     |
|   - /visitantes             --> Relatório Instantâneo de Visitantes     |
|   - /status                 --> Diagnóstico de Saúde dos Serviços       |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                    LINKEDIN BRIDGE (FastAPI + Playwright)               |
|   - POST /analyze/post          --> Acessa URL, extrai autor e conteúdo |
|   - POST /engage/post           --> Curte o post e comenta com delay    |
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

---

### 1. Engajamento Sob Demanda em Posts de Terceiros (Colar Link no Chat)

Este é o fluxo mais rápido e frequente para construir autoridade diária no LinkedIn:
1. Eduardo encontra uma postagem interessante no feed do LinkedIn (ou de um influenciador/líder técnico) e copia o link (`https://www.linkedin.com/posts/...` ou link encurtado `https://lnkd.in/...`).
2. Cola o link diretamente na conversa com o bot no Telegram.
3. O bot reconhece a URL instantaneamente e aciona o endpoint `/analyze/post` na bridge do Playwright.
4. O Playwright acessa a postagem na sessão logada e extrai:
   - Nome do autor;
   - Texto completo da publicação.
5. O bot envia o texto extraído para o **DeepSeek v4.1** com a persona técnica de Eduardo Cardoso (instruções do `CONTEXT.md`), gerando um comentário inteligente, agregador e sem jargões corporativos.
6. O Telegram entrega a mensagem com os botões inline:
   - `[✅ Curtir e Comentar Post]`
   - `[🔄 Gerar Outra Opção]`
   - `[❌ Cancelar]`
7. Ao clicar em **`✅ Curtir e Comentar Post`**:
   - A bridge do Playwright abre o post;
   - Aciona o botão de reação ("Gostei");
   - Foca na caixa de comentário e digita o texto gerado simulando digitação humana realista;
   - Clica em "Publicar";
   - Retorna a confirmação imediata no Telegram.

---

### 2. Criação e Publicação Humanizada de Novos Posts (`/post <tema>`)

1. Eduardo envia `/post <tema ou ideia>` no Telegram.
2. O bot consulta o DeepSeek v4.1 usando as regras estritas anti-IA de `CONTEXT.md`.
3. Duas versões são entregues simultaneamente:
   - **Variação 1:** Bastidores & Storytelling Prático de Produção.
   - **Variação 2:** Arquitetura & Posicionamento de Engenharia.
4. Ao selecionar uma versão com 1 clique, o bot salva o rascunho e exibe o prompt calibrado para gerar a imagem no Meta AI (100% PT-BR, 16:9, Dark Mode).
5. Eduardo pode aprovar direto com `[Publicar Agora]` ou enviar a foto gerada no chat antes de confirmar.
6. O worker do Playwright publica no LinkedIn e retorna a confirmação no chat.

---

### 3. Monitor de Comentários Human-in-the-Loop (n8n a cada 30 min)

1. O n8n consulta `GET /comments/recent` na bridge a cada 30 minutos.
2. Se houver novo comentário de seguidor, o DeepSeek v4.1 gera uma réplica inteligente de colega para colega.
3. Alerta enviado no Telegram com botões: `[✅ Curtir e Responder]` e `[❌ Ignorar]`.
4. Ao clicar no botão, a resposta é publicada diretamente na thread correspondente no LinkedIn.

---

### 4. Monitor de Visitantes LinkedIn Premium (n8n a cada 4 horas)

1. O n8n consulta `GET /profile/views` a cada 4 horas.
2. Filtra visitantes inéditos via `seen_viewers.json` para evitar notificações repetidas.
3. O DeepSeek v4.1 elabora abordagem de 2 frases conectando o background do visitante a automações e IA.
4. Notificação detalhada enviada no Telegram destacando recrutadores e tomadores de decisão com link de 1 clique para o perfil.
