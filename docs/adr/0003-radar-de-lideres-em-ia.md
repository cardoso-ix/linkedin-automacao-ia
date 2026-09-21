# ADR 0003: Radar de Líderes em IA e Engajamento Sniper Diário

## Status
Aceito

## Contexto
O algoritmo do LinkedIn prioriza perfis que geram discussões qualificadas nos posts de maior alcance da sua rede (autoridade tópica e Social Selling Index - SSI).
A estratégia tradicional de "postar e rezar" possui tração lenta quando comparada à tática de **Engajamento Sniper**:
- Comentar de forma consistente (3 a 7 vezes por dia) nos posts recentes dos líderes mais influentes do setor técnico (IA, LLMs, Automação, Engenharia de Software);
- Agregar valor real com reflexões de engenharia de trincheira em vez de elogios genéricos;
- Reter a atenção de outros comentaristas e seguidores do líder, convertendo impressões em visitas qualificadas de perfil e convites de conexão.

Para tornar essa rotina viável e escalável sem consumir horas diárias do criador de conteúdo, era necessário automatizar a descoberta e triagem de posts recentes desses líderes, mantendo controle humano absoluto (*human-in-the-loop*) na aprovação final.

## Decisões Arquiteturais

1. **Watchlist Dinâmica de Líderes (`worker/ai_leaders.json`):**
   - Base inicial curada com referências de mercado em IA, Automação e Engenharia no Brasil (Anderson Pereira, Luciano Santos, Sandro Valichek, Arthur Gurgel, Diego Barreto, Fabio Akita, Miguel Fernandez).
   - Comando conversacional `/adicionarlider <url>` e endpoint `POST /radar/leaders` para inclusão instantânea de novos perfis com extração automática de nome e headline via Playwright.

2. **Varredura Ativa no Playwright (`GET /radar/scan`):**
   - Acesso direto à aba cronológica de atividades dos perfis monitorados (`/in/{handle}/recent-activity/all/`).
   - Extração do URN canônico, texto (>50 caracteres) e tempo relativo de postagem.
   - Embaralhamento da ordem de visitação e delays humanos (2s a 5s) para comportamento indistinguível de navegação real.
   - Deduplicação persistente em `session/seen_radar_posts.json` para garantir que o mesmo post nunca seja apresentado duas vezes.

3. **Geração Anti-IA via DeepSeek v4.1:**
   - Modo de engajamento calibrado pelo `CONTEXT.md`: sem introduções vazias ("Excelente post!", "Concordo"), sem emojis corporativos exagerados (🚀, 🔥, 💡), sem travessões longos de IA (`—`) e tom de colega sênior pragmático.

4. **Fila Interativa no Telegram Bot (`worker/telegram_bot.py`):**
   - Apresentação sequencial das oportunidades com botões inline de 1 clique:
     - `[✅ Curtir e Comentar Post]` — Aciona Playwright com delay humano (15–30s), curte a publicação e digita o comentário.
     - `[🔄 Gerar Outra Opção]` — Solicita uma nova abordagem ao DeepSeek v4.1.
     - `[⏭️ Próximo Post]` — Avança para a próxima oportunidade sem comentar.
     - `[❌ Encerrar]` — Finaliza a sessão do radar.
   - Adição do botão de ação rápida `[🎯 Radar de Líderes em IA]` no menu principal e comandos `/radar` e `/lideres`.

5. **Agendamento no n8n (`workflows/linkedin_radar_monitor.json`):**
   - Disparo automático de segunda a sexta-feira às 09:30 AM (horário de pico de engajamento no LinkedIn).
   - Conexão nativa com `settings.errorWorkflow = "ErrTr1gg3r999999"` para resiliência operacional.

## Consequências
- Aumento orgânico significativo do alcance e impressões do perfil de Eduardo Cardoso junto ao público-alvo de IA e Tecnologia.
- Execução diária da rotina de autoridade em menos de 2 minutos pelo Telegram.
- Preservação da autenticidade da voz técnica sem jamais publicar comentários robotizados ou vazios.
