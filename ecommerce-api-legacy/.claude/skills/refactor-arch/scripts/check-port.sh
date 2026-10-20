#!/bin/sh
# check-port.sh — verifica se uma porta TCP local está livre antes de iniciar a aplicação
# (somente leitura).
#
# Uso:        check-port.sh <host> <port>
# Argumentos: <host>  ex.: 127.0.0.1 ou localhost
#             <port>  número da porta (1–65535)
# Regra:      conexão recusada = porta livre. Qualquer outra situação (resposta HTTP, resposta
#             vazia, conexão aceita sem resposta) = porta ocupada.
# Saída:      PORT_FREE=yes|no
#             LISTENER_PIDS=<pids separados por espaço>  (só quando ocupada e lsof disponível)
# Depende de: curl; lsof (opcional, apenas para LISTENER_PIDS)
# Exit codes: 0 livre; 1 ocupada; 2 uso inválido; 3 dependência ausente ou host inválido.

set -u

# Tempo máximo (s) para uma tentativa de conexão; curto porque a porta é local.
CONNECT_TIMEOUT_SECONDS=2

[ $# -eq 2 ] || { echo "usage: check-port.sh <host> <port>" >&2; exit 2; }
HOST=$1
PORT=$2
case "$PORT" in
    ''|*[!0-9]*) echo "error: port must be numeric" >&2; exit 2 ;;
esac
{ [ "$PORT" -ge 1 ] && [ "$PORT" -le 65535 ]; } || { echo "error: port out of range" >&2; exit 2; }
command -v curl >/dev/null 2>&1 || { echo "error: missing dependency: curl" >&2; exit 3; }

curl -s -o /dev/null --max-time "$CONNECT_TIMEOUT_SECONDS" "http://$HOST:$PORT/" </dev/null
RC=$?

case "$RC" in
    7)
        echo "PORT_FREE=yes"
        exit 0
        ;;
    6)
        echo "error: cannot resolve host '$HOST'" >&2
        exit 3
        ;;
esac

echo "PORT_FREE=no"
if command -v lsof >/dev/null 2>&1; then
    PIDS=$(lsof -t -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | LC_ALL=C sort -u | tr '\n' ' ' | sed 's/ *$//')
    echo "LISTENER_PIDS=$PIDS"
fi
exit 1
