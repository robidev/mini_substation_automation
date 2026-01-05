#pragma once
#include <Arduino.h>

void AdcManager_init();
void AdcManager_tick();

uint16_t getAdcValue(int index);