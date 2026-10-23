---

description: "Lista de tarefas para implementar a skill refactor-arch"
---

# Tasks: Skill refactor-arch — Auditoria e Refatoração Arquitetural Automatizada

**Input**: Design documents from `specs/001-refactor-arch-skill/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: não há suíte de testes automatizados (fora de escopo na spec). As verificações são os
gates da constituição (G1–G5), os testes de contrato dos scripts exigidos pelo Gate G2 e as
execuções da skill com o checklist do enunciado.

**Organization**: tarefas agrupadas por user story (spec.md) para implementação e validação
independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: user story atendida (US1–US4)

## Path Conventions

- Cópia canônica da skill: `code-smells-project/.claude/skills/refactor-arch/`
- Entregáveis na raiz: `README.md`, `reports/`, `evidence/`, `docs/iteration-log.md`
- Projetos-alvo: `code-smells-project/`, `ecommerce-api-legacy/`, `task-manager-api/` — seu
  código **nunca** é editado à mão; só muda por execução da skill.

## Regras globais para todas as tarefas da skill

- Exemplos de código nos arquivos da skill usam um domínio **neutro** (ex.: biblioteca com
  `books`, `members`, `loans`) e NUNCA nomes de arquivos, rotas, tabelas ou domínios dos 3
  projetos-alvo (ex.: proibido citar `produtos`, `usuarios`, `pedidos`, `AppManager`, `checkout`,
  `models.py` como regra).
- Arquivos com mais de 100 linhas começam com sumário (table of contents).
- Terminologia fixa: "finding", "anti-pattern", "severidade", "camada", "linha de base de
  comportamento", "ponto de restauração", "execução limpa".
- Nenhum bloco de script multi-linha em `SKILL.md` ou `references/` (exceção: antes/depois do
  playbook e trechos ilustrativos de detecção); comandos pontuais em procedimentos manuais são
  permitidos.
- Scripts: `#!/bin/sh` POSIX, cabeçalho de uso/dependências/exit codes, saída `KEY=VALUE`, exit
  codes `0/1/2/3`, sem instalar pacotes, sem valores de projeto embutidos
  ([contracts/scripts-cli.md](./contracts/scripts-cli.md)); `chmod +x`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: estrutura de diretórios e ambiente local pronto para executar os projetos

- [X] T001 Criar a estrutura da skill canônica `code-smells-project/.claude/skills/refactor-arch/` com subpastas `references/` e `scripts/` (vazias) conforme plan.md "Project Structure"
- [X] T002 [P] Criar `docs/iteration-log.md` com título, explicação de uso e tabela vazia com as colunas do data-model §11: `date | project | run_result | skill_version_before | skill_version_after | error | root_cause | skill_change | external_failure`
- [X] T003 [P] Pré-voo do projeto 1 (quickstart §2): antes de subir, confirmar porta 5000 livre com `lsof -nP -iTCP:5000 -sTCP:LISTEN` (no macOS, se aparecer `ControlCenter`, o autor desativa o Receptor AirPlay em Ajustes do Sistema → Geral → AirDrop e Handoff e registra a falha externa em `docs/iteration-log.md`); em `code-smells-project/`, `python3 -m venv .venv`, `.venv/bin/pip install -r requirements.txt`, subir `.venv/bin/python app.py`, confirmar resposta HTTP em `http://localhost:5000/health`, parar o processo e remover o banco gerado (`loja.db`); confirmar com `git status --porcelain -- code-smells-project` vazio e `git check-ignore -q code-smells-project/.venv`
- [X] T004 [P] Pré-voo do projeto 2: em `ecommerce-api-legacy/`, `npm install`, subir `npm start`, confirmar resposta em `GET http://localhost:3000/api/admin/financial-report`, parar o processo; se `sqlite3` falhar ao compilar/carregar no Node v25, registrar como falha externa em `docs/iteration-log.md` e corrigir o ambiente (toolchain ou versão LTS do Node) antes de seguir; confirmar `git status --porcelain -- ecommerce-api-legacy` vazio
- [X] T005 [P] Pré-voo do projeto 3: confirmar porta 5000 livre (mesma verificação de T003); em `task-manager-api/`, `python3 -m venv .venv`, `.venv/bin/pip install -r requirements.txt`, `.venv/bin/python seed.py`, subir `.venv/bin/python app.py`, confirmar `GET http://localhost:5000/health`, parar o processo e remover `tasks.db`/`instance/` gerados; confirmar `git status --porcelain -- task-manager-api` vazio

**Checkpoint**: os 3 originais sobem localmente em ambientes isolados (riscos do research R8 eliminados)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Análise Manual (Gate G1, insumo do catálogo e da cobertura SC-004) e esqueleto do `SKILL.md`

**⚠️ CRITICAL**: nenhuma user story começa antes desta fase

- [X] T006 Análise manual de `code-smells-project/` (ler `app.py`, `controllers.py`, `models.py`, `database.py`): adicionar ao `README.md` uma seção `## Análise Manual` com subseção `### Projeto 1 — code-smells-project (Python/Flask)` contendo tabela `# | Severidade | Problema | Arquivo:linha | Justificativa | Finding da skill (matched_by)` com ≥ 5 problemas (recomendado 7–10 para dar folga ao critério "≥ 5 dos problemas documentados" de SC-004), incluindo ≥ 1 CRITICAL ou HIGH, ≥ 2 MEDIUM e ≥ 2 LOW (coluna `matched_by` vazia por enquanto); preservar o conteúdo original do enunciado no README
- [X] T007 Análise manual de `ecommerce-api-legacy/` (`src/app.js`, `src/AppManager.js`, `src/utils.js`, `api.http`): adicionar `### Projeto 2 — ecommerce-api-legacy (Node.js/Express)` na seção `## Análise Manual` do `README.md`, mesma tabela e mesmos mínimos de T006
- [X] T008 Análise manual de `task-manager-api/` (`app.py`, `database.py`, `seed.py`, `models/`, `routes/`, `services/`, `utils/`): adicionar `### Projeto 3 — task-manager-api (Python/Flask)` na seção `## Análise Manual` do `README.md`, mesma tabela e mínimos, incluindo ao menos um problema arquitetural apesar da separação de camadas existente
- [X] T009 Gate G1: verificar no `README.md` que cada um dos 3 projetos tem ≥ 5 problemas com a distribuição mínima de severidades, `arquivo:linha` existente (conferir com `sed -n '<linha>p' <arquivo>`) e justificativa; commitar `docs: add manual analysis of the 3 target projects`
- [X] T010 Criar `code-smells-project/.claude/skills/refactor-arch/SKILL.md` com o frontmatter exato de [contracts/skill-frontmatter.md](./contracts/skill-frontmatter.md) (`name: refactor-arch`; `description` em terceira pessoa, caso de uso primeiro, ≤ 1024 caracteres, com termos auditoria arquitetural, anti-patterns, code smells, severidade, refatoração MVC, validação; `argument-hint: "[report-number]"`; `disable-model-invocation: true`) e o esqueleto do corpo: objetivo; regras não negociáveis (Fases 1–2 somente-leitura exceto o relatório; pausa obrigatória; falha na Fase 3 não é remendada; nunca alterar `.claude/` nem `reports/` na Fase 3); checklist de progresso copiável das 3 fases; seções vazias `## Phase 1`, `## Phase 2`, `## Phase 3`; índice das 6 referências com "quando ler"; tabela de scripts `${CLAUDE_SKILL_DIR}/scripts/<nome>.sh` com coluna "procedimento manual equivalente"; regra de idioma (banners em inglês, conteúdo em português)

**Checkpoint**: Gate G1 aprovado e esqueleto da skill pronto

---

## Phase 3: User Story 1 - Auditar um projeto legado sem alterá-lo (Priority: P1) 🎯 MVP

**Goal**: `/refactor-arch` executa as Fases 1 e 2, grava `reports/audit-project-N.md` automaticamente e pausa sem alterar o projeto

**Independent Test**: em `code-smells-project/`, executar `claude "/refactor-arch"`, responder `n`; verificar banner da Fase 1 (Source files = 4), relatório conforme [audit-report.md](./contracts/audit-report.md) com ≥ 5 findings e ≥ 1 CRITICAL/HIGH, `reports/audit-project-1.md` idêntico ao impresso e `git status --porcelain -- code-smells-project` vazio

### Implementation for User Story 1

- [X] T011 [P] [US1] Escrever `code-smells-project/.claude/skills/refactor-arch/references/project-analysis.md` (área 1, com sumário): heurísticas de detecção de linguagem (extensões, manifestos `requirements.txt`/`pyproject.toml`/`package.json`/`pom.xml`/`go.mod`/`Gemfile`/`composer.json`), framework e versão (dependências declaradas + imports/bootstrap), banco de dados (drivers/ORMs, arquivo vs. memória), domínio (derivado de entidades e rotas), classificação da arquitetura atual (monolito, camadas parciais, MVC); regra de contagem de arquivos-fonte de research R5 (exclusões `.claude/`, `.git/`, `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `vendor/`, `dist/`, `build/`, manifestos, lockfiles, docs, exemplos de requisição); inventário de endpoints por framework (decorators, `add_url_rule`, blueprints/routers, `app.<verbo>(`, `router.<verbo>(`) com campos do data-model §5 (`method`, `path`, `source`, `params`, `side_effect` ∈ `read|create|update|delete|admin`); detecção dos passos de execução (README, scripts do manifesto, seed); regra "campo não identificável = `not detected`"; formato do banner de [console-output.md](./contracts/console-output.md) Fase 1
- [X] T012 [P] [US1] Escrever `code-smells-project/.claude/skills/refactor-arch/references/anti-patterns-catalog.md` (área 2, com sumário): escala de severidade copiando as definições do enunciado (CRITICAL, HIGH, MEDIUM, LOW baseadas em MVC e SOLID); 20 entradas com os campos do data-model §2 (`id`, `name`, `severity`, `category`, `detection_signals` concretos com exemplos Python e Node, `false_positive_notes`, `impact`, `transformations`, `deprecated_mapping` quando aplicável): AP-01 Hardcoded Credentials/Secrets (CRITICAL→TP-01), AP-02 SQL Injection by String Building (CRITICAL→TP-02), AP-03 God Class/God File (CRITICAL→TP-03,TP-04), AP-04 Unprotected Administrative/Debug Endpoint (CRITICAL→TP-14), AP-05 Plaintext or Weak Password Storage (CRITICAL→TP-09), AP-06 Business Logic in Route Handlers (HIGH→TP-04), AP-07 Global Mutable State (HIGH→TP-05), AP-08 Tight Coupling without Dependency Injection (HIGH→TP-05), AP-09 Sensitive Data Exposure in Responses or Logs (HIGH→TP-15,TP-11), AP-10 Debug Mode or Unsafe Defaults Enabled (HIGH→TP-01), AP-11 N+1 Queries / Query inside Loop (MEDIUM→TP-07), AP-12 Missing Input Validation (MEDIUM→TP-08), AP-13 Scattered or Generic Error Handling (MEDIUM→TP-06), AP-14 Duplicated Code (MEDIUM→TP-16), AP-15 Deprecated API Usage (MEDIUM→TP-10; tabela obsoleto→moderno por stack, ex.: `datetime.utcnow()`→`datetime.now(timezone.utc)`, SQLAlchemy `Query.get()`→`Session.get()`, `new Buffer()`→`Buffer.from()`, `url.parse()`→`new URL()`, Express `req.param(name)`→`req.params`/`req.query`/`req.body`, Express `res.send(status, body)`/`res.json(status, obj)`→`res.status(status).send(body)`/`.json(obj)`; só listar APIs com depreciação documentada pelo fornecedor, para não gerar findings sem evidência), AP-16 Callback Hell (MEDIUM→TP-13), AP-17 Magic Numbers/Strings (LOW→TP-12), AP-18 Poor Naming (LOW→TP-17), AP-19 Print/Console Logging instead of Logger (LOW→TP-11), AP-20 Unused Imports/Dead Code (LOW→TP-18); seção "Como auditar" (varrer todos os arquivos-fonte, uma ocorrência conta uma vez, agrupar ocorrências listando todas as localizações, sem evidência sem finding, verificar cada linha citada)
- [X] T013 [P] [US1] Escrever `code-smells-project/.claude/skills/refactor-arch/references/report-template.md` (área 3): template exato de [contracts/audit-report.md](./contracts/audit-report.md) (cabeçalho `Project:` = nome do diretório, `Stack:`, `Files: <N> analyzed | ~<LOC> lines of code`, `## Summary`, `## Findings` com `### [SEV] <nome> (AP-NN)`, `File:`, `Description:`, `Impact:`, `Recommendation: … (TP-NN)`, linha `Deprecated APIs: none detected` quando aplicável, `Total`), regras de ordenação CRITICAL→LOW, consistência Summary/Total e checklist de autoverificação antes de imprimir
- [X] T014 [P] [US1] Implementar `code-smells-project/.claude/skills/refactor-arch/scripts/count-source-files.sh <project-dir> [ext ...]`: detecta extensões pela linguagem predominante quando não informadas, aplica as exclusões de research R5, imprime `FILES=<n>`, `LOC=<n>` e um caminho por linha; exit 2 em uso inválido
- [X] T015 [P] [US1] Implementar `code-smells-project/.claude/skills/refactor-arch/scripts/check-restore-point.sh <project-dir>`: imprime `GIT=yes|no`, `STATUS=ok|dirty|no-git`, `HEAD=<sha>`, `PENDING=<n>` e os arquivos pendentes usando `git status --porcelain -- . ':(exclude).claude'` executado no diretório do projeto; exit 0 se `ok`, 1 se `dirty`/`no-git`
- [X] T016 [P] [US1] Implementar `code-smells-project/.claude/skills/refactor-arch/scripts/resolve-output-path.sh <audit|validation> <project-name> [N]`: raiz = `git rev-parse --show-toplevel` (fallback diretório atual); pasta `reports/` (audit) ou `evidence/` (validation); `N` = argumento numérico → senão arquivo existente da mesma pasta cuja linha `Project: <project-name>` (audit) ou título `# Validation Evidence — <project-name>` (validation) corresponda → senão maior `N` existente + 1 (1 se vazio); imprime `ROOT=`, `N=`, `PATH_OUT=`; não cria arquivos
- [X] T017 [US1] Testes de contrato dos scripts T014–T016 (contracts/scripts-cli.md "Testes de contrato") executando-os contra `code-smells-project/`, `ecommerce-api-legacy/` e `task-manager-api/`: contagens esperadas 4 / 3 / 15 arquivos-fonte; `STATUS=ok` nos 3 e `STATUS=dirty` após criar um arquivo temporário não ignorado (removê-lo em seguida); `N` resolvido 1/2/3 sem argumentos com `reports/` vazio e reuso do `N` com relatório existente; exit 2 para argumentos inválidos; corrigir os scripts até passarem
- [X] T018 [US1] Escrever a seção `## Phase 1` de `code-smells-project/.claude/skills/refactor-arch/SKILL.md`: passos (ler `references/project-analysis.md`; executar `count-source-files.sh` e `check-restore-point.sh` com procedimento manual equivalente; inventariar endpoints e passos de execução; não executar nada com efeito colateral), critério de saída e banner exato da Fase 1
- [X] T019 [US1] Escrever a seção `## Phase 2` de `code-smells-project/.claude/skills/refactor-arch/SKILL.md`: ler `references/anti-patterns-catalog.md` e `references/report-template.md`; auditar todos os arquivos-fonte; imprimir o relatório; resolver o caminho com `resolve-output-path.sh audit <nome-do-diretório> $ARGUMENTS` (argumento não numérico ignorado com aviso) e gravar o arquivo com conteúdo idêntico ao impresso; imprimir `Report saved to: …`; se o ponto de restauração não for `ok`, imprimir a mensagem de bloqueio de [console-output.md](./contracts/console-output.md) e encerrar; caso contrário perguntar `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e aguardar; somente `y|yes|s|sim` libera a Fase 3, qualquer outra resposta imprime `Phase 3 skipped. No project files were modified.`
- [X] T020 [US1] Validar US1 (Independent Test acima) executando `claude "/refactor-arch"` em `code-smells-project/` e respondendo `n`; conferir SC-001, SC-002, SC-003, SC-005 e que ≥ 5 problemas da Análise Manual do projeto 1 aparecem como findings; em seguida testar o bloqueio (US1 cenário 8): criar um arquivo temporário não ignorado em `code-smells-project/`, reexecutar, confirmar a mensagem `Phase 3 is blocked: …` sem pergunta de confirmação e remover o arquivo; se algo falhar, corrigir os arquivos da skill (não o projeto) e repetir; commitar `feat(skill): phases 1-2 of refactor-arch` (sem commitar `reports/` ainda)

**Checkpoint**: MVP — auditoria segura e arquivada funcionando no projeto 1

---

## Phase 4: User Story 2 - Refatorar para MVC com validação comprovada e reversível (Priority: P2)

**Goal**: Fase 3 completa — linha de base de comportamento, refatoração MVC, validação (boot + endpoints + reauditoria zero), evidência gravada, falha com diagnóstico e reversão

**Independent Test**: em `code-smells-project/` na linha de base do código, executar a skill até o fim com `y`; obter `PHASE 3: REFACTORING COMPLETE`, `evidence/validation-project-1.md` com `Result: CLEAN`, 100% dos endpoints `✓`/`declared` e reauditoria 0; num teste de falha, confirmar que a reversão deixa `git status --porcelain -- code-smells-project` vazio com `.claude/` e `.venv/` intactos

### Implementation for User Story 2

- [X] T021 [P] [US2] Escrever `code-smells-project/.claude/skills/refactor-arch/references/mvc-guidelines.md` (área 4, com sumário): responsabilidades e proibições de cada camada — config (valores de ambiente, segredos só por variável de ambiente, defaults não sensíveis para boot local), models (acesso a dados, sem HTTP), views/routes (só roteamento/serialização, sem regra de negócio nem SQL), controllers (fluxo da aplicação e regras), middlewares (error handler centralizado), entry point/composition root (monta dependências e registra rotas); mapeamento de diretórios para Python/Flask e Node/Express (e notas para outras stacks); regras de adaptação: monolito → criar camadas; projeto parcialmente organizado → preservar o que cumpre as regras e mover só o necessário; manter comandos de boot e passos de setup funcionando (ou atualizar a documentação do projeto); proibição de adicionar dependências de terceiros salvo indispensável (declarar no manifesto e no resumo); ambiente isolado de dependências (research R8)
- [X] T022 [P] [US2] Escrever `code-smells-project/.claude/skills/refactor-arch/references/refactoring-playbook.md` (área 5, com sumário): 18 padrões com os campos do data-model §3 (`id`, `resolves`, `steps`, `before`/`after` em Python/Flask e Node/Express com domínio neutro, `layer_target`, `contract_risk`): TP-01 Extract Environment-backed Config, TP-02 Parameterized Queries, TP-03 Split God Class by Domain and Layer, TP-04 Thin Routes / Move Logic to Controllers, TP-05 Composition Root and Dependency Injection, TP-06 Centralized Error Handler, TP-07 Eliminate N+1 with JOIN/Eager Loading/Batch, TP-08 Validate Input at the Boundary, TP-09 Secure Password Hashing (stdlib/lib padrão da stack, migração transparente no login), TP-10 Replace Deprecated API, TP-11 Structured Logger, TP-12 Named Constants, TP-13 Async/Await instead of Nested Callbacks, TP-14 Protect or Disable Administrative Endpoints (manter rota, desabilitar por config e/ou exigir autorização; declarar mudança de contrato — research R10), TP-15 Response Serialization Allow-list, TP-16 Extract Shared Helper, TP-17 Rename for Intent, TP-18 Remove Dead Code and Unused Imports; ordem recomendada de aplicação (segurança → estrutura → qualidade)
- [X] T023 [P] [US2] Escrever `code-smells-project/.claude/skills/refactor-arch/references/validation-protocol.md` (com sumário): (1) pré-condição ponto de restauração `ok`; (2) ambiente isolado — `git check-ignore` antes de criar, reutilizar se existir, Python `.venv` + `pip install -r`, Node `npm ci`/`npm install`, nunca global; (3) linha de base de comportamento (research R9): plano de requisições em diretório temporário fora do repo (`mktemp -d`), uso de exemplos do projeto (ex.: arquivos `.http`) ou payloads derivados do código, ordem leituras→criações→atualizações→remoções→admin, `workspace-artifacts.sh snapshot`, `check-port.sh` (porta ocupada sem alternativa não invasiva = falha externa; resposta de outro processo nunca conta como boot), setup documentado, boot em background guardando o PID, `wait-for-http.sh <url> <timeout> <pid>`, `probe-endpoints.sh`, parada do processo, `workspace-artifacts.sh diff` e remoção dos artefatos de runtime novos **após cada execução da aplicação** (original e refatorada), `source: captured|inferred`; todos os arquivos de trabalho em `mktemp -d` removido ao final da Fase 3; proibido criar arquivos ignorados pelo git além do ambiente isolado e dos artefatos de runtime removidos (usar `.env.example` versionável, nunca `.env`); (4) definição de "formato" = status + tipo do corpo + chaves recursivas (primeiro elemento de listas), ignorando valores/ids/timestamps/ordem; (5) validação pós-refatoração com o mesmo estado inicial e as mesmas requisições, comparação por endpoint (`✓`, `✗`, `declared`); (6) reauditoria com o catálogo — zero anti-patterns de qualquer severidade; (7) template exato de [validation-evidence.md](./contracts/validation-evidence.md) e gravação via `resolve-output-path.sh validation <nome> <N do relatório>`; (8) fluxo de falha: não remendar, banner `PHASE 3: REFACTORING FAILED` com `Failure type: skill|external`, diagnóstico (erro, `TP`/referência de origem ou `environment`, lacuna provável na skill ou orientação de correção do ambiente), gravar evidência, perguntar `Revert project to the restore point? [y/n]`, executar `revert-project.sh` só após `y`; (9) encerrar todos os processos iniciados inclusive em falha
- [X] T024 [P] [US2] Implementar `code-smells-project/.claude/skills/refactor-arch/scripts/workspace-artifacts.sh snapshot|diff <project-dir> <state-file>`: `snapshot` grava a lista de arquivos do projeto (incluindo ignorados, via `find`) em `state-file`; `diff` imprime um caminho novo por linha, excluindo `.claude/` e diretórios de ambiente isolado (`.venv/`, `venv/`, `node_modules/`); somente leitura do projeto
- [X] T025 [P] [US2] Implementar `code-smells-project/.claude/skills/refactor-arch/scripts/wait-for-http.sh <url> [timeout-seconds] [pid]` (polling com `curl`; `READY=yes` exit 0 na primeira resposta HTTP enquanto o `pid` informado continua vivo; `READY=no` exit 1 por timeout — default documentado no cabeçalho — ou se o `pid` morrer) e `code-smells-project/.claude/skills/refactor-arch/scripts/check-port.sh <host> <port>` (`PORT_FREE=yes` exit 0 quando a conexão é recusada; `PORT_FREE=no` exit 1 quando algo responde ou aceita conexão)
- [X] T026 [P] [US2] Implementar `code-smells-project/.claude/skills/refactor-arch/scripts/probe-endpoints.sh <base-url> <requests-file> <out-file>`: lê linhas `method<TAB>path<TAB>body-file-or-dash` (ignora `#`), envia com `curl` (`Content-Type: application/json` quando há corpo) e grava no `out-file` por requisição `### <#> <METHOD> <PATH>`, `STATUS=<code>` e o corpo bruto; exit 3 se `curl` ausente
- [X] T027 [P] [US2] Implementar `code-smells-project/.claude/skills/refactor-arch/scripts/revert-project.sh <project-dir>`: no diretório do projeto executa `git restore --source=HEAD --staged --worktree -- . ':(exclude).claude'` e `git clean -fd -- . ':(exclude).claude'` (sem `-x`, preservando ignorados como o ambiente isolado); recusa (exit 2) se o diretório não estiver num repositório git; imprime `REVERTED=yes` e `HEAD=<sha>`
- [X] T028 [US2] Testes de contrato dos scripts T024–T027 nos 3 projetos: snapshot/diff detecta um arquivo `*.db` criado e ignora `.venv/`/`node_modules/`; `wait-for-http.sh` retorna `READY=yes` com o original rodando (passando o PID) e `READY=no` com porta fechada ou PID encerrado; `check-port.sh` retorna `PORT_FREE=no` com uma aplicação escutando e `PORT_FREE=yes` após pará-la; `probe-endpoints.sh` grava status e corpo de 2 requisições de leitura por projeto; `revert-project.sh` desfaz um arquivo modificado e um novo arquivo não ignorado mantendo intactos `.claude/` e o ambiente isolado; exit 2 em argumentos inválidos; corrigir até passar
- [X] T029 [US2] Escrever a seção `## Phase 3` de `code-smells-project/.claude/skills/refactor-arch/SKILL.md`: ordem — confirmar ponto de restauração → criar diretório temporário de trabalho → ambiente isolado → linha de base de comportamento (com verificação de porta e limpeza de artefatos de runtime) → ler `references/mvc-guidelines.md` e `references/refactoring-playbook.md` → aplicar os `TP` de todos os findings (segurança → estrutura → qualidade), sem tocar `.claude/` e `reports/` → validar conforme `references/validation-protocol.md` → gravar evidência → sucesso: banner `PHASE 3: REFACTORING COMPLETE` de [console-output.md](./contracts/console-output.md) com árvore, mudanças de contrato declaradas e as 3 verificações; falha: fluxo de falha e oferta de reversão; incluir procedimento manual equivalente para cada script da fase
- [X] T030 [US2] Gate G2 estático na cópia canônica (quickstart §3): corpo do `SKILL.md` < 500 linhas; `description` ≤ 1024 caracteres; 6 arquivos em `references/` com as 5 áreas identificáveis por título; sumário nos arquivos > 100 linhas; 20 `AP-` com as 4 severidades e AP de API deprecated; 18 `TP-` todos com antes/depois; todo `AP` aponta para `TP` existente; `grep -rniE 'produto|usuario|pedido|itens_pedido|AppManager|checkout|financial|enrollment|course|loja\.db|tasks\.db|task_routes|report_routes' code-smells-project/.claude/skills/refactor-arch` sem ocorrências (ocorrências em prosa genérica também devem ser reescritas para manter a verificação objetiva); nenhum bloco de script multi-linha fora do playbook; 8 scripts em `scripts/` todos citados no `SKILL.md` com procedimento manual; corrigir até passar
- [X] T031 [US2] Garantir a linha de base do código do projeto 1 (`git status --porcelain -- code-smells-project` vazio fora de `.claude/`, código igual a `6d1ce62`) e commitar a skill (`feat(skill): phase 3 refactoring and validation`) para registrar a versão usada na execução
- [X] T032 [US2] Executar `claude "/refactor-arch"` em `code-smells-project/` e responder `y`; se `FAILED`: aceitar a reversão, registrar a entrada em `docs/iteration-log.md`, corrigir a skill de forma genérica na cópia canônica, repetir T030, commitar `fix(skill): …` e reexecutar (proibido reexecutar com a skill inalterada, salvo falha externa registrada) até uma execução limpa; validar US2 (Independent Test) e o checklist da Fase 3 do enunciado para o projeto 1
- [X] T033 [US2] Conferir a execução limpa do projeto 1 contra os contratos: `evidence/validation-project-1.md` segue [validation-evidence.md](./contracts/validation-evidence.md) com os 19 endpoints na tabela, `Source: captured`, mudanças de contrato declaradas coerentes com o resumo da Fase 3 e `Remaining anti-patterns: 0`; a saída da Fase 3 segue [console-output.md](./contracts/console-output.md); `git diff --stat -- code-smells-project/.claude` vazio (skill intacta)
- [X] T034 [US2] Commitar a execução limpa do projeto 1: código refatorado de `code-smells-project/`, `reports/audit-project-1.md` e `evidence/validation-project-1.md` (`refactor(project-1): apply refactor-arch phase 3` e `docs(reports): add audit and evidence for project 1`); confirmar que `.venv/` e `*.db` não entraram no commit
- [X] T035 [US2] Teste controlado do fluxo de falha (US2 cenários 4–5, SC-007) — obrigatório se nenhuma execução real terminou em `FAILED`: criar um worktree temporário destacado fora do repositório no commit da skill registrado em T031 — projeto ainda na linha de base do código e sem alterações pendentes (`git worktree add --detach "$(mktemp -d)/wt" <sha-de-T031>`) — e **somente na cópia do worktree** acrescentar a `references/validation-protocol.md` uma verificação impossível (ex.: exigir `200` em `GET /__refactor_arch_failure_probe__`); executar `claude "/refactor-arch"` em `<worktree>/code-smells-project/` com `y`; confirmar banner `PHASE 3: REFACTORING FAILED` com `Failure type: skill`, diagnóstico, `evidence/validation-project-1.md` gravado na raiz do worktree com `Result: FAILED`, oferta de reversão e, após `y`, `git status --porcelain -- code-smells-project` vazio no worktree com `.claude/` e `.venv/` preservados; registrar o resultado em `docs/iteration-log.md` do repositório principal como teste (não como iteração) e remover o worktree (`git worktree remove --force`), sem nenhum commit no worktree

**Checkpoint**: projeto 1 refatorado por execução limpa, com relatório e evidência gravados pela skill

---

## Phase 5: User Story 3 - Iterar e reutilizar a mesma skill em outra stack e em projeto parcialmente organizado (Priority: P3)

**Goal**: a mesma skill, sem modificações locais, produz execuções limpas nos projetos 2 e 3; toda iteração segue reverter → atualizar → reexecutar

**Independent Test**: `diff -r` vazio entre as 3 cópias; `evidence/validation-project-2.md` e `-3.md` com `Result: CLEAN`; toda reexecução após falha no `docs/iteration-log.md` com `skill_version_before ≠ skill_version_after` (ou `external_failure = true`)

### Implementation for User Story 3

- [X] T036 [US3] Sincronizar a skill (Gate G3): copiar `code-smells-project/.claude/skills/refactor-arch/` para `ecommerce-api-legacy/.claude/skills/refactor-arch/` e `task-manager-api/.claude/skills/refactor-arch/` preservando permissões de execução; verificar `diff -r` vazio para os dois pares; commitar `chore(skill): sync refactor-arch copies`
- [X] T037 [US3] Executar `claude "/refactor-arch"` em `ecommerce-api-legacy/` (linha de base do código, ponto de restauração `ok`) e responder `y`; verificar Fase 1 (JavaScript/Node.js + Express, domínio LMS com checkout, Source files = 3), relatório `reports/audit-project-2.md` (≥ 5 findings, ≥ 1 CRITICAL/HIGH, ≥ 5 problemas da Análise Manual cobertos) e evidência `CLEAN`; em falha aplicar o ciclo de T032 (corrigir só na cópia canônica, repetir T030 e T036, registrar em `docs/iteration-log.md`, reexecutar)
- [X] T038 [US3] Commitar a execução limpa do projeto 2: código refatorado de `ecommerce-api-legacy/`, `reports/audit-project-2.md` e `evidence/validation-project-2.md`; confirmar que `node_modules/` não entrou no commit
- [X] T039 [US3] Executar `claude "/refactor-arch"` em `task-manager-api/` e responder `y`; verificar Fase 1 (Python/Flask, domínio Task Manager, Source files = 15), relatório `reports/audit-project-3.md` (≥ 5 findings, ≥ 1 CRITICAL/HIGH apesar das camadas existentes), preservação das partes já adequadas, todos os 22 endpoints `✓`/`declared`, passo de seed mantido ou documentado, evidência `CLEAN`; em falha aplicar o ciclo de T032
- [X] T040 [US3] Commitar a execução limpa do projeto 3: código refatorado de `task-manager-api/`, `reports/audit-project-3.md` e `evidence/validation-project-3.md`; confirmar que `.venv/`, `tasks.db` e `instance/` não entraram
- [ ] T041 [US3] Consistência de versão: se a skill mudou depois da execução aceita de algum projeto, restaurar esse projeto à linha de base do código (`git checkout 6d1ce62 -- <projeto>` seguido de remoção dos arquivos que não existiam em `6d1ce62`, excluindo `<projeto>/.claude/`), reexecutar a skill com a versão final e recommitar código, relatório e evidência, para que os 3 resultados correspondam à skill entregue; confirmar `diff -r` vazio entre as 3 cópias finais

**Checkpoint**: critérios de aceite atendidos em 3/3 projetos com a mesma versão da skill

---

## Phase 6: User Story 4 - Documentar e entregar o resultado para avaliação (Priority: P4)

**Goal**: README completo (A–D), histórico de iterações e evidências referenciadas, de modo que o avaliador verifique tudo navegando no repositório

**Independent Test**: um leitor sem contexto localiza, em até 5 minutos, Análise Manual, 3 relatórios, código refatorado, checklists, evidências, histórico de iterações e "Como Executar", e reproduz a validação de um projeto só com o README (SC-014)

### Implementation for User Story 4

- [ ] T042 [US4] Preencher a coluna `matched_by` das 3 tabelas da seção `## Análise Manual` do `README.md` com o finding correspondente (`AP-NN` + localização) de `reports/audit-project-{1,2,3}.md`; confirmar ≥ 5 correspondências por projeto (SC-004)
- [ ] T043 [US4] Escrever a seção `## Construção da Skill` do `README.md`: estrutura do `SKILL.md` e das 6 referências e por quê (progressive disclosure, research R3), frontmatter e decisões (`disable-model-invocation`, argumento opcional), scripts e regras de agnosticismo, anti-patterns escolhidos e justificativa por severidade, como a skill é agnóstica (heurísticas, exemplos multi-stack, ausência de identificadores dos alvos, cópias idênticas), subseção "Desafios" com o resumo do `docs/iteration-log.md` (iterações, erros, causas, mudanças na skill)
- [ ] T044 [US4] Escrever a seção `## Resultados` do `README.md`: tabela de findings por severidade por projeto (de `reports/`), árvores de diretórios antes (commit `6d1ce62`) e depois para cada projeto, checklist de validação do enunciado (Fase 1, 2 e 3) preenchido para cada um dos 3 projetos, links para `evidence/validation-project-{1,2,3}.md` com destaque de boot e endpoints, mudanças de contrato declaradas e observações sobre o comportamento da skill em Python/Flask vs. Node/Express e em projeto monolítico vs. parcialmente organizado
- [ ] T045 [US4] Escrever a seção `## Como Executar` do `README.md`: pré-requisitos (Claude Code, git, curl, python3 com venv, node/npm), comandos por projeto iniciando o Claude Code dentro do diretório do projeto (`cd <projeto>` e `claude "/refactor-arch"`), argumento opcional `[report-number]`, o que esperar em cada fase, como validar (evidência, subir o app refatorado no ambiente isolado, chamar endpoints), como reverter e reexecutar
- [ ] T046 [US4] Commitar a documentação (`docs: complete README sections B, C and D`) incluindo `docs/iteration-log.md`

**Checkpoint**: entrega documental completa

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: verificação final (Gate G5) e limpeza

- [ ] T047 Teste do leitor sem contexto (SC-014): numa sessão nova do Claude Code sem histórico (ou com outra pessoa), pedir que localize no repositório Análise Manual, 3 relatórios, código refatorado, checklists, evidências, histórico de iterações e "Como Executar" e que reproduza a validação de um projeto seguindo apenas o `README.md`; cronometrar (≤ 5 minutos para localizar) e corrigir no `README.md` qualquer lacuna encontrada
- [ ] T048 Gate G5 (quickstart §7): `reports/` com exatamente 3 arquivos; `evidence/` com exatamente 3 arquivos todos `Result: CLEAN`; README com seções A–D completas; `diff -r` vazio entre as 3 cópias da skill; nenhum `.venv/`, `node_modules/`, `*.db`, `.env` no índice (`git ls-files`); critérios de aceite 3/3
- [ ] T049 Revisar a matriz de rastreabilidade em `specs/001-refactor-arch-skill/plan.md` marcando cada uma das 31 linhas como verificada (com o artefato real) e conferir SC-001 a SC-008 da spec
- [X] T050 [P] Remover o comentário "Sync Impact Report" do topo de `.specify/memory/constitution.md` (material de revisão, não governança) e commitar `docs: finalize constitution v2.2.0`
- [ ] T051 Revisão de conformidade final com a constituição (Governance): percorrer cada regra DEVE/NÃO DEVE dos princípios I–VII e das Restrições do Entregável contra o repositório; registrar desvios corrigidos; deixar o branch pronto para o autor publicar o fork público no GitHub

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências; T003–T005 em paralelo após T001
- **Foundational (Phase 2)**: depende do Setup; T006 → T007 → T008 → T009 (mesmo arquivo `README.md`); T010 pode correr em paralelo a T006–T009
- **US1 (Phase 3)**: depende da Phase 2 (catálogo usa a Análise Manual; seções do `SKILL.md` dependem de T010)
- **US2 (Phase 4)**: depende de US1 (a Fase 3 da skill pressupõe Fases 1–2 e o catálogo)
- **US3 (Phase 5)**: depende de US2 (precisa da skill completa e do ciclo validado no projeto 1)
- **US4 (Phase 6)**: T042 depende dos 3 relatórios (US3); T043–T045 dependem de US3 concluída
- **Polish (Phase 7)**: depende de todas as stories

### User Story Dependencies

- **US1 (P1)**: após Foundational — independente
- **US2 (P2)**: após US1 — estende o mesmo `SKILL.md`
- **US3 (P3)**: após US2 — reutiliza a skill completa
- **US4 (P4)**: após US3 — documenta resultados reais

### Within Each User Story

- Referências e scripts (arquivos distintos) antes das seções do `SKILL.md` que os citam
- Testes de contrato dos scripts antes da execução da skill
- Gate G2 antes de qualquer execução com `y`
- Commit da versão da skill antes de cada execução (para registrar `skill_version`)

### Parallel Opportunities

- T002–T005 (Setup)
- T010 em paralelo à Análise Manual (T006–T009)
- US1: T011, T012, T013, T014, T015, T016
- US2: T021, T022, T023, T024, T025, T026, T027
- Polish: T050 em paralelo a T048–T049

---

## Parallel Example: User Story 1

```bash
Task: "Escrever references/project-analysis.md (T011)"
Task: "Escrever references/anti-patterns-catalog.md (T012)"
Task: "Escrever references/report-template.md (T013)"
Task: "Implementar scripts/count-source-files.sh (T014)"
Task: "Implementar scripts/check-restore-point.sh (T015)"
Task: "Implementar scripts/resolve-output-path.sh (T016)"
```

## Parallel Example: User Story 2

```bash
Task: "Escrever references/mvc-guidelines.md (T021)"
Task: "Escrever references/refactoring-playbook.md (T022)"
Task: "Escrever references/validation-protocol.md (T023)"
Task: "Implementar scripts/workspace-artifacts.sh, wait-for-http.sh, probe-endpoints.sh, revert-project.sh (T024–T027)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 (Setup) + Phase 2 (Análise Manual + esqueleto)
2. Phase 3 (US1): auditoria somente-leitura com relatório gravado
3. **STOP and VALIDATE**: T020 no projeto 1 com resposta `n`

### Incremental Delivery

1. US1 → auditoria funcionando (MVP)
2. US2 → refatoração validada no projeto 1 (primeira execução limpa)
3. US3 → mesma skill limpa nos projetos 2 e 3 (critérios de aceite 3/3)
4. US4 → documentação para avaliação
5. Polish → Gate G5 e conformidade final

---

## Notes

- Nunca editar à mão o código dos projetos-alvo; só a skill muda entre iterações
- Toda execução com falha: reverter → registrar em `docs/iteration-log.md` → corrigir a skill na cópia canônica → G2 → commit → G3 → reexecutar
- Commits em Conventional Commits, granulares por etapa (constituição)
- Publicar o fork no GitHub é ação do autor
