#pragma once
#include "Pins.h"

#include <Ethernet.h>
#include <LiquidCrystal_I2C.h>

/* ------------------------------------------------------
    AdcManager   
------------------------------------------------------ */
constexpr uint32_t SERIAL_BAUD = 115200;
constexpr uint8_t ADC_NUM_CHANNELS = 12;
constexpr uint32_t ADC_PERIOD_US = 10000; // 100 Hz

//analog channel order
const uint8_t adcPins[ADC_NUM_CHANNELS] = {
  ADC0_PIN, ADC1_PIN, ADC2_PIN, ADC3_PIN,
  ADC4_PIN, ADC5_PIN, ADC6_PIN, ADC7_PIN,
  ADC8_PIN, ADC9_PIN, ADC10_PIN, ADC11_PIN
};

constexpr uint8_t ADC_WIRE_COUNT = 6; // wires to check for shorts
constexpr uint16_t ADC_SHORT_THRESHOLD = 750; // ~3.6V (tweak for noise)
constexpr unsigned long ADC_PULSE_SETTLE_US = 2;   // settle time when pulling LOW


/* ------------------------------------------------------
    EthernetMgr  
------------------------------------------------------ */
constexpr uint32_t ETH_MAINTAIN_MS = 1000;
constexpr uint32_t ETH_RECOVER_MS = 5000;

constexpr uint8_t ETH_DHCP_ENABLE = 0;
static byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0x00, 0x01 }; // RTU MAC-address
static IPAddress fallbackIp(172,16,1,12);                   // RTU IP-address
constexpr uint16_t MODBUS_TCP_PORT = 502;                   // RTU Modbus TCP port
constexpr uint8_t ETH_CLIENTS = 4;                          // RTU clients


/* ------------------------------------------------------
   RelayUI   
------------------------------------------------------ */
constexpr unsigned long UI_PERIOD_MS = 50;
constexpr uint8_t LCD_ADDRESS = 0x27; // Change address 0x27 → 0x3F if needed
constexpr uint8_t LCD_CHARACTERS = 16;
constexpr uint8_t LCD_LINES = 2;

const byte lcd_upArrow[8] = {
    0b00100,
    0b01110,
    0b10101,
    0b00100,
    0b00100,
    0b00100,
    0b00100,
    0b00000
  };

//   Ledarray with Trip, Alarm, Warning, Healthy (local/remote?)
const uint8_t ledarray[4] = {LED1,LED2,LED3,LED4};

// CHARLIEPLEXED BUTTON SETUP
const uint32_t charlieplexed_buttons[3] = {BTN1, BTN2, BTN3};// three I/O pins used for charlieplexing

// Each button definition: {HighPinIndex, LowPinIndex}
const int32_t buttonPairs[6][2] = {
  {0, 2}, // Button 3: BTN1 -> BTN3 UP
  {2, 0}, // Button 4: BTN3 -> BTN1 DOWN
  {1, 2}, // Button 5: BTN2 -> BTN3 LEFT
  {0, 1}, // Button 1: BTN1 -> BTN2 RIGHT
  {2, 1}, // Button 6: BTN3 -> BTN2 ENTER
  {1, 0}  // Button 2: BTN2 -> BTN1 CANCEL
};



/* ------------------------------------------------------
   RTU Logic   
------------------------------------------------------ */
constexpr unsigned long RTU_SWI_INTERVAL = 500;
//output pin order
constexpr uint8_t MS_OUT_NUM_CHANNELS = 8;
const uint8_t ms_output_array[MS_OUT_NUM_CHANNELS] = { RED1, RED2, RED3, RED4, BLUE1, BLUE2, BLUE3, BLUE4};
//input pin order
constexpr uint8_t MS_IN_NUM_CHANNELS = 6;
const uint8_t ms_input_array[MS_IN_NUM_CHANNELS] = { PIN_MS_IN_RED2, PIN_MS_IN_RED3, PIN_MS_IN_RED4, PIN_MS_IN_BLUE2, PIN_MS_IN_BLUE3, PIN_MS_IN_BLUE4};

constexpr uint8_t RELAY_ROWS = 2;
constexpr uint8_t RELAY_AMOUNT = 5;
constexpr uint8_t TYPE_RELAY_INCOMING_INDEX = 0;
constexpr uint8_t TYPE_MEASURE_INDEX = 1;
constexpr uint8_t TYPE_RELAY_OUTGOING_INDEX = 2;

const unsigned long RLOAD[RELAY_ROWS][3] = {
    {5, 6, 4},
    {5, 4, 2}
};