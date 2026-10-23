#!/bin/sh
# count-source-files.sh — lista e conta os arquivos-fonte de um projeto (somente leitura).
#
# Uso:        count-source-files.sh <project-dir> [ext ...]
# Argumentos: <project-dir>  diretório do projeto (obrigatório).
#             [ext ...]      extensões sem ponto (ex.: py js). Se omitidas, o script detecta a
#                            família de linguagem predominante pelo número de arquivos.
# Saída:      FILES=<n>
#             LOC=<n>        (soma das linhas, contando a última linha sem quebra)
#             um caminho por linha, relativo ao projeto, em ordem alfabética.
# Exclusões:  diretórios .claude .git node_modules .venv venv __pycache__ vendor dist build.
#             Manifestos, lockfiles, documentação e exemplos de requisição ficam de fora porque
#             não têm extensão de código.
# Depende de: find, sed, awk, sort
# Exit codes: 0 sucesso; 2 uso inválido; 3 dependência ausente.

set -u

usage() {
    echo "usage: count-source-files.sh <project-dir> [ext ...]" >&2
    exit 2
}

[ $# -ge 1 ] || usage
PROJECT=$1
shift
[ -d "$PROJECT" ] || { echo "error: '$PROJECT' is not a directory" >&2; exit 2; }

for dep in find sed awk sort; do
    command -v "$dep" >/dev/null 2>&1 || { echo "error: missing dependency: $dep" >&2; exit 3; }
done

# Mapeamento extensão:família. Para suportar outra linguagem, acrescente pares aqui.
FAMILY_MAP="py:python js:javascript mjs:javascript cjs:javascript jsx:javascript ts:javascript tsx:javascript go:go java:jvm kt:jvm scala:jvm rb:ruby php:php cs:dotnet rs:rust"

list_files() {
    (
        cd "$PROJECT" || exit 3
        find . \( -name .claude -o -name .git -o -name node_modules -o -name .venv -o -name venv \
            -o -name __pycache__ -o -name vendor -o -name dist -o -name build \) -prune \
            -o -type f -print
    ) | sed 's|^\./||' | LC_ALL=C sort
}

ALL_FILES=$(list_files)

if [ $# -gt 0 ]; then
    EXTS=$*
else
    # Família predominante: a que tem mais arquivos; empate resolvido pela ordem alfabética.
    EXTS=$(printf '%s\n' "$ALL_FILES" | awk -v map="$FAMILY_MAP" '
        BEGIN { n = split(map, pairs, " "); for (i = 1; i <= n; i++) { split(pairs[i], kv, ":"); fam[kv[1]] = kv[2] } }
        {
            base = $0; sub(/.*\//, "", base)
            if (index(base, ".") == 0) next
            ext = base; sub(/.*\./, "", ext)
            if (ext in fam) count[fam[ext]]++
        }
        END {
            best = ""; max = 0
            for (f in count) if (count[f] > max || (count[f] == max && f < best)) { best = f; max = count[f] }
            if (best == "") exit
            out = ""
            for (e in fam) if (fam[e] == best) out = out " " e
            print out
        }')
fi

SELECTED=$(printf '%s\n' "$ALL_FILES" | awk -v exts="$EXTS" '
    BEGIN { n = split(exts, list, " "); for (i = 1; i <= n; i++) { e = list[i]; sub(/^\./, "", e); want[e] = 1 } }
    NF {
        base = $0; sub(/.*\//, "", base)
        if (index(base, ".") == 0) next
        ext = base; sub(/.*\./, "", ext)
        if (ext in want) print
    }')

FILES=0
LOC=0
if [ -n "$SELECTED" ]; then
    FILES=$(printf '%s\n' "$SELECTED" | awk 'NF { c++ } END { print c + 0 }')
    LOC=$(printf '%s\n' "$SELECTED" | (
        cd "$PROJECT" || exit 3
        total=0
        while IFS= read -r f; do
            [ -n "$f" ] || continue
            lines=$(awk 'END { print NR }' "$f")
            total=$((total + lines))
        done
        echo "$total"
    ))
fi

echo "FILES=$FILES"
echo "LOC=$LOC"
[ -n "$SELECTED" ] && printf '%s\n' "$SELECTED"
exit 0
