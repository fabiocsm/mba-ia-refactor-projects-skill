---
name: refactor-arch
description: >-
  Executa auditoria arquitetural e refatoração MVC de um projeto backend legado em três fases:
  analisa a stack (linguagem, framework, banco, domínio, arquitetura), audita o código contra um
  catálogo de anti-patterns e code smells com severidade (CRITICAL a LOW), arquivo e linha,
  grava o relatório em reports/ e, somente após confirmação explícita, reestrutura o projeto
  para o padrão MVC com validação (boot da aplicação, comparação dos endpoints com a linha de
  base de comportamento e reauditoria com zero anti-patterns) e evidência em evidence/. Usar
  quando o usuário invocar /refactor-arch dentro do diretório de um projeto (Python/Flask,
  Node.js/Express ou outra stack web) para auditar ou refatorar sua arquitetura. Aceita um
  número opcional de relatório.
argument-hint: "[report-number]"
disable-model-invocation: true
---

# refactor-arch

Audita e refatora para MVC o projeto do **diretório atual** (onde o Claude Code foi iniciado).
Nome do projeto = nome desse diretório. Argumento recebido: `$ARGUMENTS` (número opcional do
relatório).

## Regras não negociáveis

1. Três fases, nesta ordem, sem pular nem fundir: Phase 1 → Phase 2 → (confirmação) → Phase 3.
2. **Fases 1 e 2 são somente leitura** em relação ao projeto: não crie, altere, mova nem remova
   arquivos; não instale dependências; não execute a aplicação nem comandos com efeito colateral.
   Única escrita permitida: o relatório em `reports/` na raiz do repositório, ao final da Fase 2.
3. **Pausa obrigatória** ao final da Fase 2: faça a pergunta de confirmação e encerre a resposta.
   Só uma resposta afirmativa explícita do usuário (`y`, `yes`, `s`, `sim`) libera a Fase 3.
4. A Fase 3 nunca altera `.claude/` (inclusive esta skill) nem `reports/`. Fora do projeto, a
   única escrita é a evidência em `evidence/`; arquivos efêmeros só no diretório temporário do
   sistema (`mktemp -d`), removido ao final.
5. **Falha não é remendada.** A validação tem uma única tentativa: a partir do primeiro boot da
   aplicação refatorada, nenhum arquivo do projeto é alterado e a validação não é reiniciada. Se
   uma verificação falhar — ou se você notar algo a corrigir —, declare FALHA, diagnostique e
   ofereça reversão. Corrigir e "validar de novo" invalida a execução.
6. Nunca declare sucesso sem evidência da validação.
7. **Não altere o estado do repositório git:** proibido `git stash`, `switch`,
   `reset`, `restore`, `add`, `commit`, `clean` no projeto. Única exceção: `revert-project.sh`
   após falha e confirmação do usuário.

8. **Sem pausas na Fase 3:** depois do `y`, execute a Fase 3 inteira em sequência, sem parar
   para pedir confirmação ou "continuar". As únicas perguntas da skill são a do gate da Fase 2 e
   a de reversão após falha.

## Idioma e formato

Banners, rótulos e perguntas em inglês exatamente como neste arquivo; descrições, impactos,
recomendações e diagnósticos em português. Separador: linha de 32 `=`.

## Checklist de progresso

Copie e mantenha atualizado durante a execução:

```text
- [ ] Phase 1: analysis banner + endpoint inventory printed
- [ ] Phase 2: all source files audited, report printed and saved
- [ ] Phase 2: confirmation asked (or block message printed) — STOP
- [ ] Phase 3: restore point ok, work dir created, isolated environment ready
- [ ] Phase 3: behavior baseline captured on the ORIGINAL code — before reading guidelines/playbook or editing
- [ ] Phase 3: refactoring applied for every finding (MVC structure)
- [ ] Phase 3: self-review done (pre-re-audit, contract by code, syntax) — last chance to edit
- [ ] Phase 3: single-attempt validation — fingerprint, boot, endpoints, re-audit, fingerprint
- [ ] Phase 3: evidence saved, final banner printed, work dir removed
```

## Referências

Leia cada arquivo **quando a fase indicar**, por inteiro:

| Arquivo | Área | Quando ler |
|---|---|---|
| [references/project-analysis.md](references/project-analysis.md) | Análise de projeto | início da Fase 1 |
| [references/anti-patterns-catalog.md](references/anti-patterns-catalog.md) | Catálogo de anti-patterns | Fase 2 (auditoria) e Fase 3 (reauditoria) |
| [references/report-template.md](references/report-template.md) | Template de relatório | Fase 2, antes de montar o relatório |
| [references/mvc-guidelines.md](references/mvc-guidelines.md) | Guidelines de arquitetura MVC | Fase 3, antes de refatorar |
| [references/refactoring-playbook.md](references/refactoring-playbook.md) | Playbook de refatoração | Fase 3, antes de refatorar |
| [references/validation-protocol.md](references/validation-protocol.md) | Linha de base, validação, evidência, reversão | Fase 3, logo após a confirmação |

## Scripts

Scripts POSIX em `${CLAUDE_SKILL_DIR}/scripts/`. **Execute-os** (não leia o conteúdo) com
`sh "${CLAUDE_SKILL_DIR}/scripts/<nome>.sh" <args>`; a saída é `KEY=VALUE`. Exit codes: `0` ok,
`1` condição negativa esperada, `2` uso inválido, `3` dependência ausente. Se um script falhar
com `2`/`3` ou não puder ser executado, use o procedimento manual equivalente.

| Script | Uso | Fase | Procedimento manual equivalente |
|---|---|---|---|
| `count-source-files.sh` | `<project-dir> [ext ...]` → `FILES`, `LOC`, caminhos | 1, 3 | Listar com `find` os arquivos com extensão da linguagem predominante, excluindo `.claude/ .git/ node_modules/ .venv/ venv/ __pycache__/ vendor/ dist/ build/`; somar linhas com `wc -l` |
| `check-restore-point.sh` | `<project-dir>` → `GIT`, `STATUS`, `HEAD`, `PENDING` | 1, 3 | No projeto: `git rev-parse --is-inside-work-tree`, `git rev-parse --short HEAD` e `git status --porcelain --untracked-files=all -- . ':(exclude).claude'` (vazio = `ok`) |
| `resolve-output-path.sh` | `<audit\|validation> <project-name> [N]` → `ROOT`, `N`, `PATH_OUT` | 2, 3 | Raiz = `git rev-parse --show-toplevel`; `N` = argumento → arquivo existente cuja linha `Project:` (ou título da evidência) é o projeto → maior `N` existente + 1 |
| `workspace-artifacts.sh` | `snapshot\|diff <project-dir> <state-file>` → caminhos novos; `fingerprint <project-dir>` → `FINGERPRINT` | 3 | Antes: `find <projeto> -print` (sem `.claude .git .venv venv node_modules`) para um arquivo em `WORK`; depois: repetir e comparar com `comm -13`. Fingerprint: `git ls-files --cached --others --exclude-standard -- . ':(exclude).claude'` e `cksum` de cada arquivo, somados com `cksum` |
| `check-port.sh` | `<host> <port>` → `PORT_FREE`, `LISTENER_PIDS` | 3 | `curl -s -o /dev/null --max-time 2 http://<host>:<port>/` com exit 7 = livre; `lsof -t -iTCP:<port> -sTCP:LISTEN` lista os processos |
| `wait-for-http.sh` | `<url> [timeout] [pid]` → `READY` | 3 | Repetir `curl -s -o /dev/null -w '%{http_code}' <url>` a cada 1 s até código ≠ `000`, conferindo `kill -0 <pid>` |
| `probe-endpoints.sh` | `<base-url> <requests-file> <out-file>` | 3 | Para cada linha do plano, `curl -s -X <método> [-H 'Content-Type: application/json' --data-binary @<corpo>] -w '%{http_code}' <url>` e anotar status, tipo e corpo |
| `revert-project.sh` | `<project-dir>` → `REVERTED`, `HEAD` | 3 (falha + `y`) | No projeto: `git restore --source=HEAD --staged --worktree -- . ':(exclude).claude'` e `git clean -fd -- . ':(exclude).claude'` |

---

## Phase 1

**Objetivo:** entender a stack e mapear a arquitetura sem efeitos colaterais.

1. Leia `references/project-analysis.md`.
2. Execute `count-source-files.sh .` e `check-restore-point.sh .`.
3. Leia os manifestos e os arquivos-fonte necessários para detectar linguagem, framework e
   versão, dependências, banco e tabelas, domínio e arquitetura atual (heurísticas da
   referência). Campo sem evidência = `not detected`.
4. Inventarie **todos** os endpoints (`method`, `path`, `source`, `params`, `side_effect`) e os
   passos de execução (instalação, setup, boot, porta, URL de verificação).
5. Imprima o banner e, em seguida, o inventário:

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
Endpoint inventory:
<METHOD> <path> — <arquivo:linha> — <side_effect>
```

**Critério de saída:** banner completo, `Source files` igual a `FILES`, inventário com todos os
endpoints declarados no código.

## Phase 2

**Objetivo:** auditar todo o código contra o catálogo, gravar o relatório e pedir confirmação.

1. Leia `references/anti-patterns-catalog.md` e `references/report-template.md`.
2. Audite **todos** os arquivos-fonte listados na Fase 1 conforme "Como auditar" do catálogo.
   Verifique cada `arquivo:linha` citada antes de incluí-la.
3. Monte o relatório no formato exato do template e passe pela autoverificação do template.
4. Resolva o caminho: se `$ARGUMENTS` for um inteiro positivo, use-o como `N`; se estiver vazio,
   omita; se for outro valor, imprima `Warning: argument '<valor>' ignored (expected a report number).`
   e omita. Execute `resolve-output-path.sh audit <nome-do-diretório> [N]`.
5. Grave o relatório em `PATH_OUT` (crie `reports/` se não existir). Guarde `N` para a evidência.
6. **Releia o arquivo gravado** e imprima-o na resposta **integralmente**, copiando do arquivo —
   todos os findings de todas as severidades, sem resumir nem omitir —, seguido de
   `Report saved to: <PATH_OUT relativo à raiz>`. Confira que o número de findings impressos é o
   `Total`.
7. Gate de confirmação, conforme o `STATUS` do ponto de restauração da Fase 1:
   - `STATUS` ≠ `ok`: imprima, **no lugar da pergunta**,
     `Phase 3 is blocked: <motivo: no git repository | <k> pending changes outside .claude/>. Commit or discard pending changes, then re-run.`
     e encerre a execução.
   - `STATUS` = `ok`: imprima como última linha
     `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
     e **pare**, aguardando a resposta.
8. Resposta `y`/`yes`/`s`/`sim` (sem ambiguidade) → Fase 3. Qualquer outra →
   `Phase 3 skipped. No project files were modified.` e fim.

**Critério de saída:** relatório impresso e gravado com conteúdo idêntico; nenhum arquivo do
projeto alterado; pergunta (ou bloqueio) como última linha.

## Phase 3

**Objetivo:** reestruturar para MVC eliminando todos os findings, provar que a aplicação continua
funcionando e gravar a evidência.

A ordem abaixo é obrigatória. **Gate de ordem:** até imprimir a linha
`Behavior baseline captured: …` (passo 2), leia apenas `references/validation-protocol.md` e
não crie, altere nem remova nenhum arquivo do projeto.

1. **Preparação** — leia `references/validation-protocol.md` e siga §1–§2: ponto de restauração
   `ok` (senão, mensagem de bloqueio da Fase 2 e fim), diretório `WORK` com `mktemp -d`, versão da
   skill, ambiente isolado.
2. **Linha de base de comportamento** — §3–§5 do protocolo com a aplicação **original**, tal como
   está no ponto de restauração: plano de requisições, verificação de porta, setup, boot, probe,
   parada e remoção dos artefatos de runtime. Ao terminar, imprima
   `Behavior baseline captured: <k>/<k> endpoints (Source: captured|inferred)`.
   Se você perceber que alterou algum arquivo do projeto antes desta linha, a execução já falhou:
   vá para o fluxo de falha (protocolo §10) com `Failure type: skill`.
3. **Refatoração** — só agora leia `references/mvc-guidelines.md` e
   `references/refactoring-playbook.md`.
   - Escolha a estrutura alvo conforme o nível de organização (guidelines §3–§4).
   - Aplique os `TP-NN` de **todos** os findings do relatório, na ordem segurança → estrutura →
     qualidade, preservando o contrato externo (guidelines §5).
   - Registre cada mudança de contrato inevitável (correção de segurança) para declarar.
   - Mantenha comandos de boot/setup funcionando; não adicione dependências de terceiros; não
     toque `.claude/` nem `reports/`; não crie `.env`.
   - **Autorrevisão obrigatória antes de validar** (protocolo §7.1), feita por um subagente
     revisor independente com contexto limpo: pré-reauditoria completa com o catálogo, matriz de
     validação, conferência do contrato de cada endpoint (inclusive caminhos de erro) contra o
     código original. Repita com um novo subagente até não restar nada, no máximo 3 rodadas;
     faça a verificação sintática. Corrija tudo aqui — é a última oportunidade de alterar o código.
4. **Validação** — protocolo §7.2–§8, tentativa única, com o mesmo plano e o mesmo estado
   inicial: fingerprint inicial, (a) boot, (b) endpoints vs. linha de base, (c) reauditoria com
   zero findings por um novo subagente revisor, (d) fingerprint final igual ao inicial. Da primeira inicialização em diante,
   **nenhuma alteração** no projeto e nenhum segundo boot.
5. **Evidência** — protocolo §9: `resolve-output-path.sh validation <nome-do-diretório> <N>` e
   gravação do arquivo.
6. **Resultado**
   - Tudo aprovado → imprima:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios do projeto, sem .claude/, ambientes de dependências e caches>

## Declared contract changes
<lista "METHOD path — mudança (AP-NN)" ou "none">

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly (<k>/<k> match baseline <captured|inferred>)
  ✓ Zero anti-patterns remaining
Evidence saved to: <caminho relativo à raiz>
================================
```

   - Qualquer falha → protocolo §10 (sem remendos), imprima:

```text
================================
PHASE 3: REFACTORING FAILED
================================
Failure type: <skill | external>
## Failed checks
  ✗ <verificação>: <erro observado>
## Diagnosis
Origin:   <TP-NN / references/<arquivo>.md | environment>
Skill gap: <lacuna provável na skill | n/a (external): <orientação de correção>>
Evidence saved to: <caminho relativo à raiz>
================================
Revert project to the restore point? [y/n]
```

     e pare aguardando a resposta; trate-a conforme o protocolo §10.6.
7. **Encerramento** — protocolo §11: nenhum processo rodando, `WORK` removido.

**Critério de saída:** banner de sucesso com as 3 verificações `✓` e evidência `Result: CLEAN`,
ou banner de falha com diagnóstico, evidência `Result: FAILED` e a reversão oferecida.
