#!/usr/bin/env python3
"""
Modbus Slave Simulator — aligned 1:1 with Arduino firmware semantics.
"""

import argparse
import enum
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from typing import List

from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums / constants
# ---------------------------------------------------------------------------

class DeviceType(enum.IntEnum):
    INFEED = 0
    MEASURE = 1
    OUTFEED = 2

class FaultEvent(enum.IntEnum):
    NONE = 0
    PHASE_OC = 1
    EARTH_FAULT = 2

# ---------------------------------------------------------------------------
# Device model
# ---------------------------------------------------------------------------

@dataclass
class RelayDevice:
    index: int
    deviceType: DeviceType
    breakerState: bool = False   # True = CLOSED
    tripState: bool = False
    faultState: bool = False
    faultEvent: FaultEvent = FaultEvent.NONE
    faultTime: int = 0
    Measurement: List[int] = field(default_factory=lambda: [0]*4)
    remote: bool = True

    PIOC_setting_pickup_current: int = 5000
    PTOC_setting_pickup_current: int = 1000
    PTOC_setting_time_multiplier: int = 10

    def breaker_register(self) -> int:
        return 2 if self.breakerState else 1 # True means CLOSED(2), False means OPEN(1)

    # ---------------- INPUT REGISTERS (3xxxx) ----------------

    def input_registers(self) -> dict:
        regs = {}
        regs[0] = self.breaker_register()           # 30001
        regs[1] = int(self.tripState)               # 30002
        regs[2] = int(self.faultState)              # 30003
        regs[3] = int(self.remote)                  # 30004
        regs[4] = int(self.deviceType)              # 30005
        regs[5] = self.index                        # 30006

        for i, v in enumerate(self.Measurement):
            regs[9 + i] = v & 0xFFFF                 # 30010-13

        regs[29] = int(self.faultEvent)              # 30030
        regs[30] = self.faultTime & 0xFFFF           # 30031

        regs[39] = self.PIOC_setting_pickup_current & 0xFFFF
        regs[40] = self.PTOC_setting_pickup_current & 0xFFFF
        regs[41] = self.PTOC_setting_time_multiplier & 0xFFFF
        return regs

    # ---------------- HOLDING REGISTERS (4xxxx) ----------------

    def holding_registers(self) -> dict:
        # Command registers only — always zeroed
        return {
            0: 0,  # 40001 Breaker Control
            1: 0,  # 40002 Trip Reset
            2: 0,
            3: 0,  # 40004 Local/Remote
        }

# ---------------------------------------------------------------------------
# Custom DataBlock implementing Arduino semantics
# ---------------------------------------------------------------------------

class RelayDataBlock(ModbusSparseDataBlock):
    def __init__(self, device: RelayDevice, kind: str):
        self.device = device
        self.kind = kind

        base = {i: 0 for i in range(60)}
        base.update(
            device.input_registers() if kind == "input"
            else device.holding_registers()
        )
        super().__init__(base)

    def setValues(self, address, values):
        super().setValues(address, values)
        log.info("WRITE HR addr=%d val=%s", address, values)
        if self.kind != "holding":
            return

        dev = self.device
        origin_remote = True  # FC06 always treated as REMOTE origin

        for offset, val in enumerate(values):
            reg = address + offset # 0-based

            # 40001 — Breaker Control
            if reg == 0:
                if origin_remote == dev.remote:
                    if val == 1:
                        log.info("[%d] OPEN breaker", dev.index)
                        dev.breakerState = False
                        dev.tripState = False
                    elif val == 2:
                        log.info("[%d] CLOSE breaker", dev.index)
                        dev.breakerState = True
                else:
                    log.info("[%d] breaker command ignored (LOCAL)", dev.index)

                super().setValues(0, [0])
                self.sync_from_device()

            # 40002 — Trip Reset
            elif reg == 1:
                if origin_remote == dev.remote and val == 1:
                    log.info("[%d] TRIP RESET", dev.index)
                    dev.tripState = False
                    dev.faultState = False
                    dev.faultEvent = FaultEvent.NONE
                else:
                    log.info("[%d] trip reset ignored (LOCAL)", dev.index)

                super().setValues(1, [0])
                self.sync_from_device()

            # 40004 — Local / Remote
            elif reg == 3:
                dev.remote = bool(val)
                log.info("[%d] Mode set to %s",
                         dev.index,
                         "REMOTE" if dev.remote else "LOCAL")
                super().setValues(3, [0])
                self.sync_from_device()

    def sync_from_device(self):
        if self.kind == "input":
            regs = self.device.input_registers()
        else:
            regs = self.device.holding_registers()

        for a, v in regs.items():
            super().setValues(a, [v & 0xFFFF])

# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def build_context(devices: List[RelayDevice]):
    slaves = {}
    pairs = []

    for dev in devices:
        uid = dev.index + 1
        hr = RelayDataBlock(dev, "holding")
        ir = RelayDataBlock(dev, "input")

        ctx = ModbusSlaveContext(
            di=ModbusSparseDataBlock({}),
            co=ModbusSparseDataBlock({}),
            hr=hr,
            ir=ir, zero_mode=True
        )
        slaves[uid] = ctx
        pairs.append((dev, ctx))

    return ModbusServerContext(slaves=slaves, single=False), pairs

# ---------------------------------------------------------------------------
# Background simulator
# ---------------------------------------------------------------------------

def simulate(devices, slave_map, interval=2.0):
    while True:
        time.sleep(interval)
        for dev in devices:
            dev.Measurement = [
                max(0, 1200 + random.randint(-50, 50))
                for _ in range(4)
            ]
            slave_map[dev.index].store["i"].sync_from_device()

# ---------------------------------------------------------------------------
# Device factory
# ---------------------------------------------------------------------------

def make_devices():
    devices = []
    for i in range(10):
        devices.append(
            RelayDevice(
                index=i,
                deviceType=DeviceType.INFEED if i % 5 == 0 else
                           DeviceType.MEASURE if i % 5 == 1 else
                           DeviceType.OUTFEED,
                breakerState=False,
                remote=True,
                Measurement=[1200+i*10, 1195+i*10, 1205+i*10, 5+i],
            )
        )
    return devices

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=502)
    args = parser.parse_args()

    devices = make_devices()
    context, pairs = build_context(devices)
    slave_map = {dev.index: ctx for dev, ctx in pairs}

    identity = ModbusDeviceIdentification()
    identity.VendorName = "SimCo"
    identity.ProductName = "RelaySimulator"
    identity.ModelName = "Arduino-Equivalent"

    threading.Thread(
        target=simulate,
        args=(devices, slave_map),
        daemon=True,
    ).start()

    log.info("Modbus TCP server on %s:%d (unit IDs 1–10)", args.host, args.port)
    StartTcpServer(context=context, identity=identity,
                   address=(args.host, args.port))

if __name__ == "__main__":
    main()