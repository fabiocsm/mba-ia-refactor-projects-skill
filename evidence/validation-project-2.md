# Validation Evidence — ecommerce-api-legacy

| Item | Value |
|---|---|
| Result | CLEAN |
| Failure type | — |
| Date | 2026-10-23 05:14 |
| Skill version | b106f86 |
| Restore point | 913dfc6 |
| Audit report | reports/audit-project-2.md |

## Environment
- Dependency environment: node_modules/ (reused)
- Setup steps: none (seeds carregam automaticamente no boot)
- Boot command: `npm start`
- Port: 3000 (free before boot: yes)
- Runtime artifacts removed: none (banco SQLite em memória)
- Code fingerprint: 1245065678-1136 at first boot / 1245065678-1136 at end (unchanged: yes)

## Boot
```text
> desafio-arquitetura-ia-boilerplate@1.0.0 start
> node src/app.js

{"time":"2026-10-23T08:14:10.035Z","level":"info","message":"Frankenstein LMS rodando na porta 3000..."}
{"time":"2026-10-23T08:14:21.732Z","level":"info","message":"Processando pagamento","gatewayConfigured":false}
{"time":"2026-10-23T08:14:21.764Z","level":"info","message":"Processando pagamento","gatewayConfigured":false}
```

## Behavior baseline
Source: captured

| # | Method | Path | Baseline status | Baseline shape | After status | After shape | Match |
|---|---|---|---|---|---|---|---|
| 1 | POST | /api/checkout | 200, 400 | {enrollment_id,msg} / text | 200, 400 | {enrollment_id,msg} / text | ✓ |
| 2 | DELETE | /api/users/:id | 200 | text | 200 | text | ✓ |
| 3 | GET | /api/admin/financial-report | 200 | list<{course,revenue,students:list<{paid,student}>}> | 200 | list<{course,revenue,students:list<{paid,student}>}> | declared |

## Declared contract changes
| Endpoint | Change | Finding fixed |
|---|---|---|
| GET /api/admin/financial-report | Agora exige o header `X-Admin-Token` (variável de ambiente `ADMIN_TOKEN`); sem a variável configurada responde 403 "Admin endpoint disabled"; com token incorreto responde 401 "Unauthorized". | AP-04 |
| POST /api/checkout | O log do processamento de pagamento deixou de incluir o número do cartão e a chave do gateway de pagamento. | AP-09 |
| POST /api/checkout | Ao cadastrar um usuário novo (e-mail ainda não existente), a senha (`pwd`) passou a ser obrigatória; sem ela, responde 400 "Senha obrigatória para novo usuário" em vez de aplicar a senha padrão "123456". | AP-05 |
| POST /api/checkout | Erro de banco real ao buscar o curso agora responde 500 "Erro DB" em vez de 404 "Curso não encontrado" (cenário não observável nos testes, pois não há erro de banco real nas execuções). | AP-13 |

## Re-audit
Reviewer: subagent
Remaining anti-patterns: 0
