# Checklist

## Antes de ativar

- [ ] API key OpenAI nos Headers HTTP 3 e HTTP 6
- [ ] Body HTTP 3 colado (sem markdown / asteriscos)
- [ ] Body HTTP 6 fixo (sem mapear HTTP 3)
- [ ] Router: Charge = qui/dom; Texto = fallback Yes
- [ ] LinkedIn texto = Empty
- [ ] LinkedIn charge = Article + Response Image Data
- [ ] Schedule 08:00 America/Sao_Paulo
- [ ] Run once OK
- [ ] Cenário ON

## Erros comuns

| Erro | Solução |
|------|---------|
| Asteriscos no post | Reforçar regra FORMATACAO no HTTP 3 |
| Bad control character JSON | HTTP 6 sem mapear HTTP 3 |
| 401 Unauthorized | Bearer sk-... correto |
| LinkedIn sem imagem | Thumbnail = Response Image Data |
| Quinta cai em texto | Filtro Charge = Thursday OR Sunday primeiro |

## Pós-publicação (manual)

- [ ] Comentar no próprio post em 5–10 min (cascata)
- [ ] Responder comentários em até 2–4 h
