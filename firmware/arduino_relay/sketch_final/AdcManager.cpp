#include "AdcManager.h"
#include "Pins.h"
#include "Config.h"

uint16_t adcValues[ADC_NUM_CHANNELS];
uint8_t shortMatrix[ADC_WIRE_COUNT]; //[ADC_WIRE_COUNT];

struct StreamControl {
  bool enabled;
  uint16_t remainingFrames;
  uint32_t lastSendUs;
};

static StreamControl stream = {};


uint8_t crc8(const uint8_t *data, uint8_t len) {
  uint8_t crc = 0x00;
  while (len--) {
    crc ^= *data++;
    for (uint8_t i = 0; i < 8; i++) {
      if (crc & 0x80)
        crc = (crc << 1) ^ 0x07;
      else
        crc <<= 1;
    }
  }
  return crc;
}

void readADC() {
  for (uint8_t i = 0; i < ADC_NUM_CHANNELS; i++) {
    adcValues[i] = analogRead(adcPins[i]);
  }
}


/*void detectShorts(bool shortMatrix[ADC_WIRE_COUNT][ADC_WIRE_COUNT]) {
  // Initialize all to false
  for (uint8_t i = 0; i < ADC_WIRE_COUNT  ; i++)
    for (uint8_t j = 0; j < ADC_WIRE_COUNT; j++)
      shortMatrix[i][j] = false;

  for (uint8_t drive = 0; drive < ADC_WIRE_COUNT; drive++) {
    // Ensure all other wires are INPUT
    for (uint8_t j = 0; j < ADC_WIRE_COUNT; j++)
      pinMode(adcPins[j], INPUT);

    // Drive one wire LOW
    pinMode(adcPins[drive], OUTPUT);
    digitalWrite(adcPins[drive], LOW);

    delayMicroseconds(ADC_PULSE_SETTLE_US);

    // Read all other wires
    for (uint8_t sense = 0; sense < ADC_WIRE_COUNT; sense++) {
      if (sense == drive) continue; // skip self
      uint16_t adc = analogRead(adcPins[sense]);//110uS
      shortMatrix[drive][sense] = (adc < ADC_SHORT_THRESHOLD); // true if connected
    }

    // Release driven pin
    pinMode(adcPins[drive], INPUT);

    // Optional small delay to avoid ADC ghosting
    //delayMicroseconds(2);
  }
}*/

void detectShorts(uint8_t packed[ADC_WIRE_COUNT]) {
    for (int drive = 0; drive < ADC_WIRE_COUNT; drive++) {
        packed[drive] = 0;

        // Drive wire drive LOW
        pinMode(adcPins[drive], OUTPUT);
        digitalWrite(adcPins[drive], LOW);

        delayMicroseconds(2);  // settle time

        for (int sense = 0; sense < ADC_WIRE_COUNT; sense++) {
            if (sense == drive) continue; // skip self

            int adc = analogRead(adcPins[sense]); //110uS

            if (adc < ADC_SHORT_THRESHOLD) {
                packed[drive] |= (1 << sense);
            }
        }

        // Release wire drive
        pinMode(adcPins[drive], INPUT);
        // Optional small delay to avoid ADC ghosting
        delayMicroseconds(2);
    }
}


void sendADCPacket_old() {
  const uint8_t payloadLen = (ADC_NUM_CHANNELS * 2) + ADC_WIRE_COUNT;
  uint8_t packet[1 + payloadLen]; // LEN + payload

  packet[0] = payloadLen;

  for (uint8_t i = 0; i < ADC_NUM_CHANNELS; i++) {
    packet[1 + i * 2]     = adcValues[i] & 0xFF;        // LSB
    packet[1 + i * 2 + 1] = adcValues[i] >> 8;          // MSB
  }
  for (uint8_t j = 0; j < ADC_WIRE_COUNT; j++)
    packet[1 + (ADC_NUM_CHANNELS * 2) + j] = shortMatrix[j];

  uint8_t crc = crc8(packet, sizeof(packet));

  // Ensure buffer space before sending (important!)
  if (Serial.availableForWrite() >= (2 + sizeof(packet) + 1 + 2)) {
    Serial.write(0xAA);
    Serial.write(0x55);
    Serial.write(packet, sizeof(packet));
    Serial.write(crc);
    Serial.write(0x0D);
    Serial.write(0x0A);
  }
}


void sendADCPacket() {

  const uint8_t payloadLen = (ADC_NUM_CHANNELS * 2) + ADC_WIRE_COUNT + (IN_RELAY_CHANNELS * 2);
  uint8_t packet[1 + payloadLen]; // LEN + payload
  packet[0] = payloadLen;
  
  uint8_t idx = 1;
  
  // Pack existing ADC values
  for (uint8_t i = 0; i < ADC_NUM_CHANNELS; i++) {
    packet[idx++] = adcValues[i] & 0xFF;        // LSB
    packet[idx++] = adcValues[i] >> 8;          // MSB
  }
  
  // Pack short matrix
  for (uint8_t j = 0; j < ADC_WIRE_COUNT; j++) {
    packet[idx++] = shortMatrix[j];
  }
  
  // Pack relay measurements
  relay_state* relay1 = getRelayData(0, TYPE_RELAY_INCOMING_INDEX);
  relay_state* relay2 = getRelayData(1, TYPE_RELAY_INCOMING_INDEX);
  
  for (uint8_t i = 0; i < 3; i++) {
    uint16_t val1 = (uint16_t)relay1->Measurement[i];
    packet[idx++] = val1 & 0xFF;        // LSB
    packet[idx++] = val1 >> 8;          // MSB
  }
  for (uint8_t i = 0; i < 3; i++) {
    uint16_t val2 = (uint16_t)relay2->Measurement[i];
    packet[idx++] = val2 & 0xFF;        // LSB
    packet[idx++] = val2 >> 8;          // MSB
  }
  
  uint8_t crc = crc8(packet, sizeof(packet));
  
  // Ensure buffer space before sending (important!)
  if (Serial.availableForWrite() >= (2 + sizeof(packet) + 1 + 2)) {
    Serial.write(0xAA);
    Serial.write(0x55);
    Serial.write(packet, sizeof(packet));
    Serial.write(crc);
    Serial.write(0x0D);
    Serial.write(0x0A);
  }
}


void handleSerialCommand(StreamControl& sc) {
  static char buf[32];
  static uint8_t idx = 0;

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      buf[idx] = 0;
      idx = 0;

      uint16_t n;
      if (sscanf(buf, "@ADC:%hu", &n) == 1) {
        sc.enabled = true;
        sc.remainingFrames = n % 100;   // reset counter, max 100, in case frame is corrupted
      }
    } else if (idx < sizeof(buf) - 1) {
      buf[idx++] = c;
    }
  }
}

void adcSendTick(StreamControl& sc) {
  uint32_t now = micros();
  if (now - sc.lastSendUs < ADC_PERIOD_US)
    return;

  sc.lastSendUs = now;

  readADC(); //we also use ADC for MS feeder input

  if (!sc.enabled || sc.remainingFrames == 0)
    return;

  detectShorts(shortMatrix); // shorts are only for HS

  sendADCPacket();   // read ADC + write serial frame
  sc.remainingFrames--;

  if (sc.remainingFrames == 0) {
    sc.enabled = false;
  }
}

void AdcManager_init() {
  stream.enabled = false;
  stream.remainingFrames = 0;
  stream.lastSendUs = 0;
  Serial.begin(SERIAL_BAUD);

  //ensure ADC-pins are inputs
  for (uint8_t j = 0; j < ADC_WIRE_COUNT; j++)
    pinMode(adcPins[j], INPUT);
}

void AdcManager_tick() {
  handleSerialCommand(stream);
  adcSendTick(stream);
}

uint16_t getAdcValue(int index) {
  return adcValues[index];
}
 