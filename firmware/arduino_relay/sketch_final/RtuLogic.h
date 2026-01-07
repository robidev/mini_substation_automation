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

enum Origin {
  LOCAL,
  REMOTE
};

struct relay_state {
    DeviceType deviceType;
    bool breakerState; // True=Closed, False=Open
    bool tripState;    // True=tripped, False=Reset
    bool faultState;   // True=Fault detected, False=No fault
    FaultEvent faultEvent;      //
    uint32_t faultTime;         //
    long Measurement[4];// 4x current or 4x voltage
    long PTOC_Timer[4];// 4x timer
    bool remote;// True=Remote, False = Local
    long PTOC_setting_pickup_current;
    long PTOC_setting_time_multiplier;
    long PIOC_setting_pickup_current;
    uint8_t index;
};


void RtuLogic_init();
void RtuLogic_tick();

relay_state* getRelayData(uint8_t row, uint8_t col);
relay_state* getRelayDataByIndex(uint8_t index);
void process_breaker(relay_state *relay, uint8_t breaker, Origin origin);
void process_trip(relay_state *relay, uint8_t trip_reset, Origin origin);
void setFaultRegister(relay_state* relay, FaultEvent event);
void updateBreakerOutput(relay_state *relay, uint8_t state);