# Fluxo Operacional da Automação LinkedIn (v2 — Playwright + Telegram + n8n)

## Visão Geral da Arquitetura

O sistema conecta 3 camadas principais em uma infraestrutura em container na nuvem (VPS):
1. **Bridge LinkedIn (`linkedin-bridge`):** Playwright rodando em Xvfb com Chromium persistente e API FastAPI.
2. **Telegram Bot Daemon:** Interface conversacional com Eduardo (`@funcionario_vip_bot`) operando em tempo real.
3. **Orquestrador n8n (`n8n-server`):** Automações agendadas de comentários e monitoramento analítico de visitantes Premium.

```
+-------------------------------------------------------------------------+
|                              TELEGRAM                                   |
|   - /radar                  --> Ativa fila de oportunidades de líderes  |
|   - /lideres                --> Lista referências em IA monitoradas     |
|   - /adicionarlider <url>   --> Cadastra novo líder na watchlist        |
|   - Link do LinkedIn (Post) --> Extração + IA Comentário + 1-Tap Publicação
|   - /post <tema>            --> Dual Draft (Story vs Arq) + Meta AI     |
|   - /visitantes             --> Relatório Instantâneo de Visitantes     |
|   - /status                 --> Diagnóstico de Saúde dos Serviços       |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                    LINKEDIN BRIDGE (FastAPI + Playwright)               |
|   - GET  /radar/leaders         --> Lista watchlist de líderes em IA    |
|   - POST /radar/leaders         --> Adiciona novo líder (auto-extract)  |
|   - GET  /radar/scan            --> Varre publicações recentes nos feeds|
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
|   - Workflow Radar (09:30): Varredura diária de líderes + Notificação   |
|   - Workflow 1 (30 min):    Monitor de comentários + DeepSeek + Aprovação
|   - Workflow 2 (4 h):       Monitor de visitantes Premium + Abordagens  |
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

---

### 5. Ver Tela do Robô em Tempo Real (`/tela`, `/print` ou Botão no Menu)

1. Eduardo envia `/tela` (ou clica no botão `[📸 Ver Tela do Robô (Print ao Vivo)]` no `/menu`).
2. O bot envia mensagem de status imediata: *"Capturando tela ao vivo do navegador no servidor..."*.
3. O daemon do Telegram aciona o Playwright Manager na sessão ativa (`page.screenshot(type="png")`) sem interromper processos em andamento.
4. O binário PNG é empacotado via multipart e enviado via Telegram Bot API (`sendPhoto`).
5. A foto é entregue em alta resolução 1080p acompanhada do título da página, URL atual e status de autenticação.
6. A mensagem de origem do menu é atualizada com botões para `[⚡ Reabrir Menu Principal]` ou `[📸 Tirar Novo Print]`.

---

### 6. Central de Notificações de Erros e Alertas Críticos (n8n + Telegram)

1. Os workflows produtivos do n8n (`LinkedIn Comments Monitor` e `LinkedIn Profile Views Monitor`) possuem a configuração `settings.errorWorkflow = "ErrTr1gg3r999999"`.
2. Se qualquer nó falhar (ex: token expirado, instabilidade de rede ou DOM alterado no LinkedIn), o n8n intercepta a exceção antes de abortar silenciosamente.
3. O workflow `Hermes - Notificador de Erros Telegram` é disparado via nó nativo `n8n-nodes-base.errorTrigger`.
4. Uma requisição POST interna é enviada para `http://linkedin-bridge:8000/notify/error` contendo nome do workflow, nó que falhou, ID de execução e mensagem de erro.
5. A bridge formata um alerta prioritário visual com bloco de código e envia instantaneamente ao Telegram de Eduardo.
6. Eduardo pode a qualquer momento testar este canal de forma preventiva usando o comando `/testealerta` ou o botão `[🚨 Testar Notificação de Erro]` no `/menu`.

---

### 7. Radar de Líderes em IA — Sniper Engagement Diário (`/radar`, `/lideres`, `/adicionarlider`)

Este fluxo implementa a estratégia de crescimento acelerado de autoridade orgânica no LinkedIn por meio de interações diárias inteligentes em publicações de referências da área:
1. **Watchlist Curada:** Os perfis monitorados residem em `worker/ai_leaders.json`. Eduardo pode consultar a lista com `/lideres` ou cadastrar novos perfis enviando `/adicionarlider https://www.linkedin.com/in/perfil`. Ao adicionar, o Playwright visita a página, extrai o nome e a headline real e persiste a entrada.
2. **Varredura Automatizada:**
   - **Gatilho Agendado:** O workflow do n8n `LinkedIn Radar de Líderes em IA` executa de segunda a sexta-feira às 09:30 AM e aciona `GET /radar/scan?limit=3`.
   - **Gatilho Sob Demanda:** Eduardo pode enviar `/radar` ou tocar no botão `[🎯 Radar de Líderes em IA]` no `/menu` a qualquer momento no Telegram.
3. **Extração de Posts no Playwright:**
   - O robô acessa a aba de publicações recentes (`/recent-activity/all/`) dos perfis da watchlist de forma intercalada com delays humanos realistas (3s a 5s).
   - Extrai o URN da atividade, texto da postagem (>50 caracteres) e tempo de publicação.
   - Filtra postagens já vistas anteriormente consultando o registro persistente `session/seen_radar_posts.json`.
4. **Geração Anti-IA (DeepSeek v4.1):**
   - O post é processado pelo DeepSeek v4.1 com as diretrizes do `CONTEXT.md`: sem introduções vazias ("Excelente reflexão"), sem emojis corporativos exagerados, sem travessões longos artificiais (`—`) e com tom analítico sênior de colega para colega.
5. **Apresentação em Fila Interativa no Telegram:**
   - O bot apresenta a primeira oportunidade identificada com os botões:
     - `[✅ Curtir e Comentar Post]` — Publica a reação e o comentário via Playwright com delay humano (15-30s) e oferece botão para avançar para o próximo post.
     - `[🔄 Gerar Outra Opção]` — Gera uma versão alternativa de comentário para o mesmo post.
     - `[⏭️ Próximo Post]` — Pula para a próxima oportunidade da fila sem comentar.
     - `[❌ Encerrar]` — Finaliza a sessão do radar.
6. **Deduplicação & Proteção:**
   - Ao interagir ou pular, o URL canônico do post é registrado em `seen_radar_posts.json`, garantindo que o mesmo post nunca mais seja sugerido ou incomode o usuário.

