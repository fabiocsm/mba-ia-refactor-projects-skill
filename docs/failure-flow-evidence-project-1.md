# Validation Evidence — code-smells-project

| Item | Value |
|---|---|
| Result | FAILED |
| Failure type | skill |
| Date | 2026-10-20 13:23 |
| Skill version | 3e425ec |
| Restore point | 3e425ec |
| Audit report | reports/audit-project-1.md |

## Environment
- Dependency environment: .venv/ (reused)
- Setup steps: none (schema e seed executados automaticamente em `database.init_app` no primeiro boot)
- Boot command: `PYTHONDONTWRITEBYTECODE=1 ADMIN_TOKEN=<token gerado> .venv/bin/python app.py`
- Port: 5000 (free before boot: yes)
- Runtime artifacts removed: loja.db
- Code fingerprint: 2288942148-1292 at first boot / not executed at end (unchanged: not executed — verificação (d) não alcançada, ver Diagnosis)

## Boot
```text
2026-10-20 13:23:25,098 INFO __main__ Servidor iniciado em http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
2026-10-20 13:23:25,101 INFO werkzeug WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2026-10-20 13:23:25,101 INFO werkzeug Press CTRL+C to quit
2026-10-20 13:23:34,782 INFO werkzeug 127.0.0.1 - - [20/Oct/2026 13:23:34] "GET /health HTTP/1.1" 200 -
2026-10-20 13:23:39,469 INFO werkzeug 127.0.0.1 - - [20/Oct/2026 13:23:39] "GET /produtos HTTP/1.1" 200 -
2026-10-20 13:23:39,679 INFO controllers.admin_controller Banco de dados resetado via endpoint administrativo
2026-10-20 13:23:39,679 INFO werkzeug 127.0.0.1 - - [20/Oct/2026 13:23:39] "POST /admin/reset-db HTTP/1.1" 200 -
2026-10-20 13:23:39,686 INFO werkzeug 127.0.0.1 - - [20/Oct/2026 13:23:39] "POST /admin/query HTTP/1.1" 200 -
```
(log completo sem tracebacks; trecho acima omite as linhas intermediárias de requisição por brevidade — todas 200/201, sem erro)

## Behavior baseline
Source: captured

| # | Method | Path | Baseline status | Baseline shape | After status | After shape | Match |
|---|---|---|---|---|---|---|---|
| 1 | GET | /produtos | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso} | 200 | {dados:list<{ativo,categoria,criado_em,descricao,estoque,id,nome,preco}>,sucesso} | ✓ |
| 2 | GET | /produtos/busca | 200 | {dados:list<{...}>,sucesso,total} | 200 | {dados:list<{...}>,sucesso,total} | ✓ |
| 3 | GET | /produtos/<id> | 200 | {dados:{ativo,categoria,criado_em,descricao,estoque,id,nome,preco},sucesso} | 200 | {dados:{ativo,categoria,criado_em,descricao,estoque,id,nome,preco},sucesso} | ✓ |
| 4 | GET | /usuarios | 200 | {dados:list<{criado_em,email,id,nome,senha,tipo}>,sucesso} | 200 | {dados:list<{criado_em,email,id,nome,tipo}>,sucesso} | declared |
| 5 | GET | /usuarios/<id> | 200 | {dados:{criado_em,email,id,nome,senha,tipo},sucesso} | 200 | {dados:{criado_em,email,id,nome,tipo},sucesso} | declared |
| 6 | POST | /login | 200 | {dados:{email,id,nome,tipo},mensagem,sucesso} | 200 | {dados:{email,id,nome,tipo},mensagem,sucesso} | ✓ |
| 7 | GET | /pedidos | 200 | {dados:list<>,sucesso} | 200 | {dados:list<>,sucesso} | ✓ |
| 8 | GET | /pedidos/usuario/<id> | 200 | {dados:list<>,sucesso} | 200 | {dados:list<>,sucesso} | ✓ |
| 9 | GET | /relatorios/vendas | 200 | {dados:{desconto_aplicavel,faturamento_bruto,faturamento_liquido,pedidos_aprovados,pedidos_cancelados,pedidos_pendentes,ticket_medio,total_pedidos},sucesso} | 200 | {dados:{desconto_aplicavel,faturamento_bruto,faturamento_liquido,pedidos_aprovados,pedidos_cancelados,pedidos_pendentes,ticket_medio,total_pedidos},sucesso} | ✓ |
| 10 | GET | /health | 200 | {ambiente,counts:{pedidos,produtos,usuarios},database,db_path,debug,secret_key,status,versao} | 200 | {ambiente,counts:{pedidos,produtos,usuarios},database,status,versao} | declared |
| 11 | GET | / | 200 | {endpoints:{...},mensagem,versao} | 200 | {endpoints:{...},mensagem,versao} | ✓ |
| 12 | POST | /produtos | 201 | {dados:{id},mensagem,sucesso} | 201 | {dados:{id},mensagem,sucesso} | ✓ |
| 13 | POST | /usuarios | 201 | {dados:{id},sucesso} | 201 | {dados:{id},sucesso} | ✓ |
| 14 | POST | /pedidos | 201 | {dados:{pedido_id,total},mensagem,sucesso} | 201 | {dados:{pedido_id,total},mensagem,sucesso} | ✓ |
| 15 | PUT | /produtos/<id> | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 16 | PUT | /pedidos/<id>/status | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 17 | DELETE | /produtos/<id> | 200 | {mensagem,sucesso} | 200 | {mensagem,sucesso} | ✓ |
| 18 | POST | /admin/reset-db | 200 | {mensagem,sucesso} | 200 (com X-Admin-Token válido) | {mensagem,sucesso} | declared |
| 19 | POST | /admin/query | 200 | {dados:list<{"1":1}>,sucesso} | 200 (com X-Admin-Token válido) | {dados:list<{"1":1}>,sucesso} | declared |

## Declared contract changes
| Endpoint | Change | Finding fixed |
|---|---|---|
| GET /health | removidos os campos db_path, debug e secret_key da resposta | AP-09 |
| GET /usuarios | removido o campo senha de cada usuário da resposta | AP-09 |
| GET /usuarios/<id> | removido o campo senha da resposta | AP-09 |
| POST /admin/reset-db | agora exige o cabeçalho X-Admin-Token (ausente: 403; incorreto: 401) | AP-04 |
| POST /admin/query | agora exige o cabeçalho X-Admin-Token (ausente: 403; incorreto: 401) | AP-04 |

## Re-audit
Reviewer: subagent
Remaining anti-patterns: 2
- [MEDIUM] Scattered or Generic Error Handling (AP-13) — controllers/admin_controller.py:23-26, controllers/misc_controller.py:6-9, middlewares/error_handler.py:19-22
- [MEDIUM] Duplicated Code (AP-14) — models/usuario_model.py:6-7, models/usuario_model.py:32-39

## Diagnosis (FAILED only)
- Failed check: (c) Reauditoria oficial (validation-protocol.md §7.2.5.c / §8) — exige `Remaining anti-patterns: 0`; o subagente revisor devolveu 2.
- Error: [MEDIUM] AP-13 — `admin_controller.executar_query` (linha 23-26) e `misc_controller.health_check` (linha 6-9) usam `except Exception` amplo e repassam `str(exc)` ao cliente via `AppError`/`HealthCheckError`, renderizados por `middlewares/error_handler.py:19-22`. [MEDIUM] AP-14 — `usuario_model.get_by_email` (linha 32-39) reconstrói manualmente o dicionário da linha do usuário em vez de reaproveitar `_row_to_public_dict`/`_USUARIO_PUBLIC_FIELDS` (linha 6-7), duplicando 5 dos 6 campos já expressos no mapeador público.
- Origin: TP-06 (`references/refactoring-playbook.md` — "manter apenas capturas estreitas") para a regressão de AP-13; TP-16 (`references/refactoring-playbook.md` — "Extract Shared Helper") para o resíduo de AP-14.
- Skill gap: Para preservar o contrato exato de `/admin/query` (texto real do erro de SQL devolvido ao admin) e de `/health` (formato `{"status":"erro","detalhes":...}` do original), a refatoração usou `except Exception` amplo em vez de restringir à exceção específica esperada (ex.: `sqlite3.Error`) — o playbook (TP-06) não cobre explicitamente como estreitar a captura nesses dois casos sem perder a mensagem exigida pelo contrato original; isso deveria ser adicionado como um padrão explícito do TP-06. Para `usuario_model.get_by_email`, a skill deveria orientar explicitamente a estender o mapeador público com o campo sensível adicional em vez de duplicar a lista de campos.
