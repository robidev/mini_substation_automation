#include <Ethernet.h>
#include <ArduinoModbus.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#define RED1 3 //in
#define RED2 5 //out1
#define RED3 2 //out2
#define RED4 4 //out3
#define BLUE1 7 //in
#define BLUE2 9 //out1
#define BLUE3 6 //out2
#define BLUE4 8 //out3
unsigned char ioarray[8] = { RED1, RED2, RED3, RED4, BLUE1, BLUE2, BLUE3, BLUE4};

#define LED1 46 // LED1
#define LED2 47 // LED2
#define LED3 48 // LED3
#define LED4 49 // LED4
unsigned char ledarray[4] = {LED1,LED2,LED3,LED4};

#define LCD_SDA 20 // D20
#define LCD_SDC 21 // D21
unsigned char lcdpins[2] = {LCD_SDA, LCD_SDC};
LiquidCrystal_I2C lcd(0x27,  16, 2);

#define BTN1 11  //
#define BTN2 12  //
#define BTN3 13 //
unsigned char charlieplexed_buttons[3] = {BTN1,BTN2,BTN3};
// Each button definition: {HighPinIndex, LowPinIndex}
int buttonPairs[6][2] = {
  {0, 1}, // Button 1: BTN1 -> BTN2
  {0, 2}, // Button 3: BTN1 -> BTN3
  {1, 0}, // Button 2: BTN2 -> BTN1
  {1, 2}, // Button 5: BTN2 -> BTN3
  {2, 0}, // Button 4: BTN3 -> BTN1
  {2, 1}  // Button 6: BTN3 -> BTN2
};
char buttonstring[] = "BTN:000000";

#define ADC_CH_COUNT 12

#define ADC0_PIN A0
#define ADC1_PIN A1
#define ADC2_PIN A2
#define ADC3_PIN A3
#define ADC4_PIN A4
#define ADC5_PIN A5

#define ADC6_PIN A8
#define ADC7_PIN A9
#define ADC8_PIN A10
#define ADC9_PIN A11
#define ADC10_PIN A12
#define ADC11_PIN A13

const uint8_t adcPins[ADC_CH_COUNT] = {
  ADC0_PIN, ADC1_PIN, ADC2_PIN, ADC3_PIN,
  ADC4_PIN, ADC5_PIN, ADC6_PIN, ADC7_PIN,
  ADC8_PIN, ADC9_PIN, ADC10_PIN, ADC11_PIN
};

uint16_t adcValues[ADC_CH_COUNT];

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network.
// gateway and subnet are optional:
byte mac[] = {  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);
// telnet defaults to port 23
EthernetServer ethServer(502);
ModbusTCPServer modbusTCPServer;
EthernetClient clients[8];

void setup ()
{
  //switchgear
  for(int pin = 0; pin < 8; pin++){
    pinMode(ioarray[pin], OUTPUT);          // sets the digital pin as output
    digitalWrite(ioarray[pin], LOW);        // sets the digital pins off
  }
  //initialize lcd screen
  lcd.init();
  // turn on the backlight
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("Hello world!");

  //leds
  for(int pin = 0; pin < 4; pin++){
    pinMode(ledarray[pin], OUTPUT);          // sets the digital pin as output
    digitalWrite(ledarray[pin], HIGH);        // sets the digital pins off
  }
  //digitalWrite(ledarray[0], HIGH);        // sets the digital pins off
  //digitalWrite(ledarray[3], HIGH);        // sets the digital pins off
  
  //digitalWrite(ledarray[0], HIGH);        // sets the digital pins on
  //charlieplexed buttons
  pinMode(charlieplexed_buttons[0], INPUT);          // sets the digital pin as input
  pinMode(charlieplexed_buttons[1], INPUT);          // sets the digital pin as input
  pinMode(charlieplexed_buttons[2], INPUT);          // sets the digital pin as input
  digitalWrite(charlieplexed_buttons[0], HIGH);      // enable internal pullup
  digitalWrite(charlieplexed_buttons[1], HIGH);      // enable internal pullup
  digitalWrite(charlieplexed_buttons[2], HIGH);      // enable internal pullup

  Ethernet.init(10);  // Most Arduino shields
  Ethernet.begin(mac, ip);
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    if (Ethernet.linkStatus() == LinkOFF) {
    }
    else{
        // start the server
      ethServer.begin();
      // start the Modbus TCP server
      if (!modbusTCPServer.begin()) {
        Serial.println("Failed to start Modbus TCP Server!");
        while (1);
      }
      // configure a single coil at address 0x00
      modbusTCPServer.configureCoils(0x00, 1);
    }
  }
  Serial.begin(115200);
}

// Read a charlieplexed button
bool isButtonPressed(int index) {
  int hi = buttonPairs[index][0];
  int lo = buttonPairs[index][1];
  // Drive selected pins
  pinMode(charlieplexed_buttons[hi], OUTPUT);
  digitalWrite(charlieplexed_buttons[hi], LOW);
  pinMode(charlieplexed_buttons[lo], INPUT);
  digitalWrite(charlieplexed_buttons[lo], HIGH);      // enable internal pullup
  // Let the floating input settle a little
  delayMicroseconds(50);
  // Read the  pin to detect a pressed connection (LOW means pressed)
  int state = digitalRead(charlieplexed_buttons[lo]);
  // reset state to input
  pinMode(charlieplexed_buttons[hi], INPUT);          // sets the digital pin as input
  digitalWrite(charlieplexed_buttons[hi], HIGH);      // enable internal pullup
  return (state == LOW);
}

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

#define WIRE_COUNT 6

const uint16_t ADC_LIVE_THRESHOLD = 120;  // ~0.6V (tweak for noise)
const uint16_t ADC_GND_THRESHOLD = 600;  // ~2.9V (tweak for noise)
const uint16_t ADC_SHORT_THRESHOLD = 750; // ~3.6V (tweak for noise)
const unsigned long PULSE_SETTLE_US = 2;   // settle time when pulling LOW


void detectStatus(bool liveStatus[WIRE_COUNT], bool gndStatus[WIRE_COUNT]) {
  for (uint8_t i = 0; i < WIRE_COUNT; i++) {
    pinMode(adcPins[i], INPUT);       // ensure high-Z
    uint16_t adc = analogRead(adcPins[i]);
    liveStatus[i] = (adc > ADC_LIVE_THRESHOLD); // true if WIRE is LIVE
    if(liveStatus[i])// if wire is live, check for ground-fault
        gndStatus[i] = (adc < ADC_GND_THRESHOLD); // true if shorted to GND
    else
        gndStatus[i] = 0;
  }
}

void detectShorts(bool shortMatrix[WIRE_COUNT][WIRE_COUNT]) {
  // Initialize all to false
  for (uint8_t i = 0; i < WIRE_COUNT; i++)
    for (uint8_t j = 0; j < WIRE_COUNT; j++)
      shortMatrix[i][j] = false;

  for (uint8_t drive = 0; drive < WIRE_COUNT; drive++) {
    // Ensure all other wires are INPUT
    for (uint8_t j = 0; j < WIRE_COUNT; j++)
      pinMode(adcPins[j], INPUT);

    // Drive one wire LOW
    pinMode(adcPins[drive], OUTPUT);
    digitalWrite(adcPins[drive], LOW);

    delayMicroseconds(PULSE_SETTLE_US);

    // Read all other wires
    for (uint8_t sense = 0; sense < WIRE_COUNT; sense++) {
      if (sense == drive) continue; // skip self
      uint16_t adc = analogRead(adcPins[sense]);//110uS
      shortMatrix[drive][sense] = (adc < ADC_SHORT_THRESHOLD); // true if connected
    }

    // Release driven pin
    pinMode(adcPins[drive], INPUT);

    // Optional small delay to avoid ADC ghosting
    //delayMicroseconds(2);
  }
}

void readADC() {
  for (uint8_t i = 0; i < ADC_CH_COUNT; i++) {
    adcValues[i] = analogRead(adcPins[i]);
  }
}

void sendADCPacket() {
  const uint8_t payloadLen = ADC_CH_COUNT * 2;
  uint8_t packet[1 + payloadLen]; // LEN + payload

  packet[0] = payloadLen;

  //Serial.println("values:");
  for (uint8_t i = 0; i < ADC_CH_COUNT; i++) {
    packet[1 + i * 2]     = adcValues[i] & 0xFF;        // LSB
    packet[1 + i * 2 + 1] = adcValues[i] >> 8;          // MSB
    //Serial.println((adcValues[i]*5),DEC);
  }
  //Serial.println("---");
  uint8_t crc = crc8(packet, sizeof(packet));

  // Ensure buffer space before sending (important!)
  /*if (Serial.availableForWrite() >= (2 + sizeof(packet) + 1 + 2)) {
    Serial.write(0xAA);
    Serial.write(0x55);
    Serial.write(packet, sizeof(packet));
    Serial.write(crc);
    Serial.write(0x0D);
    Serial.write(0x0A);
  }*/
}



unsigned long tADC = 0;
const unsigned long ADC_INTERVAL = 1000; // ms

unsigned long tBTN = 0;
const unsigned long BTN_INTERVAL = 50; // ms

unsigned long tSWI = 0;
const unsigned long SWI_INTERVAL = 1000; // ms

void loop() {
  unsigned long now = millis();

  /*if (now - tADC >= ADC_INTERVAL) {
    tADC = now;
    //readADC();
    //sendADCPacket();
    bool liveStatus[WIRE_COUNT];
    bool gndStatus[WIRE_COUNT];
    bool shortMatrix[WIRE_COUNT][WIRE_COUNT];

    detectStatus(liveStatus, gndStatus);
    detectShorts(shortMatrix);
    Serial.print("l:");
    for(int i = 0; i < WIRE_COUNT; i++)
    {
        Serial.print(liveStatus[i],BIN);
    }
    Serial.print(", g:");
    for(int i = 0; i < WIRE_COUNT; i++)
    {
        Serial.print(gndStatus[i],BIN);
    }
    Serial.print(", s:");
    for(int i = 0; i < WIRE_COUNT; i++)
    {
        for(int j = 0; j < WIRE_COUNT; j++){
            Serial.print(shortMatrix[i][j],BIN);
        }
        Serial.print("   ");
    }
    Serial.println();
  }*/
  if (now - tSWI >= SWI_INTERVAL) {
    tSWI = now;

    static int swi_pin_counter = 0;
    digitalWrite(ioarray[(swi_pin_counter % 8)], HIGH);       // sets the digital pin on
    digitalWrite(ioarray[((swi_pin_counter+7) % 8)], LOW);        // sets the previous digital pin off

    if(swi_pin_counter < 7)
      swi_pin_counter++;
    else
      swi_pin_counter = 0;
  }  
  if (now - tBTN >= BTN_INTERVAL) {
    tBTN = now;
    for (int i = 0; i < 6; i++) {
        if (isButtonPressed(i)) {
        buttonstring[4+i] = '1';
        digitalWrite(ledarray[i%4], HIGH);
        }
        else
        {
        buttonstring[4+i] = '0'; 
        digitalWrite(ledarray[i%4], LOW);
        }
        //delay(200); // simple debounce
    }
    lcd.setCursor(0,1);
    lcd.print(buttonstring); 
  }
  //ethernetTask();   // always run this

}