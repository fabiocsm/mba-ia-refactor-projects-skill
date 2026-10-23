# Data Model: Skill refactor-arch

**Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

A "dados" desta feature são documentos Markdown (skill, relatórios, evidências, registros) e
estruturas que o agente mantém durante uma execução. Formatos exatos de saída estão em
[contracts/](./contracts/).

---

## 1. Skill (pacote)

| Campo | Regra |
|---|---|
| `dir` | `.claude/skills/refactor-arch/` dentro de cada projeto-alvo |
| `SKILL.md` | frontmatter ([contracts/skill-frontmatter.md](./contracts/skill-frontmatter.md)) + corpo < 500 linhas |
| `references/*.md` | 6 arquivos (research R3); todos citados diretamente no `SKILL.md` |
| `scripts/*.sh` | opcionais, POSIX `sh` ([contracts/scripts-cli.md](./contracts/scripts-cli.md)) |
| `version` | hash do conteúdo da pasta / commit que a alterou por último |

**Validações**: cópias nos 3 projetos idênticas (`diff -r` vazio); zero identificadores
específicos dos projetos-alvo; nenhum bloco de script multi-linha no Markdown (comandos únicos
citados em procedimentos manuais são permitidos); arquivos > 100 linhas com sumário.

## 2. Anti-pattern (entrada do catálogo)

| Campo | Tipo / regra |
|---|---|
| `id` | `AP-NN`, estável, único |
| `name` | nome canônico (usado no título do finding) |
| `severity` | `CRITICAL` \| `HIGH` \| `MEDIUM` \| `LOW` (escala do enunciado) |
| `category` | segurança, arquitetura, SOLID, performance, qualidade, deprecated |
| `detection_signals` | lista de sinais concretos e verificáveis, com exemplos por stack |
| `false_positive_notes` | quando o sinal **não** caracteriza o problema |
| `impact` | consequência para manutenção/segurança/testes |
| `transformations` | ≥ 1 `TP-NN` do playbook |
| `deprecated_mapping` | (só para API deprecated) API obsoleta → equivalente moderno, por stack |

**Validações**: ≥ 8 entradas; ≥ 1 por severidade; ≥ 1 de API deprecated; todo `transformations`
aponta para um `TP` existente.

## 3. Padrão de transformação (entrada do playbook)

| Campo | Regra |
|---|---|
| `id` | `TP-NN`, estável, único |
| `resolves` | lista de `AP-NN` |
| `steps` | passos aplicáveis em qualquer stack |
| `before` / `after` | exemplos de código (≥ 1 par; preferencialmente Python e Node) |
| `layer_target` | camada MVC de destino (config, model, view/route, controller, middleware, entry point) |
| `contract_risk` | se pode alterar o contrato de um endpoint (então exige declaração) |

**Validações**: ≥ 8 entradas, 100% com antes/depois.

## 4. Projeto-alvo e resumo da Fase 1

| Campo | Regra |
|---|---|
| `project_name` | nome do diretório do projeto |
| `language`, `framework` (+versão), `dependencies` | detectados por heurística (manifesto, imports) |
| `database` | driver/ORM e tipo (arquivo, memória) |
| `domain` | descrição curta derivada de entidades e rotas |
| `architecture` | descrição da organização atual (monolito, camadas parciais…) |
| `source_files` | lista e contagem (research R5) |
| `loc` | linhas totais dos arquivos-fonte |
| `data_entities` | tabelas/modelos detectados |
| `endpoints` | lista de **Endpoint inventariado** |
| `run_steps` | passos documentados de setup e boot (README, scripts do manifesto) |
| `restore_point` | `ok` \| `no-git` \| `dirty` (+ arquivos pendentes) |

## 5. Endpoint inventariado

| Campo | Regra |
|---|---|
| `method`, `path` | ex.: `GET /items/<id>` |
| `source` | `arquivo:linha` da declaração |
| `params` | path/query/body esperados |
| `side_effect` | `read` \| `create` \| `update` \| `delete` \| `admin` (define a ordem de execução) |

## 6. Finding

| Campo | Regra |
|---|---|
| `severity`, `anti_pattern_id`, `title` | do catálogo |
| `locations` | 1..n `arquivo:linha` ou `arquivo:início-fim`, existentes no código auditado |
| `description`, `impact`, `recommendation` | português; recomendação cita `TP-NN` |
| `deprecated_replacement` | obrigatório se o anti-pattern for de API deprecated |

**Regras**: ordenação CRITICAL → LOW; uma ocorrência conta uma vez; sem evidência, sem finding.

## 7. Relatório de auditoria

Cabeçalho (`Project`, `Stack`, `Files`, `~LOC`), `Summary` por severidade, `Findings`, `Total`.
Arquivo: `<raiz>/reports/audit-project-N.md`. Formato: [contracts/audit-report.md](./contracts/audit-report.md).

## 8. Linha de base de comportamento

| Campo | Regra |
|---|---|
| `source` | `captured` (original executado) \| `inferred` (original não iniciou) |
| `requests` | plano de requisições ordenado (arquivo temporário fora do repo) |
| `responses[]` | por requisição: `status`, `body_type`, `shape` (chaves recursivas) |
| `port` | porta usada; verificada livre antes do boot (`check-port.sh`) |
| `runtime_artifacts` | arquivos novos gerados pela execução, removidos logo após ela |

## 9. Execução (state machine)

```text
STARTED → PHASE1_DONE → PHASE2_DONE (relatório gravado)
PHASE2_DONE --(restore_point≠ok; mensagem de bloqueio, sem pergunta)--> BLOCKED_NO_RESTORE_POINT
PHASE2_DONE --(restore_point=ok)--> AWAITING_CONFIRMATION
AWAITING_CONFIRMATION --(não/ambíguo)--> ENDED_NO_CHANGES
AWAITING_CONFIRMATION --(sim)--> BASELINE_CAPTURED → REFACTORED → VALIDATING
BASELINE_CAPTURED/VALIDATING --(porta ocupada sem alternativa não invasiva)--> FAILED (external)
VALIDATING --(boot ok ∧ endpoints = baseline ∧ reauditoria = 0)--> CLEAN (evidência gravada)
REFACTORED/VALIDATING --(qualquer erro)--> FAILED (evidência gravada) → REVERTED | KEPT_FOR_INSPECTION
```

| Campo | Regra |
|---|---|
| `project`, `N`, `skill_version` | identificação |
| `result` | `CLEAN` \| `FAILED` \| `ENDED_NO_CHANGES` \| `BLOCKED_NO_RESTORE_POINT` |
| `checks` | boot, endpoints (por endpoint), reauditoria (lista de findings remanescentes) |
| `declared_contract_changes` | lista (research R10) |
| `failure_type` | se `FAILED`: `skill` \| `external` (ex.: porta ocupada, runtime ausente) |
| `diagnosis` | se `FAILED`: erro, `TP`/arquivo de referência de origem, lacuna provável |
| `temp_dir` | diretório temporário do SO com os arquivos de trabalho; removido ao final |

**Regras**: só `CLEAN` é aceito para commit; `FAILED` nunca é "remendado" na mesma execução.

## 10. Evidência de validação

Arquivo `<raiz>/evidence/validation-project-N.md`, gravado em `CLEAN` e `FAILED`.
Formato: [contracts/validation-evidence.md](./contracts/validation-evidence.md).

## 11. Registro de iteração

Arquivo `docs/iteration-log.md` (uma entrada por execução não limpa ou reexecução):

| Campo | Regra |
|---|---|
| `date`, `project`, `run_result` | |
| `skill_version_before` / `skill_version_after` | DEVEM diferir, salvo `external_failure = true` |
| `error`, `root_cause` | do diagnóstico |
| `skill_change` | arquivo(s) e resumo da alteração genérica |
| `external_failure` | `true` apenas para causa fora da skill (porta, runtime, rede) |

## 12. Problema da Análise Manual

Entrada no README (seção A): `project`, `severity`, `title`, `location`, `justification`,
`matched_by` (id do finding correspondente no relatório, preenchido após a execução — base de
SC-004).
