#!/bin/bash
set -e

BRIDGE="br0"
NUM_INSTANCES=6
UPLINK=""

# 1. Create bridge if it doesn't exist
if ! ip link show $BRIDGE &>/dev/null; then
    ip link add name $BRIDGE type bridge
fi
ip link set $BRIDGE up
ip link set $BRIDGE type bridge stp_state 0
echo 0 | tee /sys/class/net/$BRIDGE/bridge/multicast_snooping

# 2. Attach uplink if not already a bridge member
if [ -n "$UPLINK" ]; then
    if [ "$(cat /sys/class/net/$UPLINK/master 2>/dev/null)" != "$BRIDGE" ]; then
        ip link set $UPLINK master $BRIDGE
    fi
    ip link set $UPLINK up
fi

# 3. Create veth pairs if they don't exist
for i in $(seq 1 $NUM_INSTANCES); do
    HOST_IF="veth${i}"
    PEER_IF="veth${i}p"

    if ! ip link show $HOST_IF &>/dev/null; then
        ip link add $HOST_IF type veth peer name $PEER_IF
        ip link set $HOST_IF master $BRIDGE
    fi

    ip link set $HOST_IF up
    ip link set $PEER_IF up
done

echo "Done."