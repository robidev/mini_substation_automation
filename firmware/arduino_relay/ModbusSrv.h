#pragma once
#include <Arduino.h>
#include <Client.h>
#include "ModbusServer.h"

class customModbusTCPServer : public ModbusServer {
public:
  customModbusTCPServer();
  virtual ~customModbusTCPServer();
  int begin(int id = 0xff);
  void accept(Client& client);
  virtual int poll();

private:
  Client* _client;
};


void ModbusSrv_init();
void ModbusSrv_tick();
bool ModbusSrv_status();

/*
Holding Registers (40001+) for read/write control/status
Input Registers (30001+) for read-only measurements (optional)
Registers are 16-bit integers
Floats (for CT/VT) stored as 2 consecutive 16-bit registers if needed
No scaling is applied — raw values are used
All operations are single coil/write per function for simplicity

mbpoll -m tcp -a 1 -t 3 -0 -r 0 -c 50 172.16.1.12

| Address | Name            | Type | Description           | Values                                  |
| ------- | --------------- | ---- | --------------------- | --------------------------------------- |
| 40001   | Breaker Control | RW   | Command to breaker    | 0 = No action, , 1 = Open, 2 = Close    |
| 40002   | Trip Reset      | RW   | Clears a trip         | 0 = No action, 1 = Reset trip           |
| 40004   | Local/Remote    | RW   | set to local/remote   | 0 = Local, 1 = Remote(cannot be written)|


| Address | Name          | Type | Description           | Values                               |
| ------- | ------------- | ---- | --------------------- | -------------------------------------|
| 30001   | Breaker State | RO   | Current breaker state | 0 = OPEN, 1 = CLOSED, 2 = TRIPPED    |
| 30002   | Trip Status   | RO   | Trip flag             | 0 = OK, 1 = TRIPPED                  |
| 30003   | Fault Status  | RO   | Fault detected        | 0 = None, 1 = FAULT                  |
| 30004   | Local/Remote  | RO   | local/remote status   | 0 = Local, 1 = Remote                |
| 30005   | DeviceType    | RO   | The device type       | 0 = infeed, 1 = measure, 2 = outfeed |
| 30006   | Device index  | RO   | unique device index   | 0-9 for all devices                  |


| Address | Name | Type | Description                         | Notes                 |
| ------- | ---- | ---- | ----------------------------------- | --------------------- |
| 30010   | IA   | RO   | Phase A current (A × 10 if integer) | Example: 123 → 12.3 A |
| 30011   | IB   | RO   | Phase B current                     |                       |
| 30012   | IC   | RO   | Phase C current                     |                       |
| 30013   | In   | RO   | Phase neutral current               |                       |


| Address | Name | Type | Description                         | Notes                     |
| ------- | ---- | ---- | ----------------------------------- | ------------------------- |
| 30020   | VA   | RO   | Phase A voltage (V × 10 if integer) | Example: 10200 → 1020.0 V |
| 30021   | VB   | RO   | Phase B voltage                     |                           |
| 30022   | VC   | RO   | Phase C voltage                     |                           |
| 30023   | Vn   | RO   | Phase neutral voltage               |                           |


| Address | Name           | Type | Description                           |
| ------- | -------------- | ---- | ------------------------------------- |
| 30030   | Last Trip Type | RO   | 0=None, 1=Phase OC, 2=Earth Fault     |
| 30031   | Last Trip Time | RO   | Unix timestamp or seconds since reset |


| Address | Name                | Type | Description         |
| ------- | ------------------- | ---- | ------------------- |
| 30040   | PIOC Pickup current | RO   | current in amps     |
| 30041   | PTOC Pickup current | RO   | current in amps     |
| 30042   | PTOC TMS            | RO   | Time mulitplier     |

*/

