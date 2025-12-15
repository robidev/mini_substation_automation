#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <avr/pgmspace.h>

/* ------------------------------------------------------
   LCD (LiquidCrystal_I2C)
------------------------------------------------------ */

LiquidCrystal_I2C lcd(0x27, 16, 2); 
// Change address 0x27 → 0x3F if needed

/* ------------------------------------------------------
   CHARLIEPLEXED BUTTON SETUP
------------------------------------------------------ */

// three I/O pins used for charlieplexing
int charlieplexed_buttons[3] = {8, 9, 10};

// Mapping index → (hi, lo) pairs
int buttonPairs[6][2] = {
  {0, 1}, // Button 0
  {0, 2}, // Button 1
  {1, 0}, // Button 2
  {1, 2}, // Button 3
  {2, 0}, // Button 4
  {2, 1}  // Button 5
};

// Read charlieplexed button index
bool isButtonPressed(int index) {
  int hi = buttonPairs[index][0];
  int lo = buttonPairs[index][1];

  pinMode(charlieplexed_buttons[hi], OUTPUT);
  digitalWrite(charlieplexed_buttons[hi], LOW);

  pinMode(charlieplexed_buttons[lo], INPUT);
  digitalWrite(charlieplexed_buttons[lo], HIGH);   // enable pullup

  delayMicroseconds(50);  // let line settle

  int state = digitalRead(charlieplexed_buttons[lo]);

  // reset pins
  pinMode(charlieplexed_buttons[hi], INPUT);
  digitalWrite(charlieplexed_buttons[hi], HIGH);

  return (state == LOW);
}

/* ------------------------------------------------------
   BUTTON → NAV MAPPING
------------------------------------------------------ */

enum NavEvent {
  NAV_NONE,
  NAV_UP,
  NAV_DOWN,
  NAV_LEFT,
  NAV_RIGHT,
  NAV_ENTER,
  NAV_CANCEL
};

// Your 6 charlieplex buttons mapped to navigation
// Adjust as you prefer
NavEvent buttonMap[6] = {
  NAV_UP,      // button index 0
  NAV_DOWN,    // index 1
  NAV_LEFT,    // index 2
  NAV_RIGHT,   // index 3
  NAV_ENTER,   // index 4
  NAV_CANCEL   // index 5
};

NavEvent readButtons() { // BE AWARE, this routine only returns the FIRST button pressed. multiple simultaneous buttons may have side-effects
  for (int i = 0; i < 6; i++) {
    if (isButtonPressed(i)) {
      return buttonMap[i];
    }
  }
  return NAV_NONE;
}

/* ------------------------------------------------------
   MENU STRUCTURES (PROGMEM)
------------------------------------------------------ */

struct Menu;

struct MenuItem {
  const char *label;         // PROGMEM string
  void (*action)();          // callback
  const Menu *submenu;       // pointer to submenu
};

struct Menu {
  const char *title;         // PROGMEM
  const MenuItem *items;     // PROGMEM
  uint8_t itemCount;
};

/* ------------------------------------------------------
   ACTION PROTOTYPES
------------------------------------------------------ */

void actionToggleSound();
void actionShowTemperature();
void actionShowAbout();

/* ------------------------------------------------------
   STRINGS IN PROGMEM
------------------------------------------------------ */

const char strMainTitle[]        PROGMEM = "Main Menu";
const char strSettings[]         PROGMEM = "Settings";
const char strStatus[]           PROGMEM = "Status";
const char strAbout[]            PROGMEM = "About";

const char strSettingsTitle[]    PROGMEM = "Settings";
const char strSoundToggle[]      PROGMEM = "Sound Toggle";
const char strBack[]             PROGMEM = "Back";

const char strStatusTitle[]      PROGMEM = "Status";
const char strTemperature[]      PROGMEM = "Temp";

/* ------------------------------------------------------
   MENU DEFINITIONS
------------------------------------------------------ */

extern const Menu mainMenu;
extern const Menu settingsMenu;
extern const Menu statusMenu;

// Settings
const MenuItem settingsItems[] PROGMEM = {
  { strSoundToggle,   actionToggleSound,  nullptr },
  { strBack,          nullptr,            nullptr }
};

const Menu settingsMenu = {
  strSettingsTitle,
  settingsItems,
  2
};

// Status
const MenuItem statusItems[] PROGMEM = {
  { strTemperature,   actionShowTemperature, nullptr },
  { strBack,          nullptr,               nullptr }
};

const Menu statusMenu = {
  strStatusTitle,
  statusItems,
  2
};

// Main
const MenuItem mainItems[] PROGMEM = {
  { strSettings, nullptr, &settingsMenu },
  { strStatus,   nullptr, &statusMenu },
  { strAbout,    actionShowAbout, nullptr }
};

const Menu mainMenu = {
  strMainTitle,
  mainItems,
  3
};

/* ------------------------------------------------------
   MENU RUNTIME STATE
------------------------------------------------------ */

const Menu *currentMenu = &mainMenu;
const Menu *parentMenu  = nullptr;
uint8_t currentIndex     = 0;
bool needsRedraw         = true;

/* ------------------------------------------------------
   PROGMEM STRING HANDLING
------------------------------------------------------ */

void printFromPROGMEM(const char *ptr) {
  char buffer[17];
  strcpy_P(buffer, ptr);
  lcd.print(buffer);
}

/* ------------------------------------------------------
   LCD RENDERING
------------------------------------------------------ */

void renderMenu() {
  if (!needsRedraw) return;
  needsRedraw = false;

  lcd.clear();

  // print title
  lcd.setCursor(0, 0);
  printFromPROGMEM(currentMenu->title);

  // selected item
  const MenuItem *item =
    (const MenuItem*)pgm_read_ptr(&currentMenu->items[currentIndex]);

  lcd.setCursor(0, 1);
  lcd.print("> ");

  const char *label =
    (const char*)pgm_read_ptr(&item->label);

  printFromPROGMEM(label);
}

/* ------------------------------------------------------
   MENU NAVIGATION
------------------------------------------------------ */

void processNav(NavEvent e) {
  switch (e) {

    case NAV_UP:
      currentIndex =
        (currentIndex == 0) ?
        currentMenu->itemCount - 1 : currentIndex - 1;
      needsRedraw = true;
      break;

    case NAV_DOWN:
      currentIndex = (currentIndex + 1) % currentMenu->itemCount;
      needsRedraw = true;
      break;

    case NAV_ENTER: {
      const MenuItem *item =
        (const MenuItem*)pgm_read_ptr(&currentMenu->items[currentIndex]);

      const Menu *submenu =
        (const Menu*)pgm_read_ptr(&item->submenu);

      void (*action)() =
        (void (*)()) pgm_read_ptr(&item->action);

      if (submenu) {
        parentMenu = currentMenu;
        currentMenu = submenu;
        currentIndex = 0;
        needsRedraw = true;
        return;
      }

      if (action) {
        action();
        needsRedraw = true;
      }
      break;
    }

    case NAV_CANCEL:
      if (parentMenu != nullptr) {
        currentMenu = parentMenu;
        parentMenu = nullptr;
        currentIndex = 0;
        needsRedraw = true;
      }
      break;

    default:
      break;
  }
}

/* ------------------------------------------------------
   ACTIONS
------------------------------------------------------ */

bool soundEnabled = true;

void actionToggleSound() {
  soundEnabled = !soundEnabled;
  lcd.clear();
  lcd.print("Sound: ");
  lcd.print(soundEnabled ? "ON" : "OFF");
  delay(1000);
}

void actionShowTemperature() {
  int temperature = 23;
  lcd.clear();
  lcd.print("Temp: ");
  lcd.print(temperature);
  lcd.print("C");
  delay(1200);
}

void actionShowAbout() {
  lcd.clear();
  lcd.print("Device v1.0");
  lcd.setCursor(0, 1);
  lcd.print("(c) 2025");
  delay(1200);
}

/* ------------------------------------------------------
   SETUP & LOOP
------------------------------------------------------ */

void setup() {
  lcd.init();
  lcd.backlight();

  // charlieplex pins default to INPUT_PULLUP
  for (int i = 0; i < 3; i++) {
    pinMode(charlieplexed_buttons[i], INPUT_PULLUP);
  }

  needsRedraw = true;
}

void loop() {
  NavEvent e = readButtons();
  if (e != NAV_NONE) {
    processNav(e);
    delay(150);  // debounce
  }

  renderMenu();
}
