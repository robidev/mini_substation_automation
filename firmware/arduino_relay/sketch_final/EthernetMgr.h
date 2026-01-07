#pragma once
#include <Arduino.h>
//Wiznet W5500

bool EthernetMgr_init();
void EthernetMgr_tick();

bool EthernetMgr_isUp();
bool EthernetMgr_restarting();
