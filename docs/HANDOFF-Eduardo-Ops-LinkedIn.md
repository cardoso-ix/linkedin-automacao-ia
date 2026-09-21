# Handoff Ops LinkedIn — Eduardo Cardoso
Atualizado: 14/09/2026 ~23:23 America/Sao_Paulo
Origem: Chefe | Coordenação LinkedIn (Grok Bot)
Objetivo: transferir contexto completo para outro bot/assistente.

---

## 1. Quem é o Eduardo

- **Nome:** Eduardo Cardoso
- **Idade (guia):** ~30 anos
- **Cidade:** Chapecó/SC, Brasil
- **Fuso:** America/Sao_Paulo (UTC-3)
- **LinkedIn:** https://www.linkedin.com/in/eduardo-cardoso-213a02267
- **Portfólio:** https://cardoso-ix.github.io/Portifolio/
- **Perfil profissional:** interseção de **suporte técnico / Help Desk** + **automações com IA** (n8n, OpenAI, APIs/webhooks, LLMs/RAG/agentes em formação)
- **Pós:** Tech Agentes de IA — FIAP + Alura (em andamento)
- **Formação adicional (perfil de vagas):** MBA Controladoria e Finanças; Administração; Automação Industrial (Senai)

### Experiência (resumo — para contexto, NÃO usar como refrão de post)
- Técnico de Laboratório de Calibração — Fluxo Metrologia (Jul/2025–atual) — nos posts citar só como “indústria/calibração”, **nunca o nome da empresa**
- Coordenador de Logística — Sandimas (Mai/2023–Fev/2025)
- Suporte Técnico Help Desk — Crescer Sistemas (Fev/2022–Mai/2023)
- Orçamentista — MR Indústria Gráfica
- Metrologista — JBS Foods — nos posts: “indústria de alimentos”, **nunca JBS**

### Skills-chave
Help Desk N1/N2, n8n, OpenAI/prompt, APIs/webhooks/integrações, LLMs/RAG/agentes (em formação)

### Arquivos de currículo/perfil
- `linkedin-ops/curriculo-eduardo.pdf`
- `linkedin-ops/perfil-busca-vagas.md`

---

## 2. Como ele quer soar no LinkedIn

### Tom (obrigatório desde 14/09/2026)
- Casual e simples, **tecnicamente bem construído**, bom de ler
- **Sempre** uma dica ou informação útil a mais
- Direto, leve, PT-BR natural
- Prosa corrida (texto corrido), parágrafos curtos
- 1000–1800 caracteres; 3–5 hashtags CamelCase no final

### Evitar
- Emojis
- Travessão / hífen de lista
- Markdown no texto do post
- URLs no corpo (salvo pedido explícito)
- Corporatês, bajulação, hashtag spam
- Inventar experiência
- **Enaltecer trajetória / mini currículo**
- Refrões: “vim da indústria”, “passei por suporte”, “hoje estudo X na pós”, “minha jornada”
- Nome da empresa dele nos posts
- Posts guru / fora da curva / extraordinários demais
- Posts consecutivos com o mesmo assunto/ângulo (checar distância temática)

### Âncora ok
Help Desk, n8n, VPS (quando existia), webhooks, fila, ticket, fluxo — como **assunto**, não como autoelogio

### Fontes de estilo
- `linkedin-ops/guia-texto-posts.md`
- `linkedin-ops/tom-de-voz.md`

---

## 3. Imagens de post

### Estilo principal (Lucíola dark-tech)
- Vertical **4:5**
- Infográfico editorial dark-tech (não fotorrealismo)
- Fundo preto / azul-marinho
- Tipografia grande, cards/grids, ícones flat, mockups UI
- Sem selfie/stock/foto realista do Eduardo na capa (avatar flat ok)
- Foto realista só no avatar do perfil
- Alternar layouts **A–E**: A assimétrica, B fluxo, C before/after, D quote, E dashboard
- Evitar o mesmo padrão visual todo dia (ex.: grade de 4 cards idêntica)

### Exceção recente (15/09)
Eduardo aprovou capa **retro CRT / lo-fi coder** (nostalgia anos 90) para o post “TAREFA CERTA”. Continua ok variar se ele pedir “nessa pegada”.

Referência visual que ele gosta: Lucíola Coelho — https://www.linkedin.com/in/luciola-coelho-agencia-de-ia/

---

## 4. Arquitetura atual (desde 13–14/09/2026)

### Fonte de verdade
**100% Grok Bot + browser LinkedIn.**  
**VPS / Hermes / n8n Hostinger: OFF** (Eduardo sem VPS). Não chamar webhooks `hermes-linkedin-*`.

### Coordenação
- **Chefe | Coordenação LinkedIn:** recebe demandas do Eduardo, prioriza, manda aos especialistas, devolve o que importa
- Eduardo prefere falar pelo Chefe em vez de cada bot isolado (exceto ajuste fundo num ramo)

### Time Ops LinkedIn (grupo)
| Agente | Papel |
|--------|--------|
| Posts \| Lucario | Texto + prompt Meta; post 8h no browser após ok+foto |
| Comentários \| Jolteon | Curte + responde comentários nos posts do Eduardo |
| Engajamento \| Eevee | Curte + comenta em links que Eduardo/Chefe mandam |
| Conexões \| Gengar | Follow mesclado (ver seção 5) |
| Vagas \| Alakazam | Busca vagas só sob pedido explícito |

### Outros (fora Ops LinkedIn, mas relevante)
- **Pikachu \| Geral:** suporte técnico / textos gerais; **não** subordinado ao Chefe; WhatsApp réplica/dashboard é com Pikachu
- Chefe **não** assume Replica WhatsApp (handoff 09/09)

---

## 5. Rotinas ativas (America/Sao_Paulo)

| Rotina | Quando | O que faz |
|--------|--------|-----------|
| Chefe — abrir o dia Ops | Seg–sex 7:50 | Lembra o time dos slots; sem spam matinal ao Eduardo se ok |
| Lucario — post browser (one-shot) | Sob demanda / 15/09 8h | Publica texto+foto aprovados no LinkedIn via browser |
| Lucario — bom-dia + link | Seg–sex 8:05 | Texto curto pra Eduardo colar noutro grupo + link do post |
| Gengar — follow mesclado | Ver abaixo | 1 Seguir por slot |
| Jolteon — comentários | Todo dia 11:30 e 20h | Último + penúltimo post |
| Posts Lucario pacote | Dom–qui 22h | Texto + prompt Meta pra aprovação |
| Relatório diário | Todo dia 22h | Um bloco só resumindo o dia |

### Gengar — detalhe (ATIVO)
- **Seg / qua / sex:** 1 follow/hora, **8h–18h** (~10/dia) — cron `0 8-17 * * 1,3,5`
- **Ter / qui:** 1 follow a cada 2h às **15, 17, 19, 21, 23** (5/dia)
- Fluxo: abrir **1** perfil → **Seguir** → fechar
- **Zero Connect / convite automático**
- Alvos: recrutadores IA/Tech e profissionais Chapecó/região
- Se LinkedIn alertar/limitar: **parar na hora** e avisar Eduardo
- Contexto: em 14/09 LinkedIn alertou “muitos perfis”; saímos de 30 convites/dia

### Anti-duplicata (Eevee + Jolteon)
Antes de comentar/responder: checar se já existe comentário/resposta do Eduardo no post/fio. Se tiver: **não duplicar**; só curtir se faltar.

### Comunicação com Eduardo
- Relatório **único às 22h**, um texto só, seções claras
- Sem pings de progresso durante o dia
- **Alertar na hora** se: rotina falhou, login, bloqueio LinkedIn, post não saiu, alerta de segurança

---

## 6. Fluxo de post diário

1. **22h (dom–qui):** Lucario/Chefe entrega tema + texto + prompt Meta → Eduardo aprova
2. Eduardo gera imagem (Meta AI) e manda a foto
3. **8h:** Lucario publica no **browser** LinkedIn (texto EXATO + imagem)
4. **8:05:** Chefe manda bom-dia + link (só pra Eduardo colar noutro grupo; não postar no lugar dele)

Aprovação **sempre** antes de publicar.

### Próximo post agendado (15/09 8h)
- Texto: “tarefa certa / ferramenta certa / stack” (inspirado em post Lucíola, sem copiar)
- Foto: `linkedin-ops/posts/foto-2026-09-15.jpg` (retro CRT)
- Rascunho: `linkedin-ops/posts/rascunho-2026-09-15.md`
- One-shot: Lucario — post 15/09 browser 8h

### Post recente
- GPT-6 Astra (14/09): https://www.linkedin.com/feed/update/urn:li:activity:7505219054735974401/

---

## 7. Vagas (Alakazam)

Só sob pedido explícito. Filtros confirmados:
- Remoto BR e/ou Chapecó/região
- Help Desk/suporte; automação/n8n/integrações; agentes IA/LLMs
- Júnior–pleno
- Não candidatar sozinho — só pesquisar e priorizar

---

## 8. Histórico técnico relevante (Hermes — legado OFF)

Antes existia n8n Hostinger (`srv1897392.hstgr.cloud`) com webhooks:
- hermes-linkedin-texto / foto / post / engage / reply-comments
- Auth header `x-hermes-secret` (secret no cofre do box; **não colar em chat**)

**Desde 13/09/2026: OFF.** Docs marcados como histórico em `linkedin-ops/hermes-webhooks.md`.

---

## 9. Preferências de operação

- Passar demandas LinkedIn pelo **Chefe**
- Imagens profissionais, variar layout
- Posts dias consecutivos com distância temática
- Eevee: engaja **qualquer** link que Eduardo mandar (adapta comentário); reload confirma like+comment
- Jolteon: publica respostas **sem revisão** (tom do Eduardo)
- Gengar antigo era convite vazio 10×3/dia; **substituído** pelo follow mesclado

---

## 10. O que o próximo bot deve fazer no dia a dia

1. Manter tom casual + dica; sem mini currículo
2. Coordenar Lucario/Jolteon/Eevee/Gengar/Alakazam conforme papéis
3. Post 8h só com ok + foto; browser only
4. Gengar: 1 follow/slot no calendário mesclado; stop se alerta
5. Anti-duplicata em Eevee/Jolteon
6. Relatório 22h em um bloco; alertas de falha na hora
7. Não reativar Hermes sem VPS/nova ordem do Eduardo

---

## 11. Arquivos úteis no box do Chefe

```
linkedin-ops/
  STATUS-OPS.md
  guia-texto-posts.md
  tom-de-voz.md
  perfil-busca-vagas.md
  curriculo-eduardo.pdf
  posts/rascunho-AAAA-MM-DD.md
  posts/foto-AAAA-MM-DD.jpg
  conexoes/
  eevee/
  jolteon/
  HANDOFF-PARA-OUTRO-BOT.md  (este arquivo)
```

---

## 12. Segredos / segurança

- Não incluir tokens no handoff para chat.
- Conta LinkedIn do Eduardo: browser logado no ambiente dos bots (sessão).
- Se pedir login/2FA: parar e pedir ao Eduardo.

---

Fim do handoff. Qualquer dúvida: alinhar com Eduardo Cardoso antes de mudar ritmo de Gengar ou religar n8n.
