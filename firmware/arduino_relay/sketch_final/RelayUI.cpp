#include "RelayUI.h"
#include "RtuLogic.h"
#include "Pins.h"
#include "Config.h"

//menu structure, items, action and navigation defintions
#include "RelayUI_MenuMap.h"

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <avr/pgmspace.h>


LiquidCrystal_I2C lcd(LCD_ADDRESS,  LCD_CHARACTERS, LCD_LINES);

unsigned long tUI = 0;
NavEvent old_event = NAV_NONE;

// Read charlieplexed button index
bool isButtonPressed(int index) {
  int hi = buttonPairs[index][0];
  int lo = buttonPairs[index][1];
  // Drive selected pins
  pinMode(charlieplexed_buttons[hi], OUTPUT);
  digitalWrite(charlieplexed_buttons[hi], LOW);

  pinMode(charlieplexed_buttons[lo], INPUT);
  digitalWrite(charlieplexed_buttons[lo], HIGH);   // enable internal pullup

  delayMicroseconds(50);  // let line settle

  // Read the  pin to detect a pressed connection (LOW means pressed)
  int state = digitalRead(charlieplexed_buttons[lo]);

  // reset state to input
  pinMode(charlieplexed_buttons[hi], INPUT);     // sets the digital pin as input
  digitalWrite(charlieplexed_buttons[hi], HIGH); // enable internal pullup

  return (state == LOW);
}

NavEvent readButtons() { // BE AWARE, this routine only returns the FIRST button pressed. multiple simultaneous buttons may have side-effects
  for (int i = 0; i < 6; i++) {
    if (isButtonPressed(i)) {
      return buttonMap[i];
    }
  }
  return NAV_NONE;
}

/* ------------------------------------------------------
   MENU RUNTIME STATE
------------------------------------------------------ */

const Menu *currentMenu  = &mainMenu;
uint8_t currentIndex     = 0;
bool needsRedraw         = true;
uint8_t currentRTU       = 255;
long delayedRedraw       = 0;

/* ------------------------------------------------------
   PROGMEM STRING HANDLING
   takes optional padding parameter until the value provided
   default and max is 16(lenght of LCD line), 0 means no padding
------------------------------------------------------ */

uint8_t printFromPROGMEM(const char *ptr, uint8_t pad_until = 16) {
  char buffer[17];
  if(pad_until > 16)
    pad_until = 16;
  // Copy up to 16 chars from PROGMEM
  uint8_t len = strncpy_P(buffer, ptr, 16) ? strlen_P(ptr) : 0;

  // Pad with spaces
  for (uint8_t i = len; i < pad_until; i++) {
    buffer[i] = ' ';
  }

  // Zero terminate
  if(len > pad_until)
    buffer[len] = '\0';
  else
    buffer[pad_until] = '\0';

  return lcd.print(buffer);
}

uint8_t lcd_print(const char *ptr, uint8_t pad_until = 16) {
  char buffer[17];
  if(pad_until > 16)
    pad_until = 16;

  uint8_t len = lcd.print(ptr);

  if(len < pad_until)
  {
    // Pad with spaces
    for (uint8_t i = 0; i < (pad_until-len); i++) {
      buffer[i] = ' ';
    }
    buffer[pad_until] = '\0';
    len += lcd.print(buffer);
  }
  return len;
}



/* ------------------------------------------------------
   LCD RENDERING
------------------------------------------------------ */

void renderMenuMain() {
  lcd.setCursor(0, 0);
  lcd.print("                ");
  lcd.setCursor(0, 1);
  const MenuItem &item = currentMenu->items[currentIndex];
  printFromPROGMEM(item.label);

  lcd.setCursor(currentIndex+3, 0);
  lcd.write((uint8_t)0);
}

void renderMenuRTU() {
  // print title
  lcd.setCursor(0, 0);
  printFromPROGMEM(currentMenu->title);

  lcd.setCursor(0, 1);
  uint8_t len = lcd_print("> ",0);

  const MenuItem &item = currentMenu->items[currentIndex];
  printFromPROGMEM(item.label, 16-len);
}

void renderConfirmMenu() {
  lcd.setCursor(0, 0);
  //print the previous menu-item
  const MenuItem &pitem = currentMenu->parentMenu->items[currentMenu->parentIndex];
  uint8_t len = lcd_print("[",0);
  len += printFromPROGMEM(pitem.label,0);
  lcd_print("]",16-len);
  lcd.setCursor(0, 1);

  const MenuItem &item = currentMenu->items[currentIndex];
  printFromPROGMEM(item.label);
}

void renderMenu() {
  if(delayedRedraw > 0) // we have a delayed redraw action
  {
    if (millis() >= delayedRedraw) {
      needsRedraw = true; // redraw the menu
      delayedRedraw = 0;
    }
  }

  if (!needsRedraw) return;
  needsRedraw = false;

  if(currentMenu->renderMenuFn)
  {
    currentMenu->renderMenuFn();
  }
  else
  {
    lcd.clear();
    lcd_print("ERROR: no menu");
  }
}

/* ------------------------------------------------------
   MENU NAVIGATION
------------------------------------------------------ */

void processNav(NavEvent e) {
  switch (e) {

    case NAV_UP:
    case NAV_LEFT:
      currentIndex =
        (currentIndex == 0) ? currentMenu->itemCount - 1 : currentIndex - 1;
      needsRedraw = true;
      break;

    case NAV_DOWN:
    case NAV_RIGHT:
      currentIndex = (currentIndex + 1) % currentMenu->itemCount;
      needsRedraw = true;
      break;

    case NAV_ENTER: {
      const MenuItem *item = &currentMenu->items[currentIndex];
      Menu *submenu = item->submenu;
      void (*action)() = item->action;

      if (action) {
        action();
      }
      if (submenu) {
        if(submenu->title == nullptr) //if no title, we use it for dynamic dialogs that can come from more then 1 origin
        { //then we set dynamically the parentmenu and parentindex
          submenu->parentIndex = currentIndex;
          submenu->parentMenu = currentMenu;
        }

        currentMenu = submenu;
        currentIndex = 0;
        needsRedraw = true;
      }
      if(!submenu && !action) //no action nor submenu means back-button
      {
        currentIndex = currentMenu->parentIndex;
        currentMenu = currentMenu->parentMenu;
        needsRedraw = true;
      }
      break;
    }

    case NAV_CANCEL: //back to top menu
      if(currentMenu != &mainMenu)
      {
        currentMenu = &mainMenu;
        if(currentRTU != 255)
          currentIndex = currentRTU;
        else
          currentIndex = 0;
      }
      else // we're at top menu, so set index to 0
      {
        currentIndex = 0;
        currentRTU = 255;
      }

      needsRedraw = true;
      break;

    default:
      break;
  }
}

/* ------------------------------------------------------
   ACTIONS
------------------------------------------------------ */

void actionSelectRTU() {
  currentRTU = currentIndex;
}

void actionControlMode() {
  relay_state *relay = getRelayDataByIndex(currentRTU);
  relay->remote = !relay->remote;
  lcd.setCursor(0, 0);
  lcd_print("Control:");
  lcd.setCursor(0, 1);
  lcd_print(relay->remote? "Remote" : "Local" );
}

void actionShowStatus() {
  uint8_t len = 0;
  relay_state *relay = getRelayDataByIndex(currentRTU);
  BreakerEvent breaker = (relay->tripState ? BREAKER_TRIPPED : (relay->breakerState? BREAKER_CLOSED : BREAKER_OPEN));
  bool trip = relay->tripState;
  bool fault = relay->faultState;

  lcd.setCursor(0, 0);
  len = lcd_print("Breaker: ",0); 
  switch(breaker)
  {
    case BREAKER_OPEN:
      lcd_print("OPEN", 16-len);
    break;
    case BREAKER_CLOSED:
      lcd_print("CLOSED", 16-len);
    break;
    case BREAKER_TRIPPED:
      lcd_print("TRIPPED", 16-len);
    break;
    default:
      lcd_print("error", 16-len);
    break;
  }
  lcd.setCursor(0, 1);
  len = lcd_print("Trip:",0); 
  len += lcd_print(trip ? "Y" : "N",0);

  len += lcd_print("  Fault:",0); 
  lcd_print(fault ? "Y" : "N", 16-len);
}

void actionShowMeasurementsVT()
{
  relay_state *relay = getRelayDataByIndex(currentRTU);
  lcd.setCursor(0, 0);
  lcd_print("U1:",0);
  lcd.print(relay->Measurement[0]);
  lcd_print(" ");
  lcd.setCursor(8, 0);
  lcd_print("U2:",0);
  lcd.print(relay->Measurement[1]);
  lcd.setCursor(0, 1);
  lcd_print("U3:",0);
  lcd.print(relay->Measurement[2]);
  lcd_print(" ");
  lcd.setCursor(8, 1);
  lcd_print("Un:",0);
  lcd.print(relay->Measurement[3]);
  lcd_print(" ",7);
}

void actionShowMeasurementsCT()
{
  relay_state *relay = getRelayDataByIndex(currentRTU);
  lcd.setCursor(0, 0);
  lcd_print("I1:",0);
  lcd.print(relay->Measurement[0]);
  lcd_print(" ");
  lcd.setCursor(8, 0);
  lcd_print("I2:",0);
  lcd.print(relay->Measurement[1]);
  lcd_print(" ",7);
  lcd.setCursor(0, 1);
  lcd_print("I3:",0);
  lcd.print(relay->Measurement[2]);
  lcd_print(" ");
  lcd.setCursor(8, 1);
  lcd_print("In:",0);
  lcd.print(relay->Measurement[3]);
  lcd_print(" ",7);
}

void actionShowBreakerControl()
{
  bool error = false;
  relay_state *relay = getRelayDataByIndex(currentRTU);
  switch(currentMenu->parentIndex)
  {
    case 0:
      if(relay->breakerState == true) {
        process_breaker(relay, 1, LOCAL); //open breaker
      }
      else
      {
        error = true;
        lcd.setCursor(0, 0);
        lcd_print("operation failed!");
        lcd.setCursor(0, 1);
        lcd_print("already open");
      }
    break;
    case 1:
      if(relay->breakerState == false) {
        if(relay->tripState == false) {
          if(relay->faultState == false) {
            process_breaker(relay, 2, LOCAL); //close breaker
          }
          else
          {
            error = true;
            lcd.setCursor(0, 0);
            lcd_print("operation failed!");
            lcd.setCursor(0, 1);
            lcd_print("fault not clear");
          }
        }
        else
        {
          error = true;
          lcd.setCursor(0, 0);
          lcd_print("operation failed!");
          lcd.setCursor(0, 1);
          lcd_print("reset trip first");
        }
      }
      else
      {
        error = true;
        lcd.setCursor(0, 0);
        lcd_print("operation failed!");
        lcd.setCursor(0, 1);
        lcd_print("already closed");
      }
    break;
    case 2:
      if(relay->tripState == true) {
        if(relay->faultState == false) {
          process_trip(relay, 1, LOCAL); //reset trip
        }
        else
        {
          error = true;
          lcd.setCursor(0, 0);
          lcd_print("operation failed!");
          lcd.setCursor(0, 1);
          lcd_print("fault not clear");
        }
      }
      else
      {
        error = true;
        lcd.setCursor(0, 0);
        lcd_print("operation failed!");
        lcd.setCursor(0, 1);
        lcd_print("not tripped");
      }
    break;
    default:
    return;
  }
  if(!error)//check was ok
  {
    lcd.setCursor(0, 0);
    lcd_print("Action executed");
    lcd.setCursor(0, 1);
    lcd_print("succesfull");
  }

  delayedRedraw = millis() + 5000; //display message for 5 seconds
  //go back to previous menu
  currentIndex = currentMenu->parentIndex;
  currentMenu = currentMenu->parentMenu;
}

void actionShowTripHistory()
{
  relay_state *relay = getRelayDataByIndex(currentRTU);
  lcd.setCursor(0, 0);
  switch(relay->faultEvent)
  {
    case   None:
      lcd_print("Last Trip: None");
    break;
    case   Phase_OC:
      lcd_print("Last Trip:Phase OC");
    break;
    case   Earth_fault:
      lcd_print("Last Trip:Earth");
    break;
    default:
      lcd_print("Last Trip:Unknown");
  }

  lcd.setCursor(0, 1);
  lcd_print("Time:",0);
  lcd.print(relay->faultTime);
  lcd_print("ms",10);
}

void actionShowAbout() {
  lcd.setCursor(0, 0);
  uint8_t len = lcd_print("Device No.",0);
  len += lcd.print(currentRTU+1, DEC);
  lcd_print(" ",16-len);
  lcd.setCursor(0, 1);
  lcd_print("(c) 2026");
}

/* ------------------------------------------------------
   SETUP & LOOP
------------------------------------------------------ */

void RelayUI_init() {
  //initialize lcd screen
  lcd.init();
  // turn on the backlight
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd_print("Initialising...");
  lcd.createChar(0, lcd_upArrow);  // store at index 0

  // charlieplex pins default to INPUT_PULLUP
  for (int i = 0; i < 3; i++) {
    pinMode(charlieplexed_buttons[i], INPUT_PULLUP);
  }

  //UI leds
  for(int pin = 0; pin < 4; pin++){
    pinMode(ledarray[pin], OUTPUT);          // sets the digital pin as output
    digitalWrite(ledarray[pin], HIGH);        // sets the digital pins off
  }

  needsRedraw = true;
}

void RelayUI_tick() {
  unsigned long now = millis();
  if (now - tUI < UI_PERIOD_MS) // slow the refresh cycle, and also helps to debounce the switches!
    return;
  tUI = now;
  
  NavEvent e = readButtons();
  if (e != NAV_NONE && old_event == NAV_NONE) {
    processNav(e);
  }
  old_event = e;
  renderMenu();
}
