#!/bin/sh
# workspace-artifacts.sh — detecta arquivos e diretórios criados por uma execução da aplicação
# (bancos locais, caches de bytecode, uploads). Somente leitura em relação ao projeto.
#
# Uso:        workspace-artifacts.sh snapshot    <project-dir> <state-file>
#             workspace-artifacts.sh diff        <project-dir> <state-file>
#             workspace-artifacts.sh fingerprint <project-dir>
# Argumentos: snapshot  grava em <state-file> a lista atual de arquivos e diretórios do projeto
#                       (inclusive ignorados pelo git).
#             diff      imprime, um por linha, os caminhos que não existiam no snapshot. Quando um
#                       diretório inteiro é novo, só o diretório é impresso.
#             fingerprint imprime FINGERPRINT=<hash> do conteúdo de todos os arquivos não
#                       ignorados pelo git do projeto (rastreados e novos), fora de .claude/.
#                       Dois valores iguais provam que o código não mudou entre dois momentos.
#             <state-file> deve ficar em um diretório temporário fora do repositório.
# Exclusões:  .claude/ .git/ e diretórios de ambiente isolado de dependências
#             (.venv/ venv/ node_modules/), que nunca são artefatos de runtime.
# Depende de: find, sed, sort, comm, awk; git e cksum (fingerprint)
# Exit codes: 0 sucesso; 2 uso inválido; 3 dependência ausente ou erro de escrita.

set -u

usage() {
    echo "usage: workspace-artifacts.sh snapshot|diff <project-dir> <state-file> | fingerprint <project-dir>" >&2
    exit 2
}

[ $# -ge 2 ] || usage
MODE=$1
PROJECT=$2
STATE=${3:-}
if [ "$MODE" = "fingerprint" ]; then [ $# -eq 2 ] || usage; else [ $# -eq 3 ] || usage; fi
[ -d "$PROJECT" ] || { echo "error: '$PROJECT' is not a directory" >&2; exit 2; }
for dep in find sed sort comm awk; do
    command -v "$dep" >/dev/null 2>&1 || { echo "error: missing dependency: $dep" >&2; exit 3; }
done

list_paths() {
    (
        cd "$PROJECT" || exit 3
        find . \( -name .claude -o -name .git -o -name .venv -o -name venv -o -name node_modules \) -prune \
            -o -print
    ) | sed -e 's|^\./||' -e '/^\.$/d' | LC_ALL=C sort
}

case "$MODE" in
    snapshot)
        list_paths > "$STATE" || { echo "error: cannot write state file '$STATE'" >&2; exit 3; }
        ;;
    diff)
        [ -f "$STATE" ] || { echo "error: state file '$STATE' not found (run snapshot first)" >&2; exit 2; }
        TMP_CURRENT="$STATE.current"
        list_paths > "$TMP_CURRENT" || { echo "error: cannot write '$TMP_CURRENT'" >&2; exit 3; }
        LC_ALL=C comm -13 "$STATE" "$TMP_CURRENT" | awk '
            { for (i = 1; i <= n; i++) if (index($0, top[i] "/") == 1) next; top[++n] = $0; print }'
        rm -f "$TMP_CURRENT"
        ;;
    fingerprint)
        command -v git >/dev/null 2>&1 || { echo "error: missing dependency: git" >&2; exit 3; }
        command -v cksum >/dev/null 2>&1 || { echo "error: missing dependency: cksum" >&2; exit 3; }
        (
            cd "$PROJECT" || exit 3
            git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "error: '$PROJECT' is not inside a git repository" >&2; exit 2; }
            git ls-files -z --cached --others --exclude-standard -- . ':(exclude).claude' |
                tr '\0' '\n' | LC_ALL=C sort | while IFS= read -r f; do
                    [ -f "$f" ] || continue
                    printf '%s %s\n' "$(cksum < "$f" | awk '{ print $1 "-" $2 }')" "$f"
                done | cksum | awk '{ print "FINGERPRINT=" $1 "-" $2 }'
        ) || exit $?
        ;;
    *)
        usage
        ;;
esac
exit 0
