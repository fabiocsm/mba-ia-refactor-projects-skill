#!/bin/sh
# resolve-output-path.sh — resolve o caminho do relatório de auditoria ou da evidência de
# validação na raiz do repositório (somente leitura; não cria arquivos nem pastas).
#
# Uso:        resolve-output-path.sh <audit|validation> <project-name> [N]
# Argumentos: <audit|validation>  tipo do arquivo: audit → reports/audit-project-N.md;
#                                  validation → evidence/validation-project-N.md
#             <project-name>      nome do diretório do projeto.
#             [N]                 número explícito (inteiro positivo).
# Resolução de N (nesta ordem):
#             1. argumento N;
#             2. arquivo existente da mesma pasta que pertence ao projeto — audit: linha
#                "Project: <project-name>"; validation: título
#                "# Validation Evidence — <project-name>" (reexecução sobrescreve);
#             3. maior N existente na pasta + 1 (1 se a pasta estiver vazia ou não existir).
# Raiz:       git rev-parse --show-toplevel; fora de um repositório, o diretório atual.
# Saída:      ROOT=<dir>, N=<n>, PATH_OUT=<arquivo>
# Depende de: git (opcional), awk, sed
# Exit codes: 0 sucesso; 2 uso inválido.

set -u

usage() {
    echo "usage: resolve-output-path.sh <audit|validation> <project-name> [N]" >&2
    exit 2
}

[ $# -ge 2 ] && [ $# -le 3 ] || usage
KIND=$1
NAME=$2
ARG_N=${3:-}

case "$KIND" in
    audit) DIR=reports; PREFIX=audit-project ;;
    validation) DIR=evidence; PREFIX=validation-project ;;
    *) usage ;;
esac
[ -n "$NAME" ] || usage
if [ -n "$ARG_N" ]; then
    case "$ARG_N" in
        *[!0-9]*) echo "error: N must be a positive integer" >&2; exit 2 ;;
    esac
    [ "$ARG_N" -ge 1 ] 2>/dev/null || { echo "error: N must be a positive integer" >&2; exit 2; }
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || ROOT=$(pwd)
[ -n "$ROOT" ] || ROOT=$(pwd)
TARGET_DIR="$ROOT/$DIR"

N=""
if [ -n "$ARG_N" ]; then
    N=$((ARG_N + 0))
else
    MAX=0
    if [ -d "$TARGET_DIR" ]; then
        for f in "$TARGET_DIR/$PREFIX"-*.md; do
            [ -f "$f" ] || continue
            num=$(printf '%s\n' "$f" | sed -n "s|.*/$PREFIX-\([0-9][0-9]*\)\.md\$|\1|p")
            [ -n "$num" ] || continue
            num=$((num + 0))
            [ "$num" -gt "$MAX" ] && MAX=$num
            if [ "$KIND" = "audit" ]; then
                owner=$(awk '/^Project:/ { sub(/^Project:[ \t]*/, ""); sub(/[ \t\r]+$/, ""); print; exit }' "$f")
            else
                owner=$(awk 'NR == 1 { sub(/^# Validation Evidence — /, ""); sub(/[ \t\r]+$/, ""); print; exit }' "$f")
            fi
            if [ "$owner" = "$NAME" ] && [ -z "$N" ]; then
                N=$num
            fi
        done
    fi
    [ -n "$N" ] || N=$((MAX + 1))
fi

echo "ROOT=$ROOT"
echo "N=$N"
echo "PATH_OUT=$TARGET_DIR/$PREFIX-$N.md"
exit 0
