#include <Ethernet.h>
#include <ArduinoModbus.h>

#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#define RED1 0
#define RED2 1
#define RED3 2
#define RED4 3
#define BLUE1 4
#define BLUE2 5
#define BLUE3 6
#define BLUE4 7
unsigned char ioarray[8] = {PIN0, PIN1, PIN2, PIN3, PIN4, PIN5, PIN6, PIN7};

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

void loop() {
  /*for(int pin = 0; pin < 8; pin++)
  {
    digitalWrite(ioarray[pin], HIGH);       // sets the digital pin on
    delay(1000);                  // waits for a second
    digitalWrite(ioarray[pin], LOW);        // sets the digital pin off
    delay(1000);                  // waits for a second
  }*/
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