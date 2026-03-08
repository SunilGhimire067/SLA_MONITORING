#!/bin/sh
# Wait for a service to become available
# Usage: ./wait-for-it.sh host:port [-t timeout] [-- command args]

WAITFORIT_cmdname=${0##*/}
echoerr() { if [ "$WAITFORIT_QUIET" -ne 1 ]; then echo "$@" 1>&2; fi }

WAITFORIT_HOST=""
WAITFORIT_PORT=""
WAITFORIT_TIMEOUT=15
WAITFORIT_QUIET=0
WAITFORIT_CMD=""

while [ $# -gt 0 ]; do
    case "$1" in
        *:*)
            WAITFORIT_HOST=$(echo "$1" | cut -d: -f1)
            WAITFORIT_PORT=$(echo "$1" | cut -d: -f2)
            shift 1
            ;;
        -t)
            WAITFORIT_TIMEOUT="$2"
            shift 2
            ;;
        -q)
            WAITFORIT_QUIET=1
            shift 1
            ;;
        --)
            shift
            WAITFORIT_CMD="$@"
            break
            ;;
        *)
            echoerr "Unknown argument: $1"
            exit 1
            ;;
    esac
done

if [ -z "$WAITFORIT_HOST" ] || [ -z "$WAITFORIT_PORT" ]; then
    echoerr "Usage: $WAITFORIT_cmdname host:port [-t timeout] [-- command]"
    exit 1
fi

WAITFORIT_start_ts=$(date +%s)
while :; do
    nc -z "$WAITFORIT_HOST" "$WAITFORIT_PORT" > /dev/null 2>&1
    WAITFORIT_result=$?
    if [ $WAITFORIT_result -eq 0 ]; then
        WAITFORIT_end_ts=$(date +%s)
        echoerr "$WAITFORIT_HOST:$WAITFORIT_PORT is available after $((WAITFORIT_end_ts - WAITFORIT_start_ts)) seconds"
        break
    fi
    WAITFORIT_now_ts=$(date +%s)
    if [ $((WAITFORIT_now_ts - WAITFORIT_start_ts)) -ge "$WAITFORIT_TIMEOUT" ]; then
        echoerr "Timeout after ${WAITFORIT_TIMEOUT}s waiting for $WAITFORIT_HOST:$WAITFORIT_PORT"
        exit 1
    fi
    sleep 1
done

if [ -n "$WAITFORIT_CMD" ]; then
    exec $WAITFORIT_CMD
fi
