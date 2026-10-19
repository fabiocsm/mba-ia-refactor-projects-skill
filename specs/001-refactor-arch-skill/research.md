# Research: Skill refactor-arch

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-19

Fontes consultadas: enunciado (`README.md`, commit `6d1ce62`), constituição v2.2.0, documentação
oficial de Skills do Claude Code (`https://code.claude.com/docs/en/skills`, antigo
`docs.anthropic.com/en/docs/claude-code/skills`), guia de boas práticas de autoria de skills da
Anthropic e inspeção dos 3 projetos-alvo.

---

## R1. Frontmatter e invocação da skill

- **Decision**: frontmatter com `name: refactor-arch`, `description` (≤ 1024 caracteres, terceira
  pessoa, caso de uso principal primeiro), `argument-hint: "[report-number]"` e
  `disable-model-invocation: true`. Sem `allowed-tools`, `context: fork`, `model` ou `effort`.
  O número opcional do relatório é lido de `$ARGUMENTS`.
- **Rationale**:
  - A doc confirma: `name` define o comando do menu `/` (default = nome do diretório);
    `description` + `when_to_use` são truncados em 1.536 caracteres — o limite de 1.024 da
    constituição (alinhado ao limite da API de Skills) fica dentro dele.
  - `disable-model-invocation: true` impede que o modelo carregue a skill por conta própria; a
    skill reescreve código e só deve rodar quando o usuário digita `/refactor-arch`. A invocação
    explícita continua funcionando, então FR-001 é preservado.
  - `$ARGUMENTS` vazio = invocação do enunciado (`claude "/refactor-arch"`); `$ARGUMENTS` com um
    inteiro = `N` explícito (FR-016).
  - `context: fork` foi rejeitado: a Fase 2 precisa pausar e conversar com o usuário no mesmo
    contexto.
  - `allowed-tools` foi rejeitado: pré-aprovar Bash/Write reduziria o controle humano justamente
    numa skill que modifica código; as permissões padrão do Claude Code mantêm o usuário no laço.
- **Alternatives considered**: `user-invocable: false` (impediria `/refactor-arch`); deixar
  invocação automática habilitada (risco de refatoração não solicitada); `arguments: [n]` nomeado
  (desnecessário para um único argumento opcional).

## R2. Descoberta da skill dentro de cada projeto

- **Decision**: a skill vive em `<projeto>/.claude/skills/refactor-arch/` e é executada com o
  Claude Code iniciado **dentro** do diretório do projeto (`cd <projeto> && claude
  "/refactor-arch"`), exatamente como no enunciado.
- **Rationale**: a doc diz que skills de `.claude/skills/` do diretório de lançamento (e dos pais
  até a raiz do repositório) carregam no startup; skills em subdiretórios só carregam depois que
  o Claude lê um arquivo ali. Iniciar na raiz deixaria `/refactor-arch` indisponível no menu.
  As skills `speckit-*` da raiz também carregam (pai), sem conflito de nome.
- **Alternatives considered**: instalar na raiz (viola a constituição — Restrições do
  Entregável); `--add-dir` (passo extra fora do enunciado).

## R3. Organização dos arquivos de referência

- **Decision**: 6 arquivos em `references/`, todos referenciados diretamente pelo `SKILL.md`:

  | Arquivo | Área obrigatória | Carregado em |
  |---|---|---|
  | `project-analysis.md` | (1) Análise de projeto | Fase 1 |
  | `anti-patterns-catalog.md` | (2) Catálogo de anti-patterns | Fases 2 e 3 (reauditoria) |
  | `report-template.md` | (3) Template de relatório | Fase 2 |
  | `mvc-guidelines.md` | (4) Guidelines de arquitetura | Fase 3 |
  | `refactoring-playbook.md` | (5) Playbook de refatoração | Fase 3 |
  | `validation-protocol.md` | complementar (linha de base de comportamento, validação, evidência, reversão) | Fase 3 |

- **Rationale**: um arquivo por área torna a cobertura das 5 áreas verificável por título
  (Princípio V) e permite progressive disclosure por fase; o protocolo de validação é longo e
  frágil (baixa liberdade), por isso sai do `SKILL.md` para mantê-lo < 500 linhas. Arquivos com
  mais de 100 linhas abrem com sumário.
- **Alternatives considered**: arquivo único (estoura contexto, dificulta verificação); colocar o
  protocolo de validação no `SKILL.md` (risco de ultrapassar 500 linhas).

## R4. Scripts utilitários

- **Decision**: scripts POSIX `sh` em `scripts/`, invocados via `${CLAUDE_SKILL_DIR}/scripts/…`,
  cada um com cabeçalho de uso/dependências, saída `KEY=VALUE` ou linhas tabuladas, códigos de
  saída documentados e procedimento manual equivalente no `SKILL.md`:

  | Script | Fase | Efeito | Finalidade |
  |---|---|---|---|
  | `count-source-files.sh <dir>` | 1 | leitura | lista/conta arquivos-fonte com exclusões padrão |
  | `check-restore-point.sh <dir>` | 1 | leitura | git presente? alterações pendentes fora de `.claude/`? |
  | `resolve-output-path.sh <audit\|validation> <projeto> [N]` | 2, 3 | leitura | resolve raiz do repo e `N` |
  | `workspace-artifacts.sh snapshot\|diff <dir> <arquivo>` | 3 | leitura | detecta artefatos gerados por uma execução |
  | `check-port.sh <host> <port>` | 3 | leitura | confirma que a porta está livre antes do boot |
  | `wait-for-http.sh <url> [timeout] [pid]` | 3 | leitura | aguarda a aplicação responder enquanto o processo iniciado continua vivo |
  | `probe-endpoints.sh <base-url> <requests-file> <out-file>` | 3 | HTTP local | executa requisições e grava status + corpo |
  | `revert-project.sh <dir>` | 3 (após falha + confirmação) | destrutivo, escopo do projeto | volta ao ponto de restauração |

- **Rationale**: dependem só de `sh`, `git`, `curl`, `find`, `grep`, `sed`, `awk` — presentes em
  qualquer máquina que rode projetos Python ou Node, independentes da stack-alvo (Princípio V).
  Toda informação de projeto (diretório, URL, lista de requisições) entra por argumento.
  Comparação de "formato" de JSON fica com o agente (lê os corpos gravados), evitando exigir `jq`
  ou um runtime específico.
- **Alternatives considered**: scripts em Python (não garantido em projetos Node); `jq` (não
  instalado por padrão); nenhum script (perde reprodutibilidade de contagem, resolução de `N` e
  reversão segura).

## R5. Contagem de arquivos-fonte (SC-001)

- **Decision**: "arquivo-fonte" = arquivo com extensão de código da linguagem detectada,
  excluindo `.claude/`, `.git/`, diretórios de dependências e ambientes (`node_modules/`,
  `.venv/`, `venv/`, `__pycache__/`, `vendor/`, `dist/`, `build/`), manifestos, lockfiles,
  documentação e arquivos de exemplo de requisições.
- **Rationale**: reproduz o exemplo do enunciado (projeto 1 → "4 files analyzed": `app.py`,
  `controllers.py`, `models.py`, `database.py`). Contagens esperadas na linha de base do código: projeto 1 =
  4, projeto 2 = 3 (`src/*.js`), projeto 3 = 13 (`.py`, incluindo `__init__.py` e `seed.py`).
- **Alternatives considered**: contar todos os arquivos (incluiria `package-lock.json` com 2.300
  linhas e distorceria "~linhas de código").

## R6. Gravação de relatório e evidência; resolução de `N`

- **Decision**: raiz = `git rev-parse --show-toplevel` (fallback: diretório atual).
  Arquivos: `<raiz>/reports/audit-project-N.md` e `<raiz>/evidence/validation-project-N.md`.
  `N` = `$ARGUMENTS` numérico → senão arquivo existente cuja linha `Project: <nome-do-diretório>`
  corresponda → senão maior `N` existente + 1. A evidência usa o mesmo `N` do relatório.
  Escrita com a ferramenta de escrita do agente, imediatamente após imprimir o relatório.
- **Rationale**: genérico (sem nomes de projeto na skill) e produz os nomes exigidos na ordem
  1 → 2 → 3; reexecuções sobrescrevem o próprio arquivo.
- **Alternatives considered**: nome derivado do diretório (`audit-code-smells-project.md` —
  viola o nome exigido); pedir o número sempre (passo manual).

## R7. Ponto de restauração e reversão

- **Decision**:
  - Verificação (Fase 1, leitura): `git rev-parse` dentro do projeto e
    `git status --porcelain -- . ':(exclude).claude'` vazio.
  - Ponto de restauração = `HEAD` no momento da confirmação.
  - Reversão (após falha, com confirmação):
    `git restore --source=HEAD --staged --worktree -- . ':(exclude).claude'` +
    `git clean -fd -- . ':(exclude).claude'` executados no diretório do projeto.
- **Rationale**: escopo limitado ao projeto; `.claude/` excluído explicitamente; `reports/` e
  `evidence/` ficam fora do diretório do projeto; `git clean` **sem** `-x` preserva arquivos
  ignorados (o ambiente isolado de dependências). Artefatos de runtime ignorados (ex.: bancos
  `*.db`) são tratados por R9.
- **Ignorados**: a reversão não apaga arquivos ignorados; por isso (R9) os artefatos de runtime
  são removidos logo após cada execução da aplicação, e a Fase 3 não cria outros arquivos
  ignorados (ex.: `.env`; usa `.env.example` versionável).
- **Alternatives considered**: `git stash` (mistura com trabalho do usuário); commit automático
  de checkpoint (polui o histórico); cópia do diretório para temp (lenta, não versionada).

## R8. Ambiente isolado de dependências

- **Decision**: Python → `python3 -m venv .venv` no diretório do projeto e instalação via
  `.venv/bin/pip install -r <manifesto>`; execução com `.venv/bin/python`. Node →
  `npm install` (ou `npm ci` se houver lockfile) gerando `node_modules/` local. Antes de criar,
  `git check-ignore -q <caminho>` DEVE confirmar que o caminho é ignorado; o ambiente é
  reutilizado se existir. Outras stacks: mecanismo local equivalente descrito nas guidelines.
- **Rationale**: o `.gitignore` da raiz já cobre `.venv/` e `node_modules/` em qualquer
  subdiretório; nada é instalado globalmente (clarificação Q4).
- **Riscos identificados** (ambiente local: Python 3.14.5, Node v25.9.0, npm 11.16, git 2.52):
  - `sqlite3@^5.1.6` (projeto 2) é módulo nativo; pode não haver binário pré-compilado para
    Node 25 e exigir compilação (`node-gyp` + Xcode Command Line Tools). Falha aqui é **falha
    externa** (não da skill) e deve ser resolvida no ambiente antes das execuções.
  - Dependências fixadas antigas (ex.: `flask==3.0.0`, `marshmallow==3.20.1`) em Python 3.14.
  - Porta 5000 ocupada pelo Receptor AirPlay do macOS (`ControlCenter` escutando `*:5000`,
    respondendo `403` com `Server: AirTunes`); os projetos 1 e 3 fixam a porta 5000 no código.
    Sem tratamento, o boot do original falha e um `wait-for-http` ingênuo aceitaria a resposta do
    AirPlay. Remediação do ambiente: desativar o Receptor AirPlay (ação do autor).
  - **Mitigação**: tarefa de pré-voo que instala as dependências dos 3 projetos e sobe cada
    original antes da primeira execução da skill.
- **Alternatives considered**: instalação global/usuário (rejeitada na clarificação); Docker
  (fora do escopo e não exigido).

## R9. Linha de base de comportamento e comparação

- **Decision**:
  1. Inventário de endpoints na Fase 1 (método, path, origem `arquivo:linha`).
  2. Plano de requisições (Fase 3, arquivo temporário fora do repositório): usa exemplos do
     projeto (ex.: arquivos `.http`) quando existirem, senão deriva payloads válidos do código;
     ordem: leituras → criações → atualizações → remoções; IDs de rotas parametrizadas vêm dos
     dados de seed ou de criações anteriores.
  3. Estado inicial idêntico para as duas execuções (original e refatorada):
     `workspace-artifacts.sh snapshot` antes, `check-port.sh` (porta ocupada sem alternativa não
     invasiva = falha externa), passos de setup documentados (ex.: seed), boot em background
     guardando o PID, `wait-for-http.sh <url> <timeout> <pid>`, `probe-endpoints.sh`, parada,
     `diff` e remoção dos artefatos novos (exceto o ambiente isolado) — **após cada** execução.
  4. Todos os arquivos de trabalho (plano de requisições, corpos, respostas, snapshots) ficam em
     um diretório criado com `mktemp -d`, removido ao final da Fase 3 com sucesso ou falha.
  5. "Formato" = status HTTP + tipo do corpo + conjunto de chaves (recursivo em objetos; primeiro
     elemento em listas). Ignorados: valores, ids gerados, timestamps, ordem.
  6. Se o original não sobe, a referência é inferida do código e marcada `inferred`.
- **Rationale**: transforma "endpoints continuam respondendo" em comparação objetiva e
  reprodutível (clarificação Q3), sem depender de valores voláteis.
- **Alternatives considered**: comparação de corpo byte a byte (quebra com ids/timestamps);
  apenas status < 500 (fraco demais).

## R10. Endpoints que mudam por correção de segurança

- **Decision**: quando a correção de um finding CRITICAL de segurança altera o contrato (ex.:
  endpoint administrativo que executa SQL arbitrário, resposta que expõe senha), a rota é
  **mantida** e protegida/neutralizada (ex.: desabilitada por configuração ou campo sensível
  removido), e a divergência é declarada no resumo da Fase 3 e na evidência como
  `declared-security-change`; qualquer outra divergência é falha.
- **Rationale**: equilibra "endpoints originais respondem" (enunciado) com eliminar CRITICALs
  (zero anti-patterns).
- **Alternatives considered**: remover a rota (quebraria o inventário); manter o comportamento
  inseguro (violaria a reauditoria zero).

## R11. Catálogo de anti-patterns (seleção inicial)

- **Decision**: catálogo com 20 entradas (AP-01–AP-20, lista final em tasks.md T012), identificadores estáveis `AP-NN`, todas as severidades
  representadas; seleção guiada pelos sinais observados nos projetos e generalizada:

  | Severidade | Anti-patterns |
  |---|---|
  | CRITICAL | credenciais/segredos hardcoded; SQL injection por concatenação/interpolação; God class/arquivo (dados + regra + rota); endpoint administrativo/debug sem proteção que executa ações destrutivas ou consultas arbitrárias; armazenamento de senha em texto puro ou hash fraco |
  | HIGH | regra de negócio em rotas/controllers; estado global mutável; acoplamento sem injeção de dependência; exposição de dados sensíveis na resposta; modo debug/bind amplo em execução padrão |
  | MEDIUM | N+1 queries / query em laço; validação de entrada ausente; tratamento de erros espalhado/genérico; duplicação de código; **API deprecated** (ex.: `datetime.utcnow()`, `Query.get()` legado do SQLAlchemy, construtores/métodos obsoletos de Node); callbacks aninhados (callback hell) |
  | LOW | magic numbers/strings; nomes pobres/abreviados; `print`/`console.log` no lugar de logger; imports não usados/código morto |

- **Rationale**: cobre ≥ 8 com as 4 severidades e API deprecated (FR-035); sinais são concretos
  (ex.: "string SQL construída com `+`/f-string contendo variável de request"). Cada entrada
  aponta para ≥ 1 padrão do playbook (FR-037).
- **Alternatives considered**: catálogo mínimo de 8 (insuficiente para ≥ 5 findings no projeto 3
  e para a reauditoria zero).

## R12. Playbook e estrutura MVC alvo

- **Decision**: 18 padrões de transformação (TP-01–TP-18, lista final em tasks.md T022) com antes/depois em Python/Flask e
  Node/Express (ex.: extrair config para variáveis de ambiente; queries parametrizadas; dividir
  God class em model/controller/route; extrair regra de negócio para controller/service; injeção
  de dependência via composition root; error handler centralizado; eager loading/JOIN contra N+1;
  validação de entrada na borda; hashing de senha com biblioteca padrão/forte; substituir API
  deprecated; logger estruturado; constantes nomeadas; promessas/async no lugar de callbacks;
  proteger/desabilitar endpoints administrativos).
  Estrutura alvo default (adaptável): `config/`, `models/`, `views/` ou `routes/`,
  `controllers/`, `middlewares/` (error handler) e entry point/composition root, sob `src/` quando
  o projeto já usar `src/`; em projetos parcialmente organizados, renomear/realocar só o
  necessário e preservar o que já cumpre as regras.
- **Rationale**: exemplos em duas stacks provam agnosticismo; mapeamento por stack evita impor
  convenções de uma linguagem em outra.
- **Alternatives considered**: estrutura rígida única (quebraria imports/boot no projeto 3).

## R13. Idioma e formato das saídas

- **Decision**: banners e rótulos em inglês, como no enunciado (`PHASE 1: PROJECT ANALYSIS`,
  `ARCHITECTURE AUDIT REPORT`, `Proceed with refactoring (Phase 3)? [y/n]`,
  `PHASE 3: REFACTORING COMPLETE`, `PHASE 3: REFACTORING FAILED`); descrições, impactos e
  recomendações em português.
- **Rationale**: fidelidade ao exemplo do enunciado e legibilidade para o avaliador.

## R14. Verificação estática da skill (Gate G2) e registro de iterações

- **Decision**: verificações por comandos de shell documentados no quickstart (linhas do corpo do
  `SKILL.md`, tamanho da `description`, contagem de `AP-`/`TP-`, severidades, presença de
  antes/depois, ausência de identificadores dos projetos-alvo, ausência de blocos de script no
  Markdown, `diff -r` entre cópias). Registro de iterações em `docs/iteration-log.md`, resumido
  na seção "Desafios" do README.
- **Rationale**: gates objetivos e repetíveis a cada iteração, sem framework de testes.
