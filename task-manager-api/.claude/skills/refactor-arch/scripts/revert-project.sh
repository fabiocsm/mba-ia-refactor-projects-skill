#!/bin/sh
# revert-project.sh — devolve o projeto ao ponto de restauração (HEAD). DESTRUTIVO: executar
# somente após falha da Fase 3 e confirmação explícita do usuário.
#
# Uso:        revert-project.sh <project-dir>
# Argumentos: <project-dir>  diretório do projeto (obrigatório; precisa estar em um repositório git).
# Efeito:     no diretório do projeto, restaura arquivos rastreados (index e working tree) a partir
#             de HEAD e remove arquivos não rastreados e não ignorados. Escopo restrito ao projeto.
# Preserva:   .claude/ (a skill), arquivos ignorados pelo git (ambiente isolado de dependências)
#             e tudo fora do diretório do projeto (reports/, evidence/).
# Saída:      REVERTED=yes e HEAD=<sha curto>
# Depende de: git, find, sort
# Exit codes: 0 revertido; 2 uso inválido ou diretório fora de um repositório git;
#             3 dependência ausente ou falha do git.

set -u

[ $# -eq 1 ] || { echo "usage: revert-project.sh <project-dir>" >&2; exit 2; }
PROJECT=$1
[ -d "$PROJECT" ] || { echo "error: '$PROJECT' is not a directory" >&2; exit 2; }
command -v git >/dev/null 2>&1 || { echo "error: missing dependency: git" >&2; exit 3; }

cd "$PROJECT" || exit 2
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "error: '$PROJECT' is not inside a git repository" >&2; exit 2; }
git rev-parse --verify -q HEAD >/dev/null || { echo "error: repository has no commits (no restore point)" >&2; exit 2; }

git restore --source=HEAD --staged --worktree -- . ':(exclude).claude' || { echo "error: git restore failed" >&2; exit 3; }
git clean -fd -q -- . ':(exclude).claude' || { echo "error: git clean failed" >&2; exit 3; }
# Diretórios que ficaram vazios (ex.: continham só caches ignorados já removidos) não pertencem ao
# ponto de restauração; remove-os, sem tocar em .git/, .claude/ nem no ambiente isolado.
find . -mindepth 1 \( -name .git -o -name .claude -o -name .venv -o -name venv -o -name node_modules \) -prune \
    -o -type d -empty -print | sort -r | while IFS= read -r d; do rmdir "$d" 2>/dev/null; done

echo "REVERTED=yes"
echo "HEAD=$(git rev-parse --short HEAD)"
exit 0
