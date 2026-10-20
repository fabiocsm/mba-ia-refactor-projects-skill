# Validation Evidence — ecommerce-api-legacy

| Item | Value |
|---|---|
| Result | CLEAN |
| Failure type | — |
| Date | 2026-10-20 16:32 |
| Skill version | fd97f1e |
| Restore point | fd97f1e |
| Audit report | reports/audit-project-2.md |

## Environment
- Dependency environment: node_modules/ (reused)
- Setup steps: none (seed automático no boot)
- Boot command: `node src/app.js`
- Port: 3000 (free before boot: yes)
- Runtime artifacts removed: none
- Code fingerprint: 3333010777-1164 at first boot / 3333010777-1164 at end (unchanged: yes)

## Boot
```text
{"time":"2026-10-20T19:58:18.454Z","level":"info","message":"Frankenstein LMS rodando na porta 3000..."}
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
| GET /api/admin/financial-report | Agora exige o cabeçalho `X-Admin-Token` quando `ADMIN_TOKEN` está configurado no ambiente (401 se ausente/incorreto); sem `ADMIN_TOKEN` configurado, responde 403 (endpoint desabilitado); antes respondia 200 sem nenhuma autenticação | AP-04 |
| DELETE /api/users/:id | Em caso de erro real de banco ao excluir (não observado nesta validação — a exclusão sempre teve sucesso), agora responde 500 "Erro ao deletar usuário" em vez de sempre 200 ignorando o erro do callback | AP-13 |

## Re-audit
Reviewer: subagent
Remaining anti-patterns: 0
