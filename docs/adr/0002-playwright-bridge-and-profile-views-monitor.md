# ADR 0002: Bridge Playwright Persistente e Monitor de Visitantes (LinkedIn Premium)

## Status
Aceito

## Contexto
O ecossistema oficial da API do LinkedIn impõe restrições severas para contas pessoais de criadores de conteúdo:
- Acesso restrito a endpoints de métricas de perfil;
- Ausência de webhook nativo para novos visitantes em contas LinkedIn Premium;
- Necessidade de manter uma sessão autenticada com cookies e fingerprint estáveis para evitar flags de segurança e checkpoints de verificação.

Além disso, visitantes do perfil no LinkedIn Premium (especialmente Tech Recruiters, Gestores de Engenharia e Tomadores de Decisão) representam leads com alto potencial de conversão para contratos e vagas, exigindo abordagem ágil, personalizada e profissional.

## Decisões Arquiteturais

1. **Bridge Headless com Playwright em Contexto Persistente (`worker/app.py`):**
   - Execução em container Docker com servidor virtual Xvfb (display :99).
   - Gerenciamento de sessão persistente em diretório de perfil Chromium isolado (`/app/session/profile`).
   - Automação sem flags de automação visíveis (`--disable-blink-features=AutomationControlled`, user agent realista e viewport full HD).

2. **Endpoint de Visitantes (`/profile/views`):**
   - Extrai lista estruturada de visitantes em `/analytics/profile-views/`.
   - Limpeza e parsing de nomes, headlines e tempos relativos da visita.
   - Heurística de classificação inteligente:
     - `isRecruiter`: Detecção de termos como *recruiter, talent, hunting, headhunter, rh*.
     - `isDecisionMaker`: Detecção de termos como *cto, ceo, founder, head, diretor, gerente, lead*.

3. **Orquestração via n8n (`workflows/linkedin_profile_views_monitor.json`):**
   - Agendamento a cada 4 horas (cadência humana segura).
   - Deduplicação em cache local (`seen_viewers.json`) para prevenir alertas repetidos.
   - Síntese com DeepSeek v4.1: Mensagem de aproximação profissional de 2-3 frases, estritamente orientada pelas regras anti-IA do `CONTEXT.md` (sem bajulação, sem emojis corporativos).
   - Entrega no Telegram com link do perfil e tags visuais em destaque.

4. **Operação Sob Demanda no Telegram:**
   - Adição do comando `/visitantes` e botão no `/menu` para consulta instantânea pelo usuário a qualquer momento.

## Consequências
- Acesso irrestrito a dados analíticos do LinkedIn Premium sem depender de APIs corporativas fechadas.
- Risco de banimento zero devido a requisições com cadência humana espaçada e sessão persistente idêntica a um navegador comum.
- Redução do tempo de resposta para oportunidades estratégicas de dias para minutos.
