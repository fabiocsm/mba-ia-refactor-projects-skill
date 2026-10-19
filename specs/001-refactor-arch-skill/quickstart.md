# Quickstart: validar a skill refactor-arch

Guia de validação ponta a ponta. Formatos de saída: [contracts/](./contracts/). Entidades e
estados: [data-model.md](./data-model.md).

## 1. Pré-requisitos

- Claude Code instalado e autenticado.
- `git`, `curl`, `python3` (com `venv`), `node` + `npm` no PATH.
- Cada projeto na linha de base do código: `git diff --quiet 6d1ce62 -- <projeto>
  ':(exclude)<projeto>/.claude'` retorna 0 e `git status --porcelain -- <projeto>` está vazio.
- macOS: Receptor AirPlay desativado (Ajustes do Sistema → Geral → AirDrop e Handoff), pois ele
  ocupa a porta 5000 usada pelos projetos 1 e 3. Conferir com `lsof -nP -iTCP:5000 -sTCP:LISTEN`
  (sem saída = livre).

## 2. Pré-voo do ambiente (uma vez, antes da primeira execução)

Prova que os originais sobem no ambiente local (riscos do research R8). Executar em cada projeto,
no ambiente isolado, e depois remover os artefatos de runtime gerados:

```bash
cd code-smells-project && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
cd task-manager-api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
cd ecommerce-api-legacy && npm install
```

Esperado: instalações sem erro; cada app responde em `/` ou em um endpoint de leitura conforme o
README do projeto. Falha aqui é **externa à skill** — corrigir o ambiente antes de seguir.

## 3. Gate G2 — verificação estática da skill (cópia canônica)

Executar a partir de `code-smells-project/.claude/skills/refactor-arch/`:

| Verificação | Esperado |
|---|---|
| Linhas do corpo do `SKILL.md` (após o frontmatter) | < 500 |
| Tamanho da `description` | ≤ 1024 caracteres |
| `name` | `refactor-arch` |
| Arquivos em `references/` | 6, cada área obrigatória com título identificável |
| Arquivos > 100 linhas | começam com sumário |
| Entradas `AP-` no catálogo | ≥ 8, com CRITICAL, HIGH, MEDIUM e LOW, ≥ 1 de API deprecated |
| Entradas `TP-` no playbook | ≥ 8, cada uma com bloco "antes" e "depois" |
| Todo `AP` aponta para `TP` existente | 100% |
| Identificadores dos projetos-alvo nas regras | 0 ocorrências (busca por nomes de arquivos, rotas e tabelas dos 3 projetos) |
| Blocos de script multi-linha em `SKILL.md`/`references/` | 0 (exceto antes/depois do playbook) |
| Scripts | 8 em `scripts/` (incluindo `check-port.sh`), todos citados no `SKILL.md` com procedimento manual; testes de contrato ([scripts-cli.md](./contracts/scripts-cli.md)) passando nos 3 projetos |

## 4. Gate G3 — sincronização

```bash
diff -r code-smells-project/.claude/skills/refactor-arch ecommerce-api-legacy/.claude/skills/refactor-arch
```

```bash
diff -r code-smells-project/.claude/skills/refactor-arch task-manager-api/.claude/skills/refactor-arch
```

Esperado: nenhuma saída.

## 5. Execução por projeto (Gate G4)

Ordem 1 → 2 → 3 (garante `audit-project-1/2/3` sem argumento):

```bash
cd code-smells-project && claude "/refactor-arch"
```

```bash
cd ecommerce-api-legacy && claude "/refactor-arch"
```

```bash
cd task-manager-api && claude "/refactor-arch"
```

Verificar em cada execução:

| Momento | Verificação | Critério |
|---|---|---|
| Fim da Fase 1 | banner com linguagem, framework, domínio; `Source files` = 4 / 3 / 15 | SC-001 |
| Fim da Fase 2 | relatório conforme [audit-report.md](./contracts/audit-report.md); ≥ 5 findings; ≥ 1 CRITICAL/HIGH | SC-002, SC-003 |
| Fim da Fase 2 | `reports/audit-project-N.md` existe e é idêntico ao impresso | SC-005 |
| Na pergunta | `git status --porcelain -- <projeto>` vazio | SC-005 |
| Após responder `n` (teste negativo, opcional) | nada alterado no projeto | US1 cenário 5 |
| Fim da Fase 3 | `PHASE 3: REFACTORING COMPLETE`; evidência `Result: CLEAN`; 100% `✓`/`declared`; reauditoria 0 | SC-006, SC-008 |
| Após a Fase 3 | estrutura MVC (config, models, views/routes, controllers, error handler, entry point) | SC-010 |
| Cobertura | ≥ 5 problemas da Análise Manual casam com findings (`matched_by`) | SC-004 |

Execução limpa → commit do projeto refatorado, do relatório e da evidência.

## 6. Execução com falha — ciclo de iteração

1. Ler o diagnóstico (`PHASE 3: REFACTORING FAILED` + evidência).
2. Responder `y` para reverter. Confirmar: `git status --porcelain -- <projeto>` vazio e
   `.claude/` intacto.
3. Registrar a entrada em `docs/iteration-log.md` (erro, causa, versão da skill).
4. Corrigir a skill **na cópia canônica**, de forma genérica; commitar
   (`feat(skill): …`/`fix(skill): …`).
5. Repetir os Gates G2 e G3.
6. Reexecutar a partir da linha de base do código em todos os projetos afetados. Proibido reexecutar com a
   skill inalterada, exceto falha externa registrada.

## 7. Verificação final de entrega (Gate G5)

| Item | Esperado |
|---|---|
| `reports/` | exatamente `audit-project-1.md`, `audit-project-2.md`, `audit-project-3.md` |
| `evidence/` | exatamente `validation-project-1.md`, `-2.md`, `-3.md`, todos `Result: CLEAN` |
| README | seções Análise Manual, Construção da Skill (com histórico de iterações), Resultados (checklist preenchido ×3, links para `evidence/`), Como Executar |
| Matriz de rastreabilidade ([plan.md](./plan.md)) | 100% dos requisitos com artefato e verificação |
| Repositório | sem `.venv/`, `node_modules/`, `*.db`, `.env` commitados; fork público |
