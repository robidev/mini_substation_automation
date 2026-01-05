#include "ModbusSrv.h"
#include "EthernetMgr.h"
#include "Config.h"

#include <ArduinoModbus.h>
#include <Ethernet.h>

EthernetServer ethServer(MODBUS_TCP_PORT);
static ModbusTCPServer modbusTCP;

static bool modbusStarted = false;

static void setupRegisterMap() {
  modbusTCP.configureHoldingRegisters(0, 64);
  modbusTCP.configureInputRegisters(0, 64);
}


void ModbusSrv_init() {
  modbusStarted = false;
}

void ModbusSrv_tick() {
  if (!EthernetMgr_isUp()) {
    modbusStarted = false;
    return;
  }

  if (!modbusStarted) {
    ethServer.begin();
    if (!modbusTCP.begin()) {
      return; // try again next tick
    }

    setupRegisterMap();
    modbusStarted = true;
  }

  // Non-blocking: handles connections, frames, responses
  modbusTCP.poll();
}

bool ModbusSrv_status()
{
  return modbusStarted;
}