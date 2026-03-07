#pragma once
#include <Arduino.h>

/* ================= MS LED OUTPUTS ================= */
constexpr uint8_t BLUE1 = 7; // in
constexpr uint8_t BLUE2 = 9; // out1
constexpr uint8_t BLUE3 = 6; // out2
constexpr uint8_t BLUE4 = 8; // out3

constexpr uint8_t RED1 = 42; // in
constexpr uint8_t RED2 = 5;  // out1
constexpr uint8_t RED3 = 43; // out2
constexpr uint8_t RED4 = 3;  // out3

/* ================= MS INPUTS (short sense for outgoing MS feeder) ================= */
constexpr uint8_t PIN_MS_IN_RED2  = 30; // pin-assignment not final
constexpr uint8_t PIN_MS_IN_RED3  = 31; // pin-assignment not final
constexpr uint8_t PIN_MS_IN_RED4  = 32; // pin-assignment not final
constexpr uint8_t PIN_MS_IN_BLUE2 = 33; // pin-assignment not final
constexpr uint8_t PIN_MS_IN_BLUE3 = 34; // pin-assignment not final
constexpr uint8_t PIN_MS_IN_BLUE4 = 35; // pin-assignment not final


/* ================= SERIAL ================= */
constexpr uint8_t  RX_PIN = 0;
constexpr uint8_t  TX_PIN = 1;


/* ================= ADC INPUTS ================= */
constexpr uint8_t  ADC0_PIN = A0; // feed 1, phase 1
constexpr uint8_t  ADC1_PIN = A1; // feed 1, phase 2
constexpr uint8_t  ADC2_PIN = A2; // feed 1, phase 3
constexpr uint8_t  ADC3_PIN = A3; // feed 2, phase 1
constexpr uint8_t  ADC4_PIN = A4; // feed 2, phase 2
constexpr uint8_t  ADC5_PIN = A5; // feed 2, phase 3

constexpr uint8_t  ADC6_PIN = A8; // PTR 1, phase 1
constexpr uint8_t  ADC7_PIN = A9; // PTR 1, phase 2
constexpr uint8_t  ADC8_PIN = A10; // PTR 1, phase 3
constexpr uint8_t  ADC9_PIN = A11; // PTR 2, phase 1
constexpr uint8_t  ADC10_PIN = A12; // PTR 2, phase 2
constexpr uint8_t  ADC11_PIN = A13; // PTR 2, phase 3


/* ================= CHARLIEPLEXED UI BUTTONS ================= */
constexpr uint8_t BTN1 = 11; //
constexpr uint8_t BTN2 = 12; //
constexpr uint8_t BTN3 = 13; //


/* ================= UI LCD (I2C) ================= */
// SDA / SCL fixed on Mega (20 / 21)
constexpr uint8_t LCD_SDA = 20; // D20
constexpr uint8_t LCD_SDC = 21; // D21


/* ================= UI LED OUTPUTS ================= */
constexpr uint8_t LED1 = 49; // Trip
constexpr uint8_t LED2 = 48; // Alarm
constexpr uint8_t LED3 = 47; // Warning
constexpr uint8_t LED4 = 46; // Healthy


/* ================= ETHERNET W5500 ================= */
constexpr uint8_t PIN_ETH_CS     = 10; // W5500 chip select
constexpr uint8_t PIN_ETHint     = 2;  // W5500 ethernet interrupt
constexpr uint8_t PIN_SDcard     = 4;  // W5500 sdcard select
constexpr uint8_t PIN_MISO       = 50; // W5500 SPI
constexpr uint8_t PIN_MOSI       = 51; // W5500 SPI
constexpr uint8_t PIN_SCK        = 52; // W5500 SPI
constexpr uint8_t PIN_HardwareSS = 53; // W5500 slave select