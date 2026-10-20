# Validation Evidence — code-smells-project

| Item | Value |
|---|---|
| Result | CLEAN |
| Failure type | — |
| Date | 2026-10-20 16:02 |
| Skill version | 154ab3e |
| Restore point | 154ab3e |
| Audit report | reports/audit-project-1.md |

## Environment
- Dependency environment: .venv/ (reused)
- Setup steps: none
- Boot command: `.venv/bin/python app.py` (env: `ADMIN_TOKEN=<token gerado para esta execução>`)
- Port: 5000 (free before boot: yes)
- Runtime artifacts removed: loja.db
- Code fingerprint: 2451202911-1260 at first boot / 2451202911-1260 at end (unchanged: yes)

## Boot
```text
==================================================
SERVIDOR INICIADO
Rodando em http://127.0.0.1:5000
==================================================
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
2026-10-20 15:58:06,649 INFO 127.0.0.1 - - [20/Oct/2026 15:58:06] "GET /health HTTP/1.1" 200 -
2026-10-20 15:58:11,546 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "GET /produtos HTTP/1.1" 200 -
2026-10-20 15:58:11,676 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "POST /produtos HTTP/1.1" 201 -
2026-10-20 15:58:11,727 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "POST /usuarios HTTP/1.1" 201 -
2026-10-20 15:58:11,736 INFO Pedido 1 criado para usuario 2 - notificacoes enviadas (email, sms, push)
2026-10-20 15:58:11,737 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "POST /pedidos HTTP/1.1" 201 -
2026-10-20 15:58:11,752 INFO Pedido 1 aprovado - preparar envio
2026-10-20 15:58:11,752 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "PUT /pedidos/1/status HTTP/1.1" 200 -
2026-10-20 15:58:11,759 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "DELETE /produtos/11 HTTP/1.1" 200 -
2026-10-20 15:58:11,766 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "POST /admin/query HTTP/1.1" 200 -
2026-10-20 15:58:11,774 INFO Banco de dados resetado
2026-10-20 15:58:11,774 INFO 127.0.0.1 - - [20/Oct/2026 15:58:11] "POST /admin/reset-db HTTP/1.1" 200 -
```

## Behavior baseline
Source: captured

| # | Method | Path | Baseline status | Baseline shape | After status | After shape | Match |
|---|---|---|---|---|---|---|---|
| 1 | GET | /produtos | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso} | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso} | ✓ |
| 2 | GET | /produtos/busca | 200 | {dados:list<{...}>,sucesso,total} | 200 | {dados:list<{...}>,sucesso,total} | ✓ |
| 3 | GET | /produtos/<id> | 200 | {dados:{...},sucesso} | 200 | {dados:{...},sucesso} | ✓ |
| 4 | GET | /usuarios | 200 | {dados:list<{criado_em,email,id,nome,senha,tipo}>,sucesso} | 200 | {dados:list<{criado_em,email,id,nome,tipo}>,sucesso} | declared |
| 5 | GET | /usuarios/<id> | 200 | {dados:{criado_em,email,id,nome,senha,tipo},sucesso} | 200 | {dados:{criado_em,email,id,nome,tipo},sucesso} | declared |
| 6 | GET | /pedidos | 200 | {dados:list<>,sucesso} | 200 | {dados:list<>,sucesso} | ✓ |
| 7 | GET | /pedidos/usuario/<id> | 200 | {dados:list<>,sucesso} | 200 | {dados:list<>,sucesso} | ✓ |
| 8 | GET | /relatorios/vendas | 200 | {dados:{desconto_aplicavel,faturamento_bruto,faturamento_liquido,pedidos_aprovados,pedidos_cancelados,pedidos_pendentes,ticket_medio,total_pedidos},sucesso} | 200 | {dados:{desconto_aplicavel,faturamento_bruto,faturamento_liquido,pedidos_aprovados,pedidos_cancelados,pedidos_pendentes,ticket_medio,total_pedidos},sucesso} | ✓ |
| 9 | GET | /health | 200 | {ambiente,counts:{pedidos,produtos,usuarios},database,db_path,debug,secret_key,status,versao} | 200 | {ambiente,counts:{pedidos,produtos,usuarios},database,status,versao} | declared |
| 10 | GET | / | 200 | {endpoints:{...},mensagem,versao} | 200 | {endpoints:{...},mensagem,versao} | ✓ |
| 11 | POST | /login | 200 | {dados:{email,id,nome,tipo},mensagem,sucesso} | 200 | {dados:{email,id,nome,tipo},mensagem,sucesso} | ✓ |
| 12 | POST | /produtos | 201 | {dados:{id},mensagem,sucesso} | 201 | {dados:{id},mensagem,sucesso} | ✓ |
| 13 | POST | /usuarios | 201 | {dados:{id},sucesso} | 201 | {dados:{id},sucesso} | ✓ |
| 14 | POST | /pedidos | 201 | {dados:{pedido_id,total},mensagem,sucesso} | 201 | {dados:{pedido_id,total},mensagem,sucesso} | ✓ |
| 15 | PUT | /produtos/<id> | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 16 | PUT | /pedidos/<id>/status | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 17 | DELETE | /produtos/<id> | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 18 | POST | /admin/query | 200 | {dados:list<{total}>,sucesso} | 200 | {dados:list<{total}>,sucesso} | declared |
| 19 | POST | /admin/reset-db | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | declared |

## Declared contract changes
| Endpoint | Change | Finding fixed |
|---|---|---|
| GET /usuarios | Campo "senha" removido de cada objeto de usuário na resposta | AP-09 |
| GET /usuarios/<id> | Campo "senha" removido do objeto de usuário na resposta | AP-09 |
| GET /health | Campos "db_path", "debug" e "secret_key" removidos da resposta ("ambiente" preservado) | AP-01, AP-09 |
| POST /admin/reset-db | Agora exige o cabeçalho `X-Admin-Token` igual a `ADMIN_TOKEN`; sem `ADMIN_TOKEN` configurado → 403; token ausente/errado → 401 | AP-04 |
| POST /admin/query | Mesma proteção de `X-Admin-Token`/`ADMIN_TOKEN` descrita acima | AP-04 |

## Re-audit
Reviewer: subagent
Remaining anti-patterns: 0
