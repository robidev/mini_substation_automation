#include "ModbusSrv.h"
#include "EthernetMgr.h"
#include "RtuLogic.h"
#include "Config.h"

#include <ArduinoModbus.h>
#include <Ethernet.h>

extern "C" {
#include "libmodbus/modbus.h"
#include "libmodbus/modbus-tcp.h"
}


EthernetServer ethServer(MODBUS_TCP_PORT);
static customModbusTCPServer modbusTCP;
EthernetClient clients[8];

static bool modbusStarted = false;

static void setupRegisterMap() {
  modbusTCP.configureHoldingRegisters(0, 16);
  modbusTCP.configureInputRegisters(0, 64);
}

void ModbusSrv_init() {
  modbusStarted = false;
}

void updateModbusRegisters(uint8_t index)
{
  relay_state* relay = getRelayDataByIndex(index);
  if(!relay){ // nullptr means error
    //clear all registers
    return;
  }
  
  //inputs
  if(relay->deviceType == TYPE_MEASURE) {
    //clear all registers
    //TODO values should be 32 bit instead of 16
    modbusTCP.inputRegisterWrite(20,(uint16_t)relay->Measurement[0]);
    modbusTCP.inputRegisterWrite(21,(uint16_t)relay->Measurement[1]);
    modbusTCP.inputRegisterWrite(22,(uint16_t)relay->Measurement[2]);
    modbusTCP.inputRegisterWrite(23,(uint16_t)relay->Measurement[3]);
  }
  else { // TYPE BREAKER
    //reset measurement regs
    //holding regs
    uint8_t breaker = modbusTCP.holdingRegisterRead(1); // | 40001 / 00  | Breaker Control | RW   | Command to breaker    | 0 = No action, 1 = Open, 2 = Close      |
    if(breaker) {
      process_breaker(relay, breaker, REMOTE);
      modbusTCP.holdingRegisterWrite(4,0); // TODO return error if failed, with additional status(idle/success/fail/)/failure-code registers
    }

    uint8_t trip = modbusTCP.holdingRegisterRead(2);    // | 40002 / 01  | Trip Reset      | RW   | Clears a trip         | 0 = No action, 1 = Reset trip     
    if(trip) {
      process_trip(relay, trip, REMOTE);
      modbusTCP.holdingRegisterWrite(4,0); // TODO return error if failed, with additional status(idle/success/fail/)/failure-code registers
    }   

    // no holding register for fault value (40003)
    uint8_t control = modbusTCP.holdingRegisterRead(4); // | 40004 / 03  | Local/Remote    | RW   | set to local/remote   | 0 = No action, 1= Local, 2 = Remote(cannot be written)|
    if(control) {
      relay->remote = control -1; // 0=local 1=remote, but 'control' is 1 or 2 
      modbusTCP.holdingRegisterWrite(4,0); // TODO return error if failed, with additional status(idle/success/fail/)/failure-code registers
    }

    modbusTCP.inputRegisterWrite(1,(uint16_t)relay->breakerState); // 30001 / 00
    modbusTCP.inputRegisterWrite(2,(uint16_t)relay->tripState);    // 30002 / 01
    modbusTCP.inputRegisterWrite(3,(uint16_t)relay->faultState);   // 30003 / 02
    modbusTCP.inputRegisterWrite(4,(uint16_t)relay->remote + 1);   // 30004 / 03
    modbusTCP.inputRegisterWrite(5,(uint16_t)relay->deviceType);   // 30005 / 04
    modbusTCP.inputRegisterWrite(6,(uint16_t)relay->index);   // 30006 / 05

    //TODO some values should be 32 bit instead of 16
    modbusTCP.inputRegisterWrite(10,(uint16_t)relay->Measurement[0]);
    modbusTCP.inputRegisterWrite(11,(uint16_t)relay->Measurement[1]);
    modbusTCP.inputRegisterWrite(12,(uint16_t)relay->Measurement[2]);
    modbusTCP.inputRegisterWrite(13,(uint16_t)relay->Measurement[3]);

    modbusTCP.inputRegisterWrite(30,(uint16_t)relay->faultEvent);
    modbusTCP.inputRegisterWrite(31,(uint16_t)relay->faultTime);

    modbusTCP.inputRegisterWrite(40,(uint16_t)relay->PIOC_setting_pickup_current);
    modbusTCP.inputRegisterWrite(41,(uint16_t)relay->PTOC_setting_pickup_current);
    modbusTCP.inputRegisterWrite(42,(uint16_t)relay->PTOC_setting_time_multiplier);
  }
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

  EthernetClient newClient = ethServer.accept();

  if (newClient) {
    for (byte i = 0; i < 8; i++) {
      if (!clients[i]) {
        modbusTCP.accept(clients[i]);
        clients[i] = newClient;
        break;
      }
    }
  }

  // check for incoming data from all clients
  for (byte i = 0; i < 8; i++) {
    if (clients[i] && clients[i].available() > 0) {
      modbusTCP.poll();
    }
  }

  // stop any clients which disconnect
  for (byte i = 0; i < 8; i++) {
    if (clients[i] && !clients[i].connected()) {
      clients[i].stop();
    }
  }
}

bool ModbusSrv_status()
{
  return modbusStarted;
}


customModbusTCPServer::customModbusTCPServer() :
  _client(NULL)
{ }
customModbusTCPServer::~customModbusTCPServer() { }

int customModbusTCPServer::begin(int id)
{
  modbus_t* mb = modbus_new_tcp(NULL, IPAddress(0, 0, 0, 0), 0);
  if (!ModbusServer::begin(mb, id)) {
    return 0;
  }
  if (modbus_tcp_listen(mb) != 0) {
    return 0;
  }
  return 1;
}

void customModbusTCPServer::accept(Client& client)
{
  if (modbus_tcp_accept(_mb, &client) == 0) {
    _client = &client;
  }
}

int customModbusTCPServer::poll()
{
  if (_client != NULL) {
    uint8_t request[MODBUS_TCP_MAX_ADU_LENGTH];
    int requestLength = modbus_receive(_mb, request);
    if (requestLength > 0) {
      uint8_t unitId = request[6]; // MBAP unit id
      updateModbusRegisters(unitId - 1);
      modbus_reply(_mb, request, requestLength, &_mbMapping);
      return 1;
    }
  }
  return 0;
}
