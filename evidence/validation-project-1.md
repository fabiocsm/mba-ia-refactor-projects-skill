# Validation Evidence — code-smells-project

| Item | Value |
|---|---|
| Result | CLEAN |
| Failure type | — |
| Date | 2026-10-23 05:45 |
| Skill version | 1ee20f3 |
| Restore point | 913dfc6 |
| Audit report | reports/audit-project-1.md |

## Environment
- Dependency environment: .venv/ (reused)
- Setup steps: none (schema e seed executados automaticamente no primeiro boot via `database.init_app`)
- Boot command: `ADMIN_TOKEN=<token gerado na execução> python app.py`
- Port: 5000 (free before boot: yes)
- Runtime artifacts removed: loja.db
- Code fingerprint: 851997682-1360 at first boot / 851997682-1360 at end (unchanged: yes)

## Boot
```text
2026-10-23 05:39:46,959 INFO __main__ Servidor iniciado em http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
2026-10-23 05:39:46,964 INFO werkzeug WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2026-10-23 05:39:46,964 INFO werkzeug Press CTRL+C to quit
2026-10-23 05:39:50,661 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:50] "GET /health HTTP/1.1" 200 -
2026-10-23 05:39:59,510 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET / HTTP/1.1" 200 -
2026-10-23 05:39:59,519 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /produtos HTTP/1.1" 200 -
2026-10-23 05:39:59,528 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /produtos/busca?q=mouse HTTP/1.1" 200 -
2026-10-23 05:39:59,536 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /produtos/2 HTTP/1.1" 200 -
2026-10-23 05:39:59,543 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /usuarios HTTP/1.1" 200 -
2026-10-23 05:39:59,550 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /usuarios/2 HTTP/1.1" 200 -
2026-10-23 05:39:59,558 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /pedidos HTTP/1.1" 200 -
2026-10-23 05:39:59,565 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /pedidos/usuario/2 HTTP/1.1" 200 -
2026-10-23 05:39:59,573 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /relatorios/vendas HTTP/1.1" 200 -
2026-10-23 05:39:59,580 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "GET /health HTTP/1.1" 200 -
2026-10-23 05:39:59,630 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "POST /login HTTP/1.1" 200 -
2026-10-23 05:39:59,638 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "POST /produtos HTTP/1.1" 201 -
2026-10-23 05:39:59,689 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "POST /usuarios HTTP/1.1" 201 -
2026-10-23 05:39:59,698 INFO controllers.pedido_controller Pedido criado id=1 usuario_id=2
2026-10-23 05:39:59,698 INFO controllers.pedido_controller Notificacao enviada: email, sms e push para usuario_id=2
2026-10-23 05:39:59,698 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "POST /pedidos HTTP/1.1" 201 -
2026-10-23 05:39:59,706 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "PUT /produtos/11 HTTP/1.1" 200 -
2026-10-23 05:39:59,714 INFO controllers.pedido_controller Notificacao: pedido 1 aprovado, preparar envio
2026-10-23 05:39:59,714 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "PUT /pedidos/1/status HTTP/1.1" 200 -
2026-10-23 05:39:59,722 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "DELETE /produtos/11 HTTP/1.1" 200 -
2026-10-23 05:39:59,729 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "POST /admin/query HTTP/1.1" 200 -
2026-10-23 05:39:59,736 INFO controllers.admin_controller Banco de dados resetado
2026-10-23 05:39:59,736 INFO werkzeug 127.0.0.1 - - [23/Oct/2026 05:39:59] "POST /admin/reset-db HTTP/1.1" 200 -
```

## Behavior baseline
Source: captured

| # | Method | Path | Baseline status | Baseline shape | After status | After shape | Match |
|---|---|---|---|---|---|---|---|
| 1 | GET | / | 200 | {endpoints:{health,login,pedidos,produtos,relatorios,usuarios},mensagem,versao} | 200 | {endpoints:{health,login,pedidos,produtos,relatorios,usuarios},mensagem,versao} | ✓ |
| 2 | GET | /produtos | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso} | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso} | ✓ |
| 3 | GET | /produtos/busca?q=mouse | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso,total} | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso,total} | ✓ |
| 4 | GET | /produtos/2 | 200 | {dados:{ativo,categoria,criado_em,descricao,estoque,id,nome,preco},sucesso} | 200 | {dados:{ativo,categoria,criado_em,descricao,estoque,id,nome,preco},sucesso} | ✓ |
| 5 | GET | /usuarios | 200 | {dados:list<{criado_em,email,id,nome,senha,tipo}>,sucesso} | 200 | {dados:list<{criado_em,email,id,nome,tipo}>,sucesso} | declared |
| 6 | GET | /usuarios/2 | 200 | {dados:{criado_em,email,id,nome,senha,tipo},sucesso} | 200 | {dados:{criado_em,email,id,nome,tipo},sucesso} | declared |
| 7 | GET | /pedidos | 200 | {dados:list<>,sucesso} | 200 | {dados:list<>,sucesso} | ✓ |
| 8 | GET | /pedidos/usuario/2 | 200 | {dados:list<>,sucesso} | 200 | {dados:list<>,sucesso} | ✓ |
| 9 | GET | /relatorios/vendas | 200 | {dados:{desconto_aplicavel,faturamento_bruto,faturamento_liquido,pedidos_aprovados,pedidos_cancelados,pedidos_pendentes,ticket_medio,total_pedidos},sucesso} | 200 | {dados:{desconto_aplicavel,faturamento_bruto,faturamento_liquido,pedidos_aprovados,pedidos_cancelados,pedidos_pendentes,ticket_medio,total_pedidos},sucesso} | ✓ |
| 10 | GET | /health | 200 | {ambiente,counts:{pedidos,produtos,usuarios},database,db_path,debug,secret_key,status,versao} | 200 | {ambiente,counts:{pedidos,produtos,usuarios},database,status,versao} | declared |
| 11 | POST | /login | 200 | {dados:{email,id,nome,tipo},mensagem,sucesso} | 200 | {dados:{email,id,nome,tipo},mensagem,sucesso} | ✓ |
| 12 | POST | /produtos | 201 | {dados:{id},mensagem,sucesso} | 201 | {dados:{id},mensagem,sucesso} | ✓ |
| 13 | POST | /usuarios | 201 | {dados:{id},sucesso} | 201 | {dados:{id},sucesso} | ✓ |
| 14 | POST | /pedidos | 201 | {dados:{pedido_id,total},mensagem,sucesso} | 201 | {dados:{pedido_id,total},mensagem,sucesso} | ✓ |
| 15 | PUT | /produtos/11 | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 16 | PUT | /pedidos/1/status | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 17 | DELETE | /produtos/11 | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 18 | POST | /admin/query | 200 | {dados:list<{COUNT(*)}>,sucesso} | 200 | {dados:list<{COUNT(*)}>,sucesso} | ✓ |
| 19 | POST | /admin/reset-db | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |

## Declared contract changes
| Endpoint | Change | Finding fixed |
|---|---|---|
| GET /usuarios | campo `senha` removido de cada item da lista | AP-09 |
| GET /usuarios/<id> | campo `senha` removido | AP-09 |
| GET /health | campos `debug`, `secret_key` e `db_path` removidos da resposta | AP-09 |
| POST /admin/reset-db | exige cabeçalho `X-Admin-Token`; sem `ADMIN_TOKEN` configurado responde 403, com token ausente/incorreto responde 401 | AP-04 |
| POST /admin/query | mesma proteção de `X-Admin-Token` acima | AP-04 |

## Re-audit
Reviewer: subagent
Remaining anti-patterns: 0
