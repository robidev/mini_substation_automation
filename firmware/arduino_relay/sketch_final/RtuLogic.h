#pragma once
#include <Arduino.h>

enum DeviceType {
  TYPE_RELAY_INCOMING,
  TYPE_MEASURE,
  TYPE_RELAY_OUTGOING,
};

enum BreakerEvent {
  BREAKER_OPEN,
  BREAKER_CLOSED,
  BREAKER_TRIPPED
};

enum FaultEvent {
  None,
  Phase_OC,
  Earth_fault
};

struct relay_state {
    DeviceType deviceType;
    bool breakerState; // True=Closed, False=Open
    bool tripState;    // True=tripped, False=Reset
    bool faultState;   // True=Fault detected, False=No fault
    BreakerEvent breakerEvent; //
    FaultEvent faultEvent;     //
    long Measurement[4];// 4x current or 4x voltage
    bool remote;// True=Remote, False = Local
    long PTOC_setting_pickup_current;
    long PTOC_setting_time_multiplier;
    long PIOC_setting_pickup_current;
};


void RtuLogic_init();
void RtuLogic_tick();