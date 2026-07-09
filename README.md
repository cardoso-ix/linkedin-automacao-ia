# Automação LinkedIn — Agentes de IA

Automação diária de conteúdo no LinkedIn com **Make.com**, **OpenAI** (texto + imagem) e publicação automática às **8h** (America/Sao_Paulo).

Foco: **agentes de IA e automação inteligente** — posts humanizados para alcance (impressões, comentários, seguidores), com rota de **só texto** na maior parte da semana e **texto + charge editorial** em dias específicos.

**Portfólio** — [cardoso-ix.github.io/Portifolio](https://cardoso-ix.github.io/Portifolio/) · **LinkedIn** — [eduardo-cardoso](https://www.linkedin.com/in/eduardo-cardoso-213a02267)

## O que faz

Todo dia às 8h:

1. **GPT-4o** gera o post em português (gancho forte, lista, perguntas, hashtags)
2. **Router** decide o formato pelo dia da semana
3. **Seg–qua, sex–sáb:** publica **só texto** (Media Type Empty)
4. **Qui e dom:** **GPT-4o-mini** gera prompt de charge → **gpt-image-1.5** gera a imagem → LinkedIn **Article** com thumbnail
5. Calendário de **40 temas** rotativos por dia do mês

## Arquitetura

```
Schedule 8h (America/Sao_Paulo)
        │
        ▼
   HTTP 3 — OpenAI GPT-4o (texto do post)
        │
        ▼
     Router
        │
        ├── Charge (qui / dom)
        │      → HTTP 6 (prompt charge)
        │      → OpenAI Generate Image (gpt-image-1.5)
        │      → LinkedIn Article + thumbnail
        │
        └── Texto (fallback)
               → LinkedIn Empty (só conteúdo)
```

## Stack

| Camada | Tecnologia |
|--------|------------|
| Orquestração | Make.com |
| Texto | OpenAI GPT-4o |
| Prompt de imagem | OpenAI GPT-4o-mini |
| Imagem | OpenAI gpt-image-1.5 |
| Publicação | LinkedIn (OpenID Connect) |
| Agendamento | Schedule diário 08:00 |

## Destaques

- Texto **sem markdown** (LinkedIn não renderiza `**negrito**`)
- Tom humanizado, sem saudação forçada (“oi pessoal”)
- Gancho nas primeiras 2 linhas + perguntas que geram comentário
- Charge editorial premium (estilo charge BR / Wired), não stock photo
- Custo estimado ~**US$ 2/mês** com 1 post/dia (cabe em crédito OpenAI baixo)

## Estrutura do repositório

```
linkedin-automacao-ia/
├── README.md
├── docs/
│   ├── SETUP.md              # Passo a passo no Make
│   ├── TEMAS.md              # 40 temas do calendário
│   └── CHECKLIST.md          # Validação e erros comuns
├── prompts/
│   ├── http3-texto.json      # Body GPT-4o (texto)
│   └── http6-imagem.json     # Body GPT-4o-mini (prompt charge)
└── assets/
    └── preview.png           # Preview para portfólio
```

## Como usar

1. Conta Make + API key OpenAI + LinkedIn conectado
2. Monte o fluxo conforme [docs/SETUP.md](docs/SETUP.md)
3. Cole os JSONs de [prompts/](prompts/) nos módulos HTTP
4. Ative o cenário às 8h

## Custo estimado (1 post/dia)

| Item | Mês |
|------|-----|
| GPT-4o (texto) | ~US$ 0,90 |
| GPT-4o-mini (prompt) | ~US$ 0,03 |
| gpt-image-1.5 (2×/semana) | ~US$ 1,00 |
| **Total** | **~US$ 2,00** |

## Licença

Uso pessoal / portfólio. Adapte livremente.
