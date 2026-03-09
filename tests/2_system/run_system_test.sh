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

# create unix socket directory
if [ ! -d /run/iec61850_ui ]; then
    sudo mkdir -p /run/iec61850_ui
    sudo chmod 777 /run/iec61850_ui
fi

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

sleep 1

###############################################################################
# 1️⃣ SERIAL MOCK
###############################################################################
start_bg serial_mock \
    python3 -u "$BASE_MINI/tests/0_unit/rly01/serial_mock.py"


###############################################################################
# 3️⃣ SERIAL SERVICE
###############################################################################
start_bg serial_service \
    python3 -u "$BASE_MINI/software/rly01/service.py" -d

sleep 15
###############################################################################
# 4️⃣ UI SERVICE
###############################################################################
start_bg ui_service \
    python3 -u "$BASE_MINI/software/rly01/relay_ui/relay_320x480.py"

###############################################################################
# 5️⃣ MODBUS SIMULATOR
###############################################################################
start_bg modbus_sim \
    python3 -u "$BASE_MINI/tests/1_integration/test_modbus.py"

###############################################################################
# 6️⃣ IEC 61850 OPEN SERVERS
###############################################################################
(
    cd "$BASE_SERVER"
    ./open_server lo 2102 cfg/FEED1.cfg cfg/FEED1.ext L 65000 &
    ./open_server lo 3102 cfg/FEED2.cfg cfg/FEED2.ext L 65001 &
    ./open_server lo 4102 cfg/BUS1.cfg  cfg/BUS1.ext  L 65002 &
    ./open_server lo 5102 cfg/BUS2.cfg  cfg/BUS2.ext  L 65003 &
    ./open_server lo 6102 cfg/TR1.cfg   cfg/TR1.ext   L 65004 &
    ./open_server lo 7102 cfg/TR2.cfg   cfg/TR2.ext   L 65005
) >"$LOG_DIR/iec61850_servers.log" 2>&1 &
echo $! >"$PID_DIR/iec61850_servers.pid"

sleep 5

###############################################################################
# 7️⃣ IEC 61850 GATEWAY (venv)
###############################################################################
start_bg gateway \
    bash -c "
        cd '$BASE_GATEWAY'
        source .venv/bin/activate
        exec python3 -u app.py
    "

###############################################################################
# 8️⃣ IEC 61850 CLIENT (venv)
###############################################################################
start_bg client \
    bash -c "
        cd '$BASE_CLIENT'
        source .venv/bin/activate
        exec python3 -u app.py
    "

###############################################################################
log "===== ALL SERVICES STARTED ====="
log "Logs: $LOG_DIR"
log "PIDs: $PID_DIR"
log "Use ./stop_system_test.sh to stop everything"

tail -f "$LOG_DIR/"*.log