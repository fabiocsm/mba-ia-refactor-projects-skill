#!/bin/sh
# probe-endpoints.sh — executa um plano de requisições HTTP e grava status, tipo e corpo de cada
# resposta.
#
# Uso:        probe-endpoints.sh <base-url> <requests-file> <out-file>
# Argumentos: <base-url>       ex.: http://127.0.0.1:8080
#             <requests-file>  uma requisição por linha, campos separados por TAB:
#                                method<TAB>path<TAB>body-file-or-dash[<TAB>headers-file-or-dash]
#                              linhas vazias e iniciadas por # são ignoradas. body-file contém o
#                              corpo JSON; headers-file contém um cabeçalho "Nome: valor" por linha.
#             <out-file>       arquivo de saída (deve ficar no diretório temporário de trabalho).
# Saída:      no <out-file>, por requisição:
#                ### <#> <METHOD> <PATH>
#                STATUS=<code>          (000 = sem resposta)
#                CONTENT_TYPE=<tipo>
#                <corpo bruto>
#             no stdout: PROBED=<n> e OUT=<out-file>
# Depende de: curl
# Exit codes: 0 sucesso (mesmo com respostas 4xx/5xx); 2 uso inválido; 3 dependência ausente.

set -u

REQUEST_TIMEOUT_SECONDS=10

[ $# -eq 3 ] || { echo "usage: probe-endpoints.sh <base-url> <requests-file> <out-file>" >&2; exit 2; }
BASE=${1%/}
REQS=$2
OUT=$3
[ -f "$REQS" ] || { echo "error: requests file '$REQS' not found" >&2; exit 2; }
command -v curl >/dev/null 2>&1 || { echo "error: missing dependency: curl" >&2; exit 3; }

: > "$OUT" || { echo "error: cannot write '$OUT'" >&2; exit 3; }
BODY_TMP="$OUT.body.tmp"
TAB=$(printf '\t')
COUNT=0

while IFS="$TAB" read -r METHOD REQ_PATH BODY HEADERS || [ -n "${METHOD:-}" ]; do
    case "$METHOD" in ''|\#*) continue ;; esac
    COUNT=$((COUNT + 1))
    BODY=${BODY:--}
    HEADERS=${HEADERS:--}

    set -- -s -X "$METHOD" -o "$BODY_TMP" -w '%{http_code}\t%{content_type}' --max-time "$REQUEST_TIMEOUT_SECONDS"
    if [ "$BODY" != "-" ]; then
        [ -f "$BODY" ] || { echo "error: body file '$BODY' not found (request $COUNT)" >&2; exit 2; }
        set -- "$@" -H "Content-Type: application/json" --data-binary "@$BODY"
    fi
    if [ "$HEADERS" != "-" ]; then
        [ -f "$HEADERS" ] || { echo "error: headers file '$HEADERS' not found (request $COUNT)" >&2; exit 2; }
        while IFS= read -r H || [ -n "$H" ]; do
            [ -n "$H" ] && set -- "$@" -H "$H"
        done < "$HEADERS"
    fi

    : > "$BODY_TMP"
    META=$(curl "$@" "$BASE$REQ_PATH" </dev/null)
    STATUS=${META%%"$TAB"*}
    CTYPE=${META#*"$TAB"}
    [ -n "$STATUS" ] || STATUS=000

    {
        printf '### %s %s %s\n' "$COUNT" "$METHOD" "$REQ_PATH"
        printf 'STATUS=%s\n' "$STATUS"
        printf 'CONTENT_TYPE=%s\n' "$CTYPE"
        cat "$BODY_TMP"
        printf '\n\n'
    } >> "$OUT"
done < "$REQS"

rm -f "$BODY_TMP"
echo "PROBED=$COUNT"
echo "OUT=$OUT"
exit 0
