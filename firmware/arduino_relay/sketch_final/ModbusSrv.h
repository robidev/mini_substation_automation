#pragma once
#include <Arduino.h>

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

| Address | Name            | Type | Description           | Values                                  |
| ------- | --------------- | ---- | --------------------- | --------------------------------------- |
| 40001   | Breaker Control | RW   | Command to breaker    | 0 = No action, 1 = Close, 2 = Open      |
| 40002   | Trip Reset      | RW   | Clears a trip         | 0 = No action, 1 = Reset trip           |
| 40004   | Local/Remote    | RW   | set to local/remote   | 0 = Local, 1 = Remote(cannot be written)|


| Address | Name          | Type | Description           | Values                            |
| ------- | ------------- | ---- | --------------------- | --------------------------------- |
| 30001   | Breaker State | RO   | Current breaker state | 0 = OPEN, 1 = CLOSED, 2 = TRIPPED |
| 30002   | Trip Status   | RO   | Trip flag             | 0 = OK, 1 = TRIPPED               |
| 30003   | Fault Status  | RO   | Fault detected        | 0 = None, 1 = FAULT               |
| 30004   | Local/Remote  | RO   | local/remote status   | 0 = Local, 1 = Remote             |


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


  modbusTCP.configureHoldingRegisters(0, 64);// means 40000
  modbusTCP.configureInputRegisters(0, 64);  // means 30000
  modbusTCP.configureCoils(0, 32);
  modbusTCP.configureDiscreteInputs(0, 32);
*/