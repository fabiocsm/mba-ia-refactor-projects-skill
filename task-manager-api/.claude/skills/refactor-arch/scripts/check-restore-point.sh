#!/bin/sh
# check-restore-point.sh — verifica se o projeto tem ponto de restauração (somente leitura).
#
# Uso:        check-restore-point.sh <project-dir>
# Argumentos: <project-dir>  diretório do projeto (obrigatório).
# Saída:      GIT=yes|no
#             STATUS=ok|dirty|no-git
#             HEAD=<sha curto>|none
#             PENDING=<n>
#             PENDING_FILE=<linha do git status --porcelain>   (uma por arquivo pendente)
# Regra:      ponto de restauração = repositório git sem alterações pendentes (inclusive
#             arquivos não rastreados e não ignorados) dentro do projeto, fora de .claude/.
# Depende de: git
# Exit codes: 0 STATUS=ok; 1 STATUS=dirty ou no-git; 2 uso inválido; 3 dependência ausente.

set -u

[ $# -eq 1 ] || { echo "usage: check-restore-point.sh <project-dir>" >&2; exit 2; }
PROJECT=$1
[ -d "$PROJECT" ] || { echo "error: '$PROJECT' is not a directory" >&2; exit 2; }
command -v git >/dev/null 2>&1 || { echo "error: missing dependency: git" >&2; exit 3; }

cd "$PROJECT" || exit 2

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "GIT=no"
    echo "STATUS=no-git"
    echo "HEAD=none"
    echo "PENDING=0"
    exit 1
fi

HEAD_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo none)
PENDING_LIST=$(git status --porcelain --untracked-files=all -- . ':(exclude).claude')
if [ -n "$PENDING_LIST" ]; then
    PENDING=$(printf '%s\n' "$PENDING_LIST" | awk 'NF { c++ } END { print c + 0 }')
else
    PENDING=0
fi

echo "GIT=yes"
if [ "$HEAD_SHA" = "none" ]; then
    echo "STATUS=dirty"
    echo "HEAD=none"
    echo "PENDING=$PENDING"
    [ -n "$PENDING_LIST" ] && printf '%s\n' "$PENDING_LIST" | sed 's/^/PENDING_FILE=/'
    exit 1
fi

if [ "$PENDING" -eq 0 ]; then
    echo "STATUS=ok"
    echo "HEAD=$HEAD_SHA"
    echo "PENDING=0"
    exit 0
fi

echo "STATUS=dirty"
echo "HEAD=$HEAD_SHA"
echo "PENDING=$PENDING"
printf '%s\n' "$PENDING_LIST" | sed 's/^/PENDING_FILE=/'
exit 1
