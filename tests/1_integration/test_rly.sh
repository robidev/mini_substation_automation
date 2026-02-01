#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/home/user/mini_substation_automation"
pids=()

start_service() {
  local name="$1"
  shift

  # Create a pipe
  local fifo
  fifo=$(mktemp -u)
  mkfifo "$fifo"

  # Start the service, send stdout+stderr into the pipe
  "$@" >"$fifo" 2>&1 &
  local pid=$!
  pids+=("$pid")

  # Logger process that prefixes output
  {
    while IFS= read -r line; do
      printf '%s[%d]: %s\n' "$name" "$pid" "$line"
    done <"$fifo"
    rm -f "$fifo"
  } &
}

cleanup() {
  for pid in "${pids[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}

trap cleanup EXIT INT TERM HUP

# --- Start services ---

# socat (silent)
socat PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0 \
  >/dev/null 2>&1 &
pids+=("$!")

start_service "serial_mock" python3 -u "$WORKDIR/tests/0_unit/rly01/serial_mock.py"
start_service "service"     python3 -u "$WORKDIR/software/rly01/service.py"

echo "All services started..."

wait

