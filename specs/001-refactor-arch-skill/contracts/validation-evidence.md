# Contract: evidência de validação (`evidence/validation-project-N.md`)

Gravada ao fim da Fase 3, em sucesso **e** em falha; reexecução sobrescreve. `N` igual ao do
relatório.

~~~markdown
# Validation Evidence — <projeto>

| Item | Value |
|---|---|
| Result | CLEAN \| FAILED |
| Failure type | — \| skill \| external |
| Date | <AAAA-MM-DD HH:MM> |
| Skill version | <hash/commit> |
| Restore point | <commit curto> |
| Audit report | reports/audit-project-N.md |

## Environment
- Dependency environment: <caminho local, ex.: .venv/ ou node_modules/> (reused \| created)
- Setup steps: <passos executados, ex.: seed>
- Boot command: `<comando>`
- Port: <porta> (free before boot: yes)
- Runtime artifacts removed: <lista ou "none">
- Code fingerprint: <FP_START> at first boot / <FP_END> at end (unchanged: yes \| no)

## Boot
```text
<trecho relevante da saída de boot, ≤ 30 linhas>
```

## Behavior baseline
Source: captured \| inferred (<motivo>)

| # | Method | Path | Baseline status | Baseline shape | After status | After shape | Match |
|---|---|---|---|---|---|---|---|
| 1 | GET | /... | 200 | list<{id,name,...}> | 200 | list<{id,name,...}> | ✓ |
| … | | | | | | | ✓ \| ✗ \| declared |

## Declared contract changes
| Endpoint | Change | Finding fixed |
|---|---|---|
| … | … | AP-NN |

## Re-audit
Reviewer: subagent \| self
Remaining anti-patterns: 0 \| <lista de findings com localização>

## Diagnosis (FAILED only)
- Failed check: <...>
- Error: <...>
- Origin: <TP-NN / references/...>
- Probable skill gap: <...>
~~~

## Regras verificáveis

| Regra | Verificação |
|---|---|
| 100% dos endpoints do inventário na tabela | contagem de linhas = `Endpoints` da Fase 1 |
| `Result: CLEAN` ⇒ todas as linhas `✓` ou `declared`, reauditoria `0` | leitura |
| `declared` só com linha correspondente em "Declared contract changes" que enumere todas as chaves/status divergentes | leitura |
| `Result: CLEAN` ⇒ fingerprint inalterado entre o primeiro boot e o fim (validação de tentativa única) | leitura |
| `Result: FAILED` ⇒ seção Diagnosis preenchida | leitura |
