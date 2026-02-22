#!/usr/bin/env bash
set -euo pipefail

### CONFIG ############################################################

BASE_MINI="$HOME/mini_substation_automation"
BASE_SERVER="$HOME/iec61850_open_server"
BASE_GATEWAY="$HOME/iec61850_open_gateway"
BASE_CLIENT="$HOME/iec61850_open_client"

LOG_DIR="$(pwd)/logs"
PID_DIR="$(pwd)/pids"

TTY_A="/tmp/ttyV0"
TTY_B="/tmp/ttyV1"


#sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3.12 <- needs to be the binary, not the symlink /usr/bin/python3, else u get
#Invalid file '/usr/bin/python3' for capability operation
#check getcap /usr/bin/python3.10
PYTHON_BIN="$(readlink -f "$(command -v python3)")"

if ! getcap "$PYTHON_BIN" 2>/dev/null | grep -q cap_net_bind_service; then
    echo "ERROR: $PYTHON_BIN missing cap_net_bind_service"
    exit 1
fi

###############################################################################

log() {
    echo "[SYSTEM] $1"
}

start_bg() {
    local name="$1"
    shift
    log "Starting $name"
    "$@" >"$LOG_DIR/$name.log" 2>&1 &
    echo $! >"$PID_DIR/$name.pid"
}

wait_for_file() {
    local file="$1"
    for i in {1..20}; do
        [[ -e "$file" ]] && return 0
        sleep 0.2
    done
    echo "Timeout waiting for $file"
    exit 1
}

###############################################################################
log "===== SYSTEM TEST START ====="


###############################################################################
# 2️⃣ SOCAT (PTY PAIR)
###############################################################################
rm -f "$TTY_A" "$TTY_B"

start_bg socat \
    socat -d -d \
    PTY,link="$TTY_A",raw,echo=0 \
    PTY,link="$TTY_B",raw,echo=0

wait_for_file "$TTY_A"
wait_for_file "$TTY_B"
