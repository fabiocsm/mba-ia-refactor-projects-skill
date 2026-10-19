# Implementation Plan: Skill refactor-arch — Auditoria e Refatoração Arquitetural Automatizada

**Branch**: `dev` | **Date**: 2026-10-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-refactor-arch-skill/spec.md`

## Summary

Entregar a skill `refactor-arch` para Claude Code — `SKILL.md` de orquestração + 6 arquivos de
referência em Markdown + scripts POSIX genéricos — que, invocada com `/refactor-arch` dentro de um
projeto, executa 3 fases: (1) análise da stack e inventário de endpoints, (2) auditoria contra um
catálogo de anti-patterns com relatório gravado automaticamente em `reports/` e pausa para
confirmação, (3) refatoração para MVC com captura prévia da linha de base de comportamento,
validação (boot + comparação de endpoints + reauditoria zero) e evidência gravada em `evidence/`.
Falhas não são remendadas: a skill diagnostica e oferece reversão, e o autor itera
reverter → atualizar skill → reexecutar até obter execuções limpas nos 3 projetos. O repositório é
completado com Análise Manual, relatórios, evidências, código refatorado e README.

## Technical Context

**Language/Version**: Markdown (skill e referências); POSIX `sh` (scripts). Projetos-alvo: Python
3 / Flask 3.0–3.1 (projetos 1 e 3) e Node.js / Express 4.18 (projeto 2). Ambiente local: Python
3.14.5, Node v25.9.0, npm 11.16, git 2.52.

**Primary Dependencies**: Claude Code (Custom Skills: frontmatter, `$ARGUMENTS`,
`${CLAUDE_SKILL_DIR}`); `git`, `curl`, `find`, `grep`, `sed`, `awk`. Dependências dos alvos
instaladas só em ambiente isolado (`.venv/`, `node_modules/`).

**Storage**: arquivos Markdown — `reports/`, `evidence/`, `docs/iteration-log.md`, README. Alvos
usam SQLite (arquivo nos projetos 1 e 3, memória no projeto 2).

**Testing**: sem suíte de testes; verificação por gates — G2 estático (comandos de shell do
[quickstart](./quickstart.md)), testes de contrato dos scripts nos 3 projetos, execuções da skill
com checklist do enunciado e comparação contra a linha de base de comportamento.

**Target Platform**: Claude Code CLI em macOS/Linux; scripts POSIX.

**Project Type**: Agent Skill (prompt + base de conhecimento) com entregável documental.

**Performance Goals**: cada execução completa em uma sessão do Claude Code; `SKILL.md` < 500
linhas e referências carregadas por fase para economizar contexto.

**Constraints**: constituição v2.2.0 — nomes/caminhos fixos; Fases 1–2 somente-leitura (exceto
relatório); pausa obrigatória; agnosticismo; zero anti-patterns pós-refatoração; contrato de
endpoints preservado; ambiente isolado; execução limpa; nenhuma edição manual no código gerado.

**Scale/Scope**: 3 projetos, ~2,1 mil linhas de código-fonte; 19 / 3 / 22 endpoints; 4 / 3 / 15
arquivos-fonte; 2–4 iterações esperadas.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio / regra | Como o plano cumpre | Pré | Pós |
|---|---|---|---|
| I. Enunciado como fonte da verdade | Matriz de rastreabilidade abaixo; nomes/caminhos fixos; mínimos tratados como piso; sem escopo extra (sem suíte de testes, CI ou Docker) | ✅ | ✅ |
| II. Anatomia Anthropic | Frontmatter `name`/`description` ≤ 1024; corpo < 500 linhas; 6 referências a um nível com sumário; checklists e laços de feedback. Campos opcionais justificados: `argument-hint` (documenta `N`) e `disable-model-invocation: true` (skill com efeitos colaterais só por invocação explícita) — research R1 | ✅ | ✅ |
| III. 3 fases + gate humano | State machine em [data-model.md §9](./data-model.md); única escrita pré-confirmação é o relatório; pergunta exata em [console-output.md](./contracts/console-output.md) | ✅ | ✅ |
| IV. Agnosticismo e portabilidade | Heurísticas por stack; exemplos Python e Node; scripts sem valores de projeto; G2 busca identificadores dos alvos; G3 `diff -r`; cópia canônica em `code-smells-project/` | ✅ | ✅ |
| V. Base de conhecimento + regras de scripts | 5 áreas em 5 arquivos + protocolo de validação; 20 AP (AP-01–AP-20) e 18 TP (TP-01–TP-18) (R11, R12); scripts POSIX em `scripts/`, `${CLAUDE_SKILL_DIR}`, sem instalar pacotes, com fallback manual; Markdown só com comandos pontuais, sem scripts multi-linha | ✅ | ✅ |
| VI. Achados rastreáveis | Contrato do relatório com regras verificáveis; gravação automática e resolução de `N` (R6) | ✅ | ✅ |
| VII. Refatoração segura (NÃO NEGOCIÁVEL) | Ponto de restauração = `HEAD` na confirmação e bloqueio no lugar da pergunta sem ele (R7); reversão escopada; ambiente isolado (R8); linha de base de comportamento com verificação de porta livre e limpeza de artefatos de runtime após cada execução (R9); arquivos efêmeros só em temp do SO, removidos ao final; mudanças de segurança declaradas (R10); reauditoria zero; falha sem remendo; evidência em `evidence/` | ✅ | ✅ |
| Restrições do Entregável | Só Claude Code; skill nos 3 projetos e não na raiz; 3 relatórios + 3 evidências; README A–D; Spec Kit fora dos projetos; `.gitignore` respeitado | ✅ | ✅ |
| Fluxo e Quality Gates G1–G5 | Mapeados no [quickstart](./quickstart.md) §3–§7 e na ordem de tarefas | ✅ | ✅ |

**Resultado**: sem violações. Re-check pós-design: os artefatos da Fase 1 (data-model, contratos,
quickstart) não introduziram desvios.

## Project Structure

### Documentation (this feature)

```text
specs/001-refactor-arch-skill/
├── spec.md
├── plan.md              # este arquivo (inclui matriz de rastreabilidade)
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── skill-frontmatter.md
│   ├── console-output.md
│   ├── audit-report.md
│   ├── validation-evidence.md
│   └── scripts-cli.md
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (não criado aqui)
```

### Source Code (repository root)

```text
README.md                                  # Análise Manual, Construção da Skill, Resultados, Como Executar
docs/
└── iteration-log.md                       # registro de iterações (FR-046)
reports/
├── audit-project-1.md                     # gravado pela skill
├── audit-project-2.md
└── audit-project-3.md
evidence/
├── validation-project-1.md                # gravado pela skill
├── validation-project-2.md
└── validation-project-3.md

code-smells-project/                       # Projeto 1 — refatorado pela skill (estrutura final decidida na Fase 3)
└── .claude/skills/refactor-arch/          # CÓPIA CANÔNICA
    ├── SKILL.md
    ├── references/
    │   ├── project-analysis.md            # área 1
    │   ├── anti-patterns-catalog.md       # área 2
    │   ├── report-template.md             # área 3
    │   ├── mvc-guidelines.md              # área 4
    │   ├── refactoring-playbook.md        # área 5
    │   └── validation-protocol.md         # linha de base de comportamento, validação, evidência, reversão
    └── scripts/
        ├── count-source-files.sh
        ├── check-restore-point.sh
        ├── resolve-output-path.sh
        ├── workspace-artifacts.sh
        ├── check-port.sh
        ├── wait-for-http.sh
        ├── probe-endpoints.sh
        └── revert-project.sh
ecommerce-api-legacy/.claude/skills/refactor-arch/   # cópia idêntica
task-manager-api/.claude/skills/refactor-arch/       # cópia idêntica
```

**Structure Decision**: a skill é o "código-fonte" desta feature e vive na cópia canônica
`code-smells-project/.claude/skills/refactor-arch/`, sincronizada para os outros dois projetos.
O código dos projetos-alvo **não é editado à mão**: sua estrutura final é saída da Fase 3. Os
artefatos de entrega ficam na raiz (`reports/`, `evidence/`, `docs/`, `README.md`).

## Sequência de implementação (insumo para /speckit-tasks)

1. **Pré-voo do ambiente** (quickstart §2) — elimina riscos R8 antes de qualquer execução.
2. **Análise Manual** dos 3 projetos → README seção A (Gate G1). Insumo para o catálogo.
3. **Skill**: `SKILL.md` + 6 referências + 8 scripts e seus testes de contrato (Gate G2).
4. **Sincronização** das cópias (Gate G3).
5. **Execuções** 1 → 2 → 3 com o ciclo de iteração até execução limpa em cada projeto (Gate G4);
   commits por projeto (código refatorado + relatório + evidência).
6. **Documentação final**: README B, C, D; `docs/iteration-log.md`; verificação final (Gate G5).

## Matriz de rastreabilidade (enunciado → artefato → verificação)

| # | Requisito do enunciado | Artefato | Verificação |
|---|---|---|---|
| 1 | Analisar codebase: linguagem, framework, arquitetura | `references/project-analysis.md`; Fase 1 do `SKILL.md` | Banner da Fase 1 (SC-001) |
| 2 | Identificar anti-patterns com severidade, arquivo e linha | `anti-patterns-catalog.md`; Fase 2 | Regras do [audit-report](./contracts/audit-report.md) (SC-003) |
| 3 | Relatório de auditoria estruturado | `report-template.md`; `reports/` | Contrato do relatório |
| 4 | Refatorar para MVC | `mvc-guidelines.md`, `refactoring-playbook.md`; Fase 3 | Checklist Fase 3 (SC-010) |
| 5 | Validar que a aplicação continua funcionando | `validation-protocol.md`; `evidence/` | Evidência `CLEAN` (SC-006, SC-008) |
| 6 | Agnóstica de tecnologia | Heurísticas e exemplos multi-stack; scripts genéricos | G2 (0 identificadores), execução nos 3 projetos (SC-011) |
| 7 | Escala de severidades CRITICAL/HIGH/MEDIUM/LOW | Catálogo (seção de escala) | G2 |
| 8 | Ferramenta Claude Code + Custom Skills | `.claude/skills/refactor-arch/` | Invocação `/refactor-arch` |
| 9 | Referências em Markdown | `references/*.md` | G2 |
| 10 | Análise manual: ≥ 5 problemas/projeto (≥1 CRIT/HIGH, ≥2 MED, ≥2 LOW) no README | README seção A | G1 |
| 11 | Skill criada em `code-smells-project/`; SKILL.md com 3 fases | Cópia canônica | G2 |
| 12 | 5 áreas de conhecimento | 5 arquivos de referência | G2 (títulos) |
| 13 | Nome `refactor-arch` e `SKILL.md` inalterados | Frontmatter/diretório | [skill-frontmatter](./contracts/skill-frontmatter.md) |
| 14 | Catálogo ≥ 8 anti-patterns, severidades distribuídas | Catálogo | G2 (SC-012) |
| 15 | Detecção de APIs deprecated com equivalente moderno | Catálogo (AP deprecated) + relatório | G2; relatório |
| 16 | Playbook ≥ 8 transformações com antes/depois | Playbook | G2 (SC-012) |
| 17 | Fase 2 pausa antes de modificar arquivos | `SKILL.md` Fase 2 | `git status` vazio na pergunta (SC-005) |
| 18 | Fase 3 valida boot + endpoints | `validation-protocol.md` | Evidência (SC-006) |
| 19 | Projeto 1: stack, ≥ 5 dos problemas manuais, MVC, boot, endpoints, relatório, commit | Execução 1 | Quickstart §5 (SC-004) |
| 20 | Projeto 2: cópia da skill, 3 fases, relatório, commit | Execução 2 | G3 + quickstart §5 |
| 21 | Projeto 3: Python/Flask + domínio Task Manager, problemas em projeto organizado, sem quebrar | Execução 3 | Quickstart §5 |
| 22 | Checklist de validação (Fases 1/2/3) por projeto | README seção C | SC-010 |
| 23 | Iterar ajustando referências | Ciclo de iteração; `docs/iteration-log.md` | SC-009 |
| 24 | Skill em `.claude/skills/refactor-arch/` nos 3 projetos | 3 cópias | G3 |
| 25 | Código refatorado commitado | Commits por projeto | G5 |
| 26 | 3 relatórios em `reports/` | `reports/audit-project-{1,2,3}.md` | G5 |
| 27 | README B: decisões, anti-patterns e por quê, agnosticismo, desafios | README seção B | G5 |
| 28 | README C: findings por severidade, antes/depois, checklist, logs/screenshots, observações | README seção C + `evidence/` | G5 |
| 29 | README D: pré-requisitos, comandos, como validar | README seção D | SC-014 |
| 30 | Critérios de aceite 3/3 (stack, ≥ 5 findings, ≥ 1 CRIT/HIGH, app funciona) | Execuções limpas | G5 |
| 31 | Repositório público (fork) | GitHub `origin` | Ação do autor |

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| `sqlite3` nativo sem binário para Node 25 | Pré-voo; se falhar, ajustar ambiente (toolchain ou versão de Node) — falha externa |
| Dependências fixadas antigas em Python 3.14 | Pré-voo; tratar como falha externa |
| Reauditoria zero difícil com LOWs numerosos (magic numbers, prints) | Playbook com transformações explícitas para cada LOW; sinais com notas de falso positivo |
| Endpoints administrativos perigosos (SQL arbitrário, reset) | Política R10: manter rota, neutralizar, declarar |
| Linha de base de comportamento contaminada por estado de execuções anteriores | `workspace-artifacts.sh` + setup documentado antes de cada execução |
| Porta 5000 ocupada no macOS pelo Receptor AirPlay (verificado: `ControlCenter` escuta `*:5000` e responde `403 AirTunes`) — projetos 1 e 3 fixam a porta 5000 no código | Autor desativa o Receptor AirPlay (Ajustes do Sistema → Geral → AirDrop e Handoff) antes do pré-voo; a skill verifica a porta com `check-port.sh` antes de cada boot e trata porta ocupada como falha externa; `wait-for-http.sh` exige que o processo iniciado continue vivo, evitando aceitar a resposta de outro processo |
| Skill não aparece no menu se o Claude for iniciado na raiz | Quickstart e README instruem `cd <projeto>` (R2) |

## Complexity Tracking

Sem violações da constituição a justificar.
