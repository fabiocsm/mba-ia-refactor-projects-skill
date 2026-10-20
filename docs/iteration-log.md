# Iteration Log — refactor-arch

Registro de cada execução não limpa da skill `refactor-arch` (ou reexecução após falha) e de
falhas externas ao ambiente. Cada entrada segue o ciclo obrigatório da constituição:
**reverter → atualizar a skill (cópia canônica) → reexecutar**.

Regras:

- `skill_version_before` e `skill_version_after` são commits que alteraram
  `code-smells-project/.claude/skills/refactor-arch/` e DEVEM diferir, exceto quando
  `external_failure = true` (porta ocupada, runtime ausente, rede).
- `skill_change` descreve o(s) arquivo(s) da skill alterados e o resumo da mudança genérica.
- Testes controlados (ex.: teste do fluxo de falha) ficam na seção "Testes controlados" e não
  contam como iteração.

## Iterações

| date | project | run_result | skill_version_before | skill_version_after | error | root_cause | skill_change | external_failure |
|---|---|---|---|---|---|---|---|---|
| 2026-10-19 | code-smells-project | phases 1-2 only (answered `n`) — report format deviations | 4ce2631 | 0b26251 | `File:` omitted the filename after the first location; `Deprecated APIs: none detected` placed between MEDIUM and LOW; architecture classified as "Camadas parciais" for a monolith | template allowed ambiguous location shorthand and did not pin the position of the deprecated line; classification table keyed on file names | `references/report-template.md` (location format + position rule + self-check), `references/project-analysis.md` (classification by responsibilities) | false |
| 2026-10-19 | code-smells-project | phases 1-2 only (blocked-gate test, pending file) — block message correct; printed report ≠ saved file | 0b26251 | 69d70d0 | console report omitted the 4 LOW findings that the saved file contained; deprecated line still after MEDIUM | report was written first and re-printed from memory; the deprecated line read as the end of the report | `SKILL.md` Phase 2 (save, re-read the file and print it in full, check count = Total); `references/report-template.md` (deprecated line takes the AP-15 slot); contract updated | false |
| 2026-10-19 | code-smells-project | FAILED (rejected on review: agent reported CLEAN after patching during validation); reverted with `revert-project.sh` | 69d70d0 | 9c2007b | post-boot re-audit found a remaining AP-14 (duplicated required-field block in the new validators) and `/health` dropped `ambiente` (undeclared) and `db_path` (not listed in the declared change); the agent edited `utils/validators.py` and `controllers/health_controller.py` after the first boot and re-validated | no mandatory full self-review before the first boot; no mechanical proof that code did not change during validation; rule allowed the interpretation that validation could be restarted | `SKILL.md` (rule 5 + checklist + Phase 3 steps 3-4), `references/validation-protocol.md` §7.1 self-review / §7.2 single attempt + fingerprint + declared-change completeness, `scripts/workspace-artifacts.sh fingerprint`; contracts updated | false |
| 2026-10-19 | code-smells-project | FAILED (rejected on review: reported CLEAN, but baseline was captured after refactoring); reverted with `revert-project.sh` | 9c2007b | 6ea3da5 | agent refactored before capturing the behavior baseline, then used `git stash` to run the original; official re-audit replaced by the pre-boot self-review | SKILL.md let all phase 3 references be read up front and the ordering was easy to skip; no ban on git state changes; re-audit could be satisfied by the self-review | `SKILL.md` (order gate with `Behavior baseline captured` milestone, rule 7 on git state, checklist), `references/validation-protocol.md` §5 and §8 | false |
| 2026-10-19 | code-smells-project | in progress — order now correct (baseline before any edit); run stopped on its own after self-review and before validation (session dd77a9eb-dcb0-4175-8987-fdedd98db5bc) | 6ea3da5 | — | no protocol violation so far; agent paused asking to 'continue' | possibly turn/output budget of the non-interactive run | none yet | false |

## Testes controlados

| date | project | test | result | notes |
|---|---|---|---|---|
