# ADR 0001: Motor de Publicação Humanizada Anti-IA no LinkedIn

## Status
Aceito

## Contexto
Publicações automatizadas por modelos de linguagem no LinkedIn frequentemente falham em gerar conexão e credibilidade por apresentarem marcas óbvias de IA:
- Uso indiscriminado de emojis em tópicos (🚀, 💡, 🔥, 👏);
- Travessões tipográficos artificiais (`—`);
- Chamadas para ação previsíveis e apelativas ("O que você acha? Comente abaixo! 👇");
- Aberturas clichês ("No cenário dinâmico atual...");
- Jargões corporativos vazios ("mindset", "disruptivo", "ecossistema").

Eduardo Cardoso atua em Engenharia de Automação, IA Agêntica e Integrações (n8n, Python, LLMs). Sua autoridade no mercado depende de uma voz de "pragmático de trincheira", que compartilha desafios reais de produção, custos, limites técnicos e lições aprendidas de colega sênior para colega sênior.

## Decisões Arquiteturais

1. **Anti-AI System Prompting:**
   - O prompt do DeepSeek v4.1 recebe proibições explícitas contra emojis corporativos, travessões de IA, listas automáticas e CTAs forçados.
   - Restrição de extensão entre 1.000 e 1.600 caracteres com quebras de linha para leitura em mobile.

2. **Fluxo de Dupla Proposta no Telegram:**
   - O comando `/post <ideia>` aciona a geração simultânea de duas variações de tom:
     - **Variação 1 (Bastidores / Storytelling de Trincheira):** Narrativa baseada em caso real, problema encontrado e lição prática.
     - **Variação 2 (Arquitetura / Posicionamento Técnico):** Análise direta de engenharia comparando soluções comuns frágeis vs abordagens escaláveis.
   - O usuário escolhe via botão inline qual variação deseja utilizar.

3. **Ciclo de Aprovação e Mídia:**
   - Ao escolher uma variação, ela é registrada como o rascunho ativo. O usuário pode clicar imediatamente em `[🚀 Confirmar e Publicar]` ou anexar uma imagem enviando a foto no chat.

## Consequências
- Posts com alto engajamento orgânico e sem cheiro de IA gerada em massa.
- Redução de fricção: com 2 opções por comando, o usuário raramente precisa pedir outra geração.
- Preservação da reputação técnica de Eduardo Cardoso.
