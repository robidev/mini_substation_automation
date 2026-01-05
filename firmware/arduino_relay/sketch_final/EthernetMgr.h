#pragma once
#include <Arduino.h>

bool EthernetMgr_init();
void EthernetMgr_tick();

bool EthernetMgr_isUp();
bool EthernetMgr_restarting();
