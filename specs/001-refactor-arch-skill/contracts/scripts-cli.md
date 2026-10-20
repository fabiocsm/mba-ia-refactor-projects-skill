# Contract: interface dos scripts (`.claude/skills/refactor-arch/scripts/`)

Regras comuns (constituição, Princípio V):

- `#!/bin/sh` POSIX; cabeçalho com uso, argumentos, dependências (`git`, `curl`, `find`, `grep`,
  `sed`, `awk`) e códigos de saída.
- Nenhum valor específico de projeto/stack embutido; tudo por argumento ou detecção.
- Não instalam pacotes. Saída em linhas `KEY=VALUE` (ou formato tabulado declarado), erros em
  stderr com mensagem clara.
- Exit codes: `0` sucesso; `1` condição negativa esperada (ex.: repo sujo); `2` uso inválido;
  `3` dependência ausente/erro de ambiente.
- Invocados como `"${CLAUDE_SKILL_DIR}/scripts/<nome>.sh" …`; cada um tem procedimento manual
  equivalente no `SKILL.md`.

| Script | Args | Saída (stdout) | Efeito |
|---|---|---|---|
| `count-source-files.sh` | `<project-dir> [ext ...]` | `FILES=<n>`, `LOC=<n>`, depois um caminho por linha | leitura |
| `check-restore-point.sh` | `<project-dir>` | `GIT=yes\|no`, `STATUS=ok\|dirty\|no-git`, `HEAD=<sha>`, `PENDING=<n>` + arquivos | leitura |
| `resolve-output-path.sh` | `<audit\|validation> <project-name> [N]` | `ROOT=<dir>`, `N=<n>`, `PATH_OUT=<arquivo>` | leitura |
| `workspace-artifacts.sh` | `snapshot <project-dir> <state-file>` \| `diff <project-dir> <state-file>` \| `fingerprint <project-dir>` | `diff`: um caminho novo por linha (exclui `.claude/` e o ambiente isolado); `fingerprint`: `FINGERPRINT=<hash>` do conteúdo dos arquivos não ignorados fora de `.claude/` | leitura (state-file em diretório temporário) |
| `check-port.sh` | `<host> <port>` | `PORT_FREE=yes` (exit 0) ou `PORT_FREE=no` (exit 1) + `LISTENER_PIDS=<pids>` quando `lsof` existe — usa `curl` (conexão recusada = livre) | leitura |
| `wait-for-http.sh` | `<url> [timeout-seconds] [pid]` | `READY=yes` (exit 0); `READY=no` (exit 1) por timeout ou se o `pid` informado morrer antes de responder | leitura |
| `probe-endpoints.sh` | `<base-url> <requests-file> <out-file>` | `out-file`: por requisição, bloco `### <#> <METHOD> <PATH>`, `STATUS=<code>`, `CONTENT_TYPE=<tipo>`, corpo bruto; stdout `PROBED=<n>`, `OUT=<arquivo>` | requisições HTTP locais |
| `revert-project.sh` | `<project-dir>` | `REVERTED=yes`, `HEAD=<sha>` | destrutivo, restrito ao projeto; exclui `.claude/`; não remove arquivos ignorados |

## Formato de `requests-file`

```text
# method<TAB>path<TAB>body-file-or-dash[<TAB>headers-file-or-dash]
GET	/items	-
POST	/items	/tmp/refactor-arch.XXXX/body-03.json
GET	/admin/stats	-	/tmp/refactor-arch.XXXX/headers-admin.txt
```

A 4ª coluna (opcional) aponta para um arquivo com um cabeçalho `Nome: valor` por linha — usada
para exercitar endpoints protegidos por credencial após uma correção de segurança declarada.

Corpos, respostas e state-files ficam no mesmo diretório temporário do SO (`mktemp -d`, fora do
repositório), removido pela skill ao final da Fase 3 com sucesso ou falha.

## Testes de contrato (Gate G2)

Cada script é executado contra os 3 projetos (Python e Node) cobrindo: caminho feliz, argumento
inválido (exit 2), condição negativa (exit 1) e, para `revert-project.sh`, prova de que
`.claude/` e arquivos ignorados permanecem.
