#!/bin/bash
set -e

BRIDGE="br0"
NUM_INSTANCES=6
UPLINK="eth0"

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
IPS=(20 21 30 31 40 41)

for i in $(seq 1 $NUM_INSTANCES); do
    HOST_IF="veth${i}"
    PEER_IF="veth${i}p"

    IP="172.16.1.${IPS[$((i-1))]}"

    # Generate deterministic MACs
    MAC_HOST=$(printf "02:00:00:00:%02x:%02x" 0 $i)
    MAC_PEER=$(printf "02:00:00:01:%02x:%02x" 0 $i)

    if ! ip link show $HOST_IF &>/dev/null; then
        ip link add $HOST_IF type veth peer name $PEER_IF
        ip link set $HOST_IF master $BRIDGE
    fi

    # Set MAC addresses (always enforce)
    ip link set dev $HOST_IF address $MAC_HOST
    ip link set dev $PEER_IF address $MAC_PEER

    ip link set $HOST_IF up
    ip link set $PEER_IF up

    # Assign IP (idempotent)
    ip addr replace ${IP}/24 dev $PEER_IF
done

echo "Done."