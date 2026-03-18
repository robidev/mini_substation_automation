#include "EthernetMgr.h"
#include "Config.h"

#include <SPI.h>
#include <Ethernet.h>
#include "Pins.h"

static bool ethUp = false;
static bool restarting = false;
static uint32_t lastMaintainMs = 0;
static uint32_t lastRecoverMs = 0;

static void restartEthernet() {
  restarting = true;
  ethUp = false;
  //delay(50);                    // W5100 needs this
  pinMode(PIN_ETHint, INPUT);     // W5500 ethernet interrupt
  pinMode(PIN_SDcard, OUTPUT);    // W5500 sdcard select
  digitalWrite(PIN_SDcard, HIGH); // W5500 set sd-card inactive
  Ethernet.init(PIN_ETH_CS);


  //if DHCP_ENBALE is not 0, try to perform DHCP, if it returns 0, it means no DHCP lease could be gotten, and we set a static ip.
  if (ETH_DHCP_ENABLE == 0 || Ethernet.begin(mac) == 0) {
    Ethernet.begin(mac, fallbackIp);
  }
  restarting = false;
  ethUp = true;
}

bool EthernetMgr_init() {
  restartEthernet();
  return ethUp;
}

void EthernetMgr_tick() {
  uint32_t now = millis();

  // Maintain DHCP
  if (ETH_DHCP_ENABLE && (now - lastMaintainMs) > ETH_MAINTAIN_MS ) {
    lastMaintainMs = now;
    Ethernet.maintain();
  }

  // Link monitoring
  if (Ethernet.linkStatus() == LinkOFF) {
    ethUp = false;
    return;
  }

  // IP sanity check
  if (Ethernet.localIP() == IPAddress(0,0,0,0)) {
    ethUp = false;
  }

  // Recovery attempt
  if (!ethUp && now - lastRecoverMs > ETH_RECOVER_MS) {
    lastRecoverMs = now;
    restartEthernet();
  }
}

bool EthernetMgr_isUp() {
  return ethUp && !restarting;
}

bool EthernetMgr_restarting() {
  return restarting;
}
