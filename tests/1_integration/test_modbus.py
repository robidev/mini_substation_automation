#!/usr/bin/env python3
"""
Modbus Slave Simulator — 10 RTU devices behind 1 TCP connection.
Each device is a relay_device struct mapped to Input/Holding registers.

Usage:
    pip install pymodbus
    python modbus_slave_sim.py [--host 0.0.0.0] [--port 502]

Register map:
    Holding (4xxxx / FC3/FC6/FC16):
        40001  Breaker Control  RW  0=No action, 1=Open, 2=Close
        40002  Trip Reset       RW  0=No action, 1=Reset
        40004  Local/Remote     RW  0=Local, 1=Remote (ignored if Local)

    Input (3xxxx / FC4):
        30001  Breaker State    0=OPEN, 1=CLOSED, 2=TRIPPED
        30002  Trip Status      0=OK, 1=TRIPPED
        30003  Fault Status     0=None, 1=FAULT
        30004  Local/Remote     0=Local, 1=Remote
        30005  DeviceType       0=infeed, 1=measure, 2=outfeed
        30006  Device index     0-9
        30010-30013  IA IB IC In
        30020-30023  VA VB VC Vn
        30030  Last Trip Type   0=None,1=Phase OC,2=Earth Fault
        30031  Last Trip Time
        30040  PIOC Pickup current
        30041  PTOC Pickup current
        30042  PTOC TMS

Access example:
    mbpoll -m tcp -a 1 -t 3 -0 -r 0 -c 50 127.0.0.1
"""

import argparse
import enum
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from typing import List

from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSparseDataBlock
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Device model
# ---------------------------------------------------------------------------

class DeviceType(enum.IntEnum):
    INFEED  = 0
    MEASURE = 1
    OUTFEED = 2

class FaultEvent(enum.IntEnum):
    NONE       = 0
    PHASE_OC   = 1
    EARTH_FAULT= 2

# Breaker state constants
BS_OPEN   = 1
BS_CLOSED = 2
BS_INTERMEDIATE= 0

@dataclass
class RelayDevice:
    index: int
    deviceType: DeviceType = DeviceType.INFEED
    breakerState: bool = True   # True=Closed
    tripState:    bool = False
    faultState:   bool = False
    faultEvent:   FaultEvent = FaultEvent.NONE
    faultTime:    int  = 0
    Measurement:  List[int] = field(default_factory=lambda: [0]*4)  # IA IB IC In or VA..Vn
    PTOC_Timer:   List[int] = field(default_factory=lambda: [0]*4)
    remote:       bool = True
    PTOC_setting_pickup_current: int = 1000
    PTOC_setting_time_multiplier: int = 10
    PIOC_setting_pickup_current: int = 5000

    def breaker_register(self) -> int:
        return BS_CLOSED if self.breakerState == True else BS_OPEN

    def input_registers(self) -> dict:
        """Return {address: value} for all input registers (0-based addresses)."""
        regs = {}
        # 30001-30006 → 0-based indices 0-5
        regs[0]  = self.breaker_register()          # 30001
        regs[1]  = self.breaker_register()              # 30002
        regs[2]  = int(self.faultState)             # 30003
        regs[3]  = int(self.remote)                 # 30004
        regs[4]  = int(self.deviceType)             # 30005
        regs[5]  = self.index                       # 30006
        # 30010-30013 → indices 9-12
        for i, v in enumerate(self.Measurement):
            regs[9 + i] = v & 0xFFFF
        # 30020-30023 → indices 19-22  (voltage — second device type uses this)
        for i, v in enumerate(self.PTOC_Timer):
            regs[19 + i] = v & 0xFFFF
        # 30030-30031 → indices 29-30
        regs[29] = int(self.faultEvent)
        regs[30] = self.faultTime & 0xFFFF
        # 30040-30042 → indices 39-41
        regs[39] = self.PIOC_setting_pickup_current & 0xFFFF
        regs[40] = self.PTOC_setting_pickup_current & 0xFFFF
        regs[41] = self.PTOC_setting_time_multiplier & 0xFFFF
        return regs

    def holding_registers(self) -> dict:
        """Return {address: value} for holding registers (0-based)."""
        return {
            0: 0,                   # 40001 Breaker Control (write target)
            1: 0,                   # 40002 Trip Reset
            3: int(self.remote),    # 40004 Local/Remote
        }

# ---------------------------------------------------------------------------
# Custom data block that links writes back to the device model
# ---------------------------------------------------------------------------

class RelayDataBlock(ModbusSparseDataBlock):
    """Sparse block that intercepts writes to apply device logic."""

    def __init__(self, device: RelayDevice, register_type: str):
        self.device = device
        self.register_type = register_type
        if register_type == "holding":
            values = device.holding_registers()
        else:
            values = device.input_registers()
        # Pad sparse dict so pymodbus doesn't complain on range reads
        full = {i: 0 for i in range(60)}
        full.update(values)
        super().__init__(full)

    def setValues(self, address, values):
        log.info("setValues called: " + str(address) + " " + str(values))
        super().setValues(address, values)
        if self.register_type != "holding":
            return
        # address is 1-based in pymodbus FC6/FC16 calls; convert
        # pymodbus passes 0-based address here after subtracting offset
        for offset, val in enumerate(values):
            reg = address + offset  # 0-based
            dev = self.device
            if reg == 1:  # 40001 Breaker Control
                if val == 1 and dev.remote:
                    log.info("[%d] OPEN breaker command", dev.index)
                    dev.breakerState = False
                    dev.tripState = False
                elif val == 2 and dev.remote:
                    log.info("[%d] CLOSE breaker command", dev.index)
                    dev.breakerState = True
                # Reset control register
                super().setValues(1, [0])
                self.sync_from_device()
            elif reg == 2:  # 40002 Trip Reset
                if val == 1:
                    log.info("[%d] TRIP RESET command", dev.index)
                    dev.tripState = False
                    dev.faultState = False
                    dev.faultEvent = FaultEvent.NONE
                super().setValues(2, [0])
            elif reg == 4:  # 40004 Local/Remote
                if dev.remote:  # only writable from Remote mode to go Local
                    dev.remote = bool(val)
                    log.info("[%d] Local/Remote set to %s", dev.index, "Remote" if dev.remote else "Local")

    def sync_from_device(self):
        """Push current device state into the register values."""
        if self.register_type == "input":
            regs = self.device.input_registers()
        else:
            regs = self.device.holding_registers()
            # Preserve any pending write values for control regs
            regs[3] = int(self.device.remote)
        for addr, val in regs.items():
            super().setValues(addr, [val & 0xFFFF])

# ---------------------------------------------------------------------------
# Build the server context
# ---------------------------------------------------------------------------

def build_context(devices: List[RelayDevice]):
    slaves = {}
    for dev in devices:
        unit_id = dev.index + 1  # Modbus unit IDs 1-10
        print(unit_id)
        hr_block = RelayDataBlock(dev, "holding")
        ir_block = RelayDataBlock(dev, "input")
        slaves[unit_id] = ModbusSlaveContext(
            di=ModbusSparseDataBlock({i: 0 for i in range(60)}),
            co=ModbusSparseDataBlock({i: 0 for i in range(60)}),
            hr=hr_block,
            ir=ir_block,
        )
    return ModbusServerContext(slaves=slaves, single=False), \
           [(dev, slaves[dev.index + 1]) for dev in devices]

# ---------------------------------------------------------------------------
# Background simulator — randomly mutates device state
# ---------------------------------------------------------------------------

def simulate(devices: List[RelayDevice], slave_map, interval: float = 2.0):
    """Periodically update measurements and sync registers."""
    log.info("Simulator thread started (update every %.1fs)", interval)
    while True:
        time.sleep(interval)
        for dev in devices:
            # Drift measurements a little
            base = 1200 if dev.deviceType != DeviceType.MEASURE else 2300
            dev.Measurement = [
                max(0, base + random.randint(-50, 50)) for _ in range(4)
            ]
            # Sync registers
            ctx = slave_map[dev.index]
            ctx.store["i"].sync_from_device()
            ctx.store["h"].sync_from_device()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def make_devices() -> List[RelayDevice]:
    types = [DeviceType.INFEED, DeviceType.MEASURE, DeviceType.OUTFEED]
    devices = []
    i = 0 # 0
    d = RelayDevice(
            index=i,
            deviceType=types[0],
            breakerState=1,
            remote=True,
            Measurement=[1200 + i*10, 1195 + i*10, 1205 + i*10, 5 + i],
            PTOC_setting_pickup_current=1000,
            PTOC_setting_time_multiplier=10,
            PIOC_setting_pickup_current=5000,
        )
    devices.append(d)
    i += 1 # 1
    d = RelayDevice(
            index=i,
            deviceType=types[1],
            breakerState=0,
            remote=True,
            Measurement=[1200 + i*10, 1195 + i*10, 1205 + i*10, 5 + i],
            PTOC_setting_pickup_current=1000,
            PTOC_setting_time_multiplier=10,
            PIOC_setting_pickup_current=5000,
        )
    devices.append(d)
    i += 1 # 3
    for i in range(i, i+3): # 3,4,5
        d = RelayDevice(
            index=i,
            deviceType=types[2],
            breakerState=2,
            remote=True,
            Measurement=[1200 + i*10, 1195 + i*10, 1205 + i*10, 5 + i],
            PTOC_setting_pickup_current=1000,
            PTOC_setting_time_multiplier=10,
            PIOC_setting_pickup_current=5000,
        )
        devices.append(d)
    i += 1 # 6
    d = RelayDevice(
            index=i,
            deviceType=types[0],
            breakerState=1,
            remote=True,
            Measurement=[1200 + i*10, 1195 + i*10, 1205 + i*10, 5 + i],
            PTOC_setting_pickup_current=1000,
            PTOC_setting_time_multiplier=10,
            PIOC_setting_pickup_current=5000,
        )
    devices.append(d)
    i += 1 # 7
    d = RelayDevice(
            index=i,
            deviceType=types[1],
            breakerState=0,
            remote=True,
            Measurement=[1200 + i*10, 1195 + i*10, 1205 + i*10, 5 + i],
            PTOC_setting_pickup_current=1000,
            PTOC_setting_time_multiplier=10,
            PIOC_setting_pickup_current=5000,
        )
    devices.append(d)
    i += 1 # 8
    for i in range(i, i+3):
        d = RelayDevice(
            index=i,
            deviceType=types[2],
            breakerState=2,
            remote=True,
            Measurement=[1200 + i*10, 1195 + i*10, 1205 + i*10, 5 + i],
            PTOC_setting_pickup_current=1000,
            PTOC_setting_time_multiplier=10,
            PIOC_setting_pickup_current=5000,
        )
        devices.append(d)
    return devices

def main():
    parser = argparse.ArgumentParser(description="Modbus RTU-over-TCP relay device simulator")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=502)
    args = parser.parse_args()

    devices = make_devices()
    context, slave_pairs = build_context(devices)

    # slave_map: index -> SlaveContext  (for simulator thread)
    slave_map = {dev.index: sc for dev, sc in slave_pairs}

    identity = ModbusDeviceIdentification()
    identity.VendorName  = "SimCo"
    identity.ProductName = "RelaySimulator"
    identity.ModelName   = "10-Device RTU"

    sim_thread = threading.Thread(
        target=simulate, args=(devices, slave_map), daemon=True
    )
    sim_thread.start()

    log.info("Starting Modbus TCP server on %s:%d  (unit IDs 1-10)", args.host, args.port)
    log.info("Example: mbpoll -m tcp -a 1 -t 3 -0 -r 0 -c 50 %s", args.host)
    StartTcpServer(context=context, identity=identity, address=(args.host, args.port))

if __name__ == "__main__":
    main()