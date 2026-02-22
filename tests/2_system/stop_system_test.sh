#!/usr/bin/env bash
set -e

PID_DIR="$(pwd)/pids"

echo "[SYSTEM] Stopping services..."

for pidfile in "$PID_DIR"/*.pid; do
    [[ -e "$pidfile" ]] || continue
    pid=$(cat "$pidfile")
    kill "$pid" 2>/dev/null || true
done

sleep 1
pkill socat || true

echo "[SYSTEM] Done."