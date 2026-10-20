#!/bin/sh
# wait-for-http.sh — aguarda a aplicação iniciada responder HTTP (somente leitura).
#
# Uso:        wait-for-http.sh <url> [timeout-seconds] [pid]
# Argumentos: <url>              URL a consultar (ex.: http://127.0.0.1:8080/)
#             [timeout-seconds]  limite de espera; padrão 30 s (tempo típico de boot local de
#                                APIs pequenas, com folga).
#             [pid]              PID do processo iniciado. Se informado, o processo precisa estar
#                                vivo no momento da resposta; se morrer antes, a espera termina
#                                com READY=no (evita aceitar a resposta de outro processo).
# Regra:      qualquer resposta HTTP (inclusive 4xx/5xx) conta como "respondendo".
# Saída:      READY=yes e HTTP_STATUS=<code>; ou READY=no e REASON=timeout|process-exited
# Depende de: curl, sleep, kill
# Exit codes: 0 pronto; 1 não pronto; 2 uso inválido; 3 dependência ausente.

set -u

DEFAULT_TIMEOUT_SECONDS=30
POLL_INTERVAL_SECONDS=1
REQUEST_TIMEOUT_SECONDS=2

[ $# -ge 1 ] && [ $# -le 3 ] || { echo "usage: wait-for-http.sh <url> [timeout-seconds] [pid]" >&2; exit 2; }
URL=$1
TIMEOUT=${2:-$DEFAULT_TIMEOUT_SECONDS}
PID=${3:-}
case "$TIMEOUT" in ''|*[!0-9]*) echo "error: timeout must be numeric" >&2; exit 2 ;; esac
if [ -n "$PID" ]; then
    case "$PID" in *[!0-9]*) echo "error: pid must be numeric" >&2; exit 2 ;; esac
fi
command -v curl >/dev/null 2>&1 || { echo "error: missing dependency: curl" >&2; exit 3; }

process_alive() {
    [ -z "$PID" ] && return 0
    kill -0 "$PID" 2>/dev/null
}

ELAPSED=0
while [ "$ELAPSED" -le "$TIMEOUT" ]; do
    if ! process_alive; then
        echo "READY=no"
        echo "REASON=process-exited"
        exit 1
    fi
    CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time "$REQUEST_TIMEOUT_SECONDS" "$URL" </dev/null)
    if [ -n "$CODE" ] && [ "$CODE" != "000" ]; then
        if process_alive; then
            echo "READY=yes"
            echo "HTTP_STATUS=$CODE"
            exit 0
        fi
        echo "READY=no"
        echo "REASON=process-exited"
        exit 1
    fi
    sleep "$POLL_INTERVAL_SECONDS"
    ELAPSED=$((ELAPSED + POLL_INTERVAL_SECONDS))
done

echo "READY=no"
echo "REASON=timeout"
exit 1
