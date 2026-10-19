# Contract: saídas de console da skill

Banners e rótulos em inglês; conteúdo descritivo em português (research R13). Separador:
linha de 32 `=`.

## Fase 1

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem + versão se declarada>
Framework:     <framework + versão>
Dependencies:  <principais, separadas por vírgula>
Database:      <driver/ORM + tipo>
Domain:        <descrição curta>
Architecture:  <organização atual>
Source files:  <N> files analyzed
DB tables:     <entidades>
Endpoints:     <N> endpoints inventoried
Restore point: <ok | no-git | dirty (<k> pending files)>
================================
```

Campos não identificáveis: `not detected` (nunca chute).

## Fase 2

1. Relatório completo conforme [audit-report.md](./audit-report.md).
2. `Report saved to: <caminho absoluto ou relativo à raiz>`
3. Pergunta (última linha da fase):

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Se `restore point ≠ ok`, **no lugar** da pergunta:
`Phase 3 is blocked: <motivo>. Commit or discard pending changes, then re-run.` e a execução
termina sem perguntar (constituição VII).

Somente `y`/`yes`/`s`/`sim` (sem ambiguidade) libera a Fase 3; qualquer outra resposta:
`Phase 3 skipped. No project files were modified.`

## Fase 3 — sucesso

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios>

## Declared contract changes
<lista ou "none">

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly (<k>/<k> match baseline <captured|inferred>)
  ✓ Zero anti-patterns remaining
Evidence saved to: <caminho>
================================
```

## Fase 3 — falha

```text
================================
PHASE 3: REFACTORING FAILED
================================
Failure type: skill | external
## Failed checks
  ✗ <verificação>: <erro observado>
## Diagnosis
Origin:   <TP-NN / references/<arquivo>.md | environment>
Skill gap: <lacuna provável na skill | n/a (external): <orientação de correção, ex.: liberar a porta>>
Evidence saved to: <caminho>
================================
Revert project to the restore point? [y/n]
```

Após `y`: `Project reverted to restore point (<commit curto>). .claude/, reports/, evidence/ and
the dependency environment were preserved.` Após qualquer outra resposta: `Changes kept for
inspection. Revert before re-running the skill.`
