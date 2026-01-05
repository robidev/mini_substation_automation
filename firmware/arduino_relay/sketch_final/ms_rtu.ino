//sketch for arduino mega 2560
#include "Pins.h"
#include "Config.h"

#include "AdcManager.h"
#include "RelayUI.h"
#include "RtuLogic.h"
#include "EthernetMgr.h"
#include "ModbusSrv.h"

void setup()
{
  // init MS leds (10 output)
  // init MS inputs (6 input with pullup)
  RtuLogic_init();
  // init serial (via USB-connector)
  AdcManager_init();
  // init buttons(3 GPIO)
  // init LCD (I2C)
  // init LEDS (4 output)
  RelayUI_init();
  // init ehternet (w5100)
  EthernetMgr_init();
  // init mobus and modbus-register map
  ModbusSrv_init();
}


void loop()
{
// CT/VT data (100HZ loop), when enabled
  // read serial input for watchdog-trigger (10hz loop) (only start sending ADC values when we receive a message for how many to send)
    // check new message, if it contains the right message, and an amount of times to read the adc at interval
    // enable reading
  // read ADC (12 analog reads)
  // read interconnect-shorts(switching 6 ADC inputs to output-low in sequence)
  // write serial startbyte, (12x CT, 6-byte bools for shorts), crc, stopbyte
  AdcManager_tick();

// Relay interface (20 Hz loop?)
  // handle button-reads (6 charlieplexed inputs, 3 GPIO wires)
  // menu event loop (actions, settings, readouts)
  // draw LCD-menu (I2C controlled LCD; SDA, SCL)
  // handle display leds (4 OUTPUT)
  RelayUI_tick();

// RTU logic (10hz loop)
  // process logic based on 6x ADC input, 6x GPIO input, modbus-data/events, menu-interface
  // handle MS leds (10 outputs)
  RtuLogic_tick();

// Background tasks (every loop)
  // handle ethernet-stack
  EthernetMgr_tick();

  // handle modbus-server
  ModbusSrv_tick();
}


