# Protocolo de Validação

Referência complementar da Fase 3: ambiente isolado, linha de base de comportamento, execução da
aplicação, comparação de endpoints, reauditoria, evidência e fluxo de falha. Instruções de
**baixa liberdade**: siga a ordem e os formatos exatamente.

## Sumário

- [1. Pré-condições e diretório de trabalho](#1-pré-condições-e-diretório-de-trabalho)
- [2. Ambiente isolado de dependências](#2-ambiente-isolado-de-dependências)
- [3. Plano de requisições](#3-plano-de-requisições)
- [4. Procedimento de execução da aplicação](#4-procedimento-de-execução-da-aplicação)
- [5. Linha de base de comportamento](#5-linha-de-base-de-comportamento)
- [6. Formato de resposta e comparação](#6-formato-de-resposta-e-comparação)
- [7. Validação pós-refatoração](#7-validação-pós-refatoração) — 7.1 autorrevisão, 7.2 validação de tentativa única
- [8. Reauditoria](#8-reauditoria)
- [9. Evidência](#9-evidência)
- [10. Fluxo de falha](#10-fluxo-de-falha)
- [11. Encerramento](#11-encerramento)

## 1. Pré-condições e diretório de trabalho

1. Reexecute `check-restore-point.sh <projeto>`; exige `STATUS=ok`. Guarde `HEAD` como ponto de
   restauração.
2. Crie o diretório de trabalho fora do repositório: `mktemp -d` (guarde o caminho como `WORK`).
   **Todos** os arquivos efêmeros — plano de requisições, corpos, cabeçalhos, respostas,
   snapshots, logs de boot — ficam em `WORK`. Nada efêmero é criado no repositório.
3. Registre a versão da skill: commit mais recente que alterou a pasta da skill
   (`git log -1 --format=%h -- .claude/skills/refactor-arch` executado no projeto); se
   `git status --porcelain -- .claude/skills/refactor-arch` não estiver vazio, acrescente
   `+uncommitted`.
4. Registre data e hora (`AAAA-MM-DD HH:MM`).

## 2. Ambiente isolado de dependências

1. Escolha o caminho padrão da stack dentro do projeto: Python `.venv/`; Node `node_modules/`;
   outras stacks, o diretório local equivalente (ex.: `vendor/bundle`).
2. Antes de criar, confirme que é ignorado: `git check-ignore -q <caminho>` (exit 0). Se não for
   ignorado, pare com falha **external** (orientação: adicionar o caminho ao `.gitignore`).
3. Se já existir, **reutilize** (`reused`). Caso contrário (`created`):
   Python `python3 -m venv .venv` e `.venv/bin/pip install -r <manifesto>`;
   Node `npm ci` (com lockfile) ou `npm install`.
4. Nunca instale no ambiente global/do usuário. Falha de instalação = falha **external**.
5. Execute código Python sempre com `PYTHONDONTWRITEBYTECODE=1` (evita caches de bytecode no
   projeto).

## 3. Plano de requisições

Monte o plano a partir do inventário de endpoints da Fase 1, em `WORK/requests.tsv`, no formato
do `probe-endpoints.sh` (`method<TAB>path<TAB>body-file-or-dash[<TAB>headers-file-or-dash]`):

1. **Cobertura:** pelo menos uma requisição por endpoint inventariado.
2. **Fonte dos dados:** use exemplos do próprio projeto quando existirem (arquivos `.http`,
   coleções, README); senão derive do código payloads **válidos** que o handler aceita.
   Inclua os exemplos de cenários de negócio documentados no projeto (ex.: um exemplo de
   operação recusada) quando o original os responde sem erro 5xx.
3. **Sem entradas que derrubam o original:** não inclua requisições que, pelo código, levam o
   original a 5xx por entrada inválida — essas respostas não fazem parte do contrato.
4. **Ordem:** `read` → `create` → `update` → `delete` → `admin` (efeitos globais por último).
5. **IDs:** leituras e atualizações usam ids dos dados iniciais (seed); remoções usam,
   preferencialmente, recursos criados antes no próprio plano (id previsto a partir do estado
   inicial). Depois da captura da linha de base, confira nas respostas de criação que os ids
   previstos se confirmaram; se não, ajuste o plano e recapture a linha de base (permitido:
   nada foi modificado ainda).
6. Corpos JSON em `WORK/body-<n>.json`. Nenhuma senha/segredo real: use valores de exemplo.

## 4. Procedimento de execução da aplicação

Use este procedimento **idêntico** para a aplicação original (linha de base) e para a refatorada
(validação). `SNAP`, `LOG` e `OUT` são arquivos em `WORK` com sufixo `baseline` ou `after`.

1. **Snapshot:** `workspace-artifacts.sh snapshot <projeto> <SNAP>`.
2. **Porta:** determine host/porta de boot (literal no código ou variável de ambiente que a
   aplicação já suporta). Execute `check-port.sh 127.0.0.1 <porta>`.
   - `PORT_FREE=yes` → siga.
   - `PORT_FREE=no` → só use outra porta se a aplicação **já** aceitar porta por variável de
     ambiente ou opção de linha de comando do framework, sem editar código; senão pare com
     falha **external** (`Skill gap: n/a (external): liberar a porta <porta> — <processo>`).
3. **Setup:** execute os passos de setup documentados (ex.: script de seed), no ambiente isolado,
   com as mesmas variáveis de ambiente do boot.
4. **Boot em background:** inicie com o comando documentado (ex.: `.venv/bin/python <entrada>`,
   `npm start`), redirecionando stdout/stderr para `LOG`, e guarde o PID. Para a aplicação
   refatorada, passe as variáveis de ambiente necessárias apenas na linha de comando (ex.:
   `ADMIN_TOKEN=<valor gerado na execução>`); nunca grave `.env`.
5. **Aguardar:** `wait-for-http.sh http://127.0.0.1:<porta><path-de-leitura> 30 <PID>`.
   `READY=no` → boot falhou (registre as últimas linhas de `LOG`).
6. **Exercitar:** `probe-endpoints.sh http://127.0.0.1:<porta> WORK/requests.tsv <OUT>`
   (na validação, o plano com cabeçalhos — §7).
7. **Parar:** encerre o processo e seus filhos — `pkill -TERM -P <PID>` seguido de
   `kill -TERM <PID>`; aguarde ~1 s e execute `check-port.sh` de novo. Se ainda estiver ocupada,
   os `LISTENER_PIDS` pertencem a esta execução (a porta estava livre antes do boot): encerre-os
   e confirme `PORT_FREE=yes`.
8. **Artefatos de runtime:** `workspace-artifacts.sh diff <projeto> <SNAP>`; remova cada caminho
   listado (`rm -rf -- <projeto>/<caminho>`) e registre a lista. Remova **apenas** os caminhos
   listados.
9. **Conferir:** para a linha de base, `git status --porcelain -- .` no projeto deve continuar
   vazio (fora de `.claude/`).

## 5. Linha de base de comportamento

Executada **depois** da confirmação e **antes** de qualquer modificação — sobre o código exatamente
como está no ponto de restauração. Nunca capture a linha de base depois de começar a refatorar
nem recupere o original com comandos git (`stash`, `switch`, `restore`); se isso acontecer, a execução
falhou (§10):

1. Ambiente isolado (§2), plano (§3) e procedimento de execução (§4) com a aplicação original.
2. Para cada requisição de `OUT`, registre `status` e `shape` (§6).
3. `Source: captured`. Se o original não iniciar (boot falhou, sem relação com porta ocupada),
   construa a linha de base lendo o código (status e chaves que cada handler devolve) e marque
   `Source: inferred (<motivo>)`.

## 6. Formato de resposta e comparação

**Shape** de uma resposta = `status` + tipo do corpo + chaves:

| Corpo | Shape |
|---|---|
| JSON objeto | `{chave1,chave2,...}` em ordem alfabética; valores objeto/lista viram shape aninhado (`{a,b:{c,d},e:list<{f}>}`) |
| JSON lista | `list<shape do primeiro elemento>`; lista vazia = `list<>` |
| JSON escalar | `number`, `string`, `boolean`, `null` |
| Texto não JSON | `text` |
| Vazio | `empty` |

Ignorados na comparação: valores, ids gerados, timestamps, ordem de elementos e de chaves.
Tipos escalares de valores não são comparados (só a presença das chaves).

Resultado por endpoint (todas as requisições do endpoint):

| Match | Quando |
|---|---|
| `✓` | mesmo status e mesmo shape em todas as requisições |
| `declared` | divergência que é exatamente uma mudança de contrato declarada (correção de segurança: campo sensível removido, endpoint administrativo protegido/desabilitado) |
| `✗` | qualquer outra divergência — inclusive lista vazia onde a linha de base tinha itens e vice-versa, quando isso muda o shape |

## 7. Validação pós-refatoração

### 7.1 Autorrevisão obrigatória (antes da validação — correções permitidas)

Ainda dentro da etapa de refatoração, antes de iniciar a aplicação refatorada pela primeira vez:

1. **Pré-reauditoria completa:** execute os passos 1–5 de §8 (leitura arquivo por arquivo com a
   ferramenta de leitura, registro em `WORK/self-review.md`), exatamente como na reauditoria
   oficial. Duplicações entre funções novas (validadores, mapeadores) contam.
2. **Conferência de contrato por leitura de código:** para cada endpoint do inventário, compare
   status e chaves que o novo handler devolve com o shape da linha de base. Toda diferença precisa
   ser uma mudança declarada (correção de segurança) — senão, corrija o código para devolver
   exatamente o shape original.
3. **Verificação sintática sem executar a aplicação e sem gravar caches:** Python
   `.venv/bin/python -c "import sys; [compile(open(p, encoding='utf-8').read(), p, 'exec') for p in sys.argv[1:]]" <arquivos>`
   (não use `py_compile`, que grava `.pyc`); Node `node --check <arquivo>`.
4. Corrija tudo o que encontrar e repita 1–3 até não restar nada. Só então siga para §7.2.

### 7.2 Validação (uma única tentativa — nenhuma correção)

1. **Fingerprint inicial:** `workspace-artifacts.sh fingerprint <projeto>` → guarde como
   `FP_START`. A validação começa aqui.
2. **Regra de tentativa única:** daqui em diante é proibido alterar qualquer arquivo do projeto e
   proibido reiniciar a validação. Não existe "refazer a validação depois de corrigir": se
   qualquer verificação falhar — ou se você perceber algo que precisaria corrigir —, o resultado
   é **FAILED** (§10). A aplicação refatorada é iniciada **uma única vez**.
3. Endpoints protegidos por TP-14: gere um token aleatório para a execução (ex.:
   `openssl rand -hex 16`), passe-o no boot (`ADMIN_TOKEN=<token>`) e crie
   `WORK/headers-admin.txt` com `X-Admin-Token: <token>` (ou o cabeçalho definido no código);
   esses endpoints usam a 4ª coluna do plano. Os demais campos do plano são idênticos aos da linha
   de base.
4. Execute o procedimento §4 com a aplicação refatorada (mesmo setup, mesmo estado inicial).
5. Verificações, todas obrigatórias:
   - **(a) Boot:** `READY=yes`, processo vivo e sem traceback/erro no `LOG` até o fim do probe.
   - **(b) Endpoints:** compare cada endpoint com a linha de base (§6). Todo endpoint `✓` ou
     `declared`; nenhum `✗`.
   - **(c) Reauditoria:** §8 com zero findings.
   - **(d) Integridade:** `workspace-artifacts.sh fingerprint <projeto>` ao final é igual a
     `FP_START` (prova de que nada foi alterado durante a validação). Diferente = FAILED
     (`skill`).

## 8. Reauditoria

A reauditoria oficial é a verificação (c) da validação: uma **nova leitura completa**, feita
depois do probe e antes do fingerprint final. Não reaproveite o resultado da autorrevisão (§7.1).

1. Rode `count-source-files.sh <projeto>` para a nova lista de arquivos-fonte.
2. Abra **cada** arquivo da lista com a ferramenta de leitura de arquivos (não substitua por
   `grep`: buscas ajudam a confirmar, mas não substituem a leitura) e aplique o catálogo completo
   (`anti-patterns-catalog.md`) com os mesmos sinais e falsos positivos da Fase 2.
3. **Rastreabilidade dos findings originais:** para cada localização de cada finding do
   relatório da Fase 2, identifique para onde aquele código foi e confirme que o sinal
   desapareceu (não basta ter criado a camada: o trecho específico precisa estar corrigido).
4. **Rastreamento de dados do request:** em cada handler/controller/validador, siga cada campo do
   request (inclusive campos de elementos de listas) até o primeiro uso em comparação,
   aritmética, `len()`, consulta ou persistência e confirme a verificação de tipo antes; em cada
   laço, confirme que nenhuma chamada dentro dele executa consulta (direta ou via model).
5. Registre em `WORK/reaudit.md` uma linha por arquivo: `<arquivo> — lido — <findings ou none>`.
   O número de linhas deve ser igual a `FILES`. Atenção especial a sinais que costumam sobrar
   em código novo: comparações/aritmética com campos do request sem verificação de tipo
   (AP-12), blocos repetidos entre funções novas (AP-14), literais de regra fora das constantes
   (AP-17).
6. Resultado: `Remaining anti-patterns: 0` ou a lista `[SEV] <nome> (AP-NN) — <arquivo:linha>`.
   Qualquer item = FAILED.

## 9. Evidência

Resolva o caminho com `resolve-output-path.sh validation <nome-do-diretório> <N do relatório>` e
grave o arquivo (sucesso **e** falha; reexecução sobrescreve). Formato exato:

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
- Dependency environment: <caminho local> (reused \| created)
- Setup steps: <passos executados ou "none">
- Boot command: `<comando>`
- Port: <porta> (free before boot: yes)
- Runtime artifacts removed: <lista ou "none">
- Code fingerprint: <FP_START> at first boot / <FP_END> at end (unchanged: yes \| no)

## Boot
```text
<trecho relevante do LOG da aplicação refatorada, ≤ 30 linhas>
```

## Behavior baseline
Source: captured \| inferred (<motivo>)

| # | Method | Path | Baseline status | Baseline shape | After status | After shape | Match |
|---|---|---|---|---|---|---|---|
| 1 | GET | /... | 200 | {data:list<{id,title}>} | 200 | {data:list<{id,title}>} | ✓ |

## Declared contract changes
| Endpoint | Change | Finding fixed |
|---|---|---|
| <METHOD path> | <mudança> | AP-NN |

## Re-audit
Remaining anti-patterns: 0 \| <lista>

## Diagnosis (FAILED only)
- Failed check: <...>
- Error: <...>
- Origin: <TP-NN / references/...>
- Probable skill gap: <...>
~~~

Regras: uma linha por endpoint do inventário (contagem = `Endpoints` da Fase 1); requisições
múltiplas do mesmo endpoint aparecem na mesma linha (`200, 400`); `declared` exige linha
correspondente em "Declared contract changes" que enumere **todas** as chaves/status que diferem
da linha de base (uma chave removida e não listada torna o endpoint `✗`); sem mudanças, uma linha
`none`; em `CLEAN`, omita
a seção Diagnosis; em falha antes da validação (ex.: boot da linha de base sem porta livre),
preencha o que foi executado e marque o resto como `not executed`.

## 10. Fluxo de falha

Qualquer verificação que falhe — ou erro na refatoração, porta ocupada, instalação impossível:

1. **Não remende** o código para passar. Pare as verificações restantes (encerre processos — §4.7
   — e remova artefatos de runtime — §4.8).
2. Classifique: `external` (porta ocupada, runtime ausente, instalação de dependências, rede) ou
   `skill` (qualquer outra causa).
3. Diagnostique: verificação que falhou, erro observado (status, trecho de log, finding
   remanescente), origem (`TP-NN` / arquivo de referência que guiou a mudança, ou `environment`)
   e a lacuna provável na skill (ou a orientação de correção do ambiente).
4. Grave a evidência com `Result: FAILED` (§9).
5. Imprima o banner `PHASE 3: REFACTORING FAILED` (formato no `SKILL.md`) e pergunte
   `Revert project to the restore point? [y/n]`.
6. Somente após `y`/`yes`/`s`/`sim`: `revert-project.sh <projeto>`; confirme
   `git status --porcelain -- .` vazio fora de `.claude/` e imprima
   `Project reverted to restore point (<commit curto>). .claude/, reports/, evidence/ and the dependency environment were preserved.`
   Qualquer outra resposta: `Changes kept for inspection. Revert before re-running the skill.`

## 11. Encerramento

- Confirme que nenhum processo iniciado pela execução continua rodando (`check-port.sh` livre).
- Remova `WORK` (`rm -rf -- <WORK>`), com sucesso ou falha.
- Confirme que nada foi gravado fora do projeto além da evidência (o relatório foi gravado na
  Fase 2) e que `.claude/` e `reports/` não foram alterados.
