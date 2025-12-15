#include <LiquidCrystal.h>

/* ------------------------------------------------------
   PIN SETUP
------------------------------------------------------ */
// Adjust to your wiring:
const int PIN_UP = 2;
const int PIN_DOWN = 3;
const int PIN_LEFT = 4;
const int PIN_RIGHT = 5;
const int PIN_ENTER = 6;
const int PIN_CANCEL = 7;

LiquidCrystal lcd(8, 9, 10, 11, 12, 13);  // RS,E,D4,D5,D6,D7

/* ------------------------------------------------------
   MENU STRUCTURES
------------------------------------------------------ */

struct Menu;   // forward declaration

struct MenuItem {
  const char *label;
  void (*action)();   // function pointer if action item
  Menu *submenu;      // submenu pointer if menu item
};

struct Menu {
  const char *title;
  MenuItem *items;
  uint8_t itemCount;
};

/* ------------------------------------------------------
   FORWARD DECLARATIONS OF ACTION FUNCTIONS
------------------------------------------------------ */
void actionShowAbout();
void actionShowTemperature();
void actionToggleSound();

/* ------------------------------------------------------
   MENU DEFINITIONS
------------------------------------------------------ */

// --- Submenu: Settings ---
MenuItem settingsItems[] = {
  {"Sound On/Off", actionToggleSound, nullptr},
  {"Back", nullptr, nullptr}
};

Menu settingsMenu = {
  "Settings",
  settingsItems,
  2
};

// --- Submenu: Status ---
MenuItem statusItems[] = {
  {"Temp", actionShowTemperature, nullptr},
  {"Back", nullptr, nullptr}
};

Menu statusMenu = {
  "Status",
  statusItems,
  2
};

// --- Main Menu ---
MenuItem mainItems[] = {
  {"Settings", nullptr, &settingsMenu},
  {"Status", nullptr, &statusMenu},
  {"About", actionShowAbout, nullptr}
};

Menu mainMenu = {
  "Main Menu",
  mainItems,
  3
};

/* ------------------------------------------------------
   MENU STATE MACHINE
------------------------------------------------------ */

Menu *currentMenu = &mainMenu;
Menu *parentMenu = nullptr;
uint8_t currentIndex = 0;
bool needsRedraw = true;

/* ------------------------------------------------------
   BUTTON HANDLING
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

bool readButton(int pin) {
  return digitalRead(pin) == LOW;  // assume pull-up buttons
}

NavEvent readButtons() {
  if (readButton(PIN_UP)) return NAV_UP;
  if (readButton(PIN_DOWN)) return NAV_DOWN;
  if (readButton(PIN_LEFT)) return NAV_LEFT;
  if (readButton(PIN_RIGHT)) return NAV_RIGHT;
  if (readButton(PIN_ENTER)) return NAV_ENTER;
  if (readButton(PIN_CANCEL)) return NAV_CANCEL;
  return NAV_NONE;
}

/* ------------------------------------------------------
   MENU NAVIGATION LOGIC
------------------------------------------------------ */

void processNav(NavEvent e) {
  switch (e) {

    case NAV_UP:
      currentIndex = (currentIndex == 0)
                     ? currentMenu->itemCount - 1
                     : currentIndex - 1;
      needsRedraw = true;
      break;

    case NAV_DOWN:
      currentIndex = (currentIndex + 1) % currentMenu->itemCount;
      needsRedraw = true;
      break;

    case NAV_ENTER: {
      MenuItem *item = &currentMenu->items[currentIndex];

      // Enter submenu
      if (item->submenu != nullptr) {
        parentMenu = currentMenu;
        currentMenu = item->submenu;
        currentIndex = 0;
        needsRedraw = true;
        return;
      }

      // Run action
      if (item->action != nullptr) {
        item->action();
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
   LCD RENDERING
------------------------------------------------------ */

void renderMenu() {
  if (!needsRedraw) return;
  needsRedraw = false;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(currentMenu->title);

  lcd.setCursor(0, 1);
  lcd.print("> ");
  lcd.print(currentMenu->items[currentIndex].label);
}

/* ------------------------------------------------------
   ACTION IMPLEMENTATIONS
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
  // Fake temperature for demonstration
  int temperature = 23;

  lcd.clear();
  lcd.print("Temp: ");
  lcd.print(temperature);
  lcd.print("C");
  delay(1500);
}

void actionShowAbout() {
  lcd.clear();
  lcd.print("Device v1.0");
  lcd.setCursor(0,1);
  lcd.print("(c) 2025");
  delay(1500);
}

/* ------------------------------------------------------
   SETUP AND MAIN LOOP
------------------------------------------------------ */

void setup() {
  lcd.begin(16, 2);

  pinMode(PIN_UP, INPUT_PULLUP);
  pinMode(PIN_DOWN, INPUT_PULLUP);
  pinMode(PIN_LEFT, INPUT_PULLUP);
  pinMode(PIN_RIGHT, INPUT_PULLUP);
  pinMode(PIN_ENTER, INPUT_PULLUP);
  pinMode(PIN_CANCEL, INPUT_PULLUP);

  currentMenu = &mainMenu;
  currentIndex = 0;
  needsRedraw = true;
}

void loop() {
  NavEvent e = readButtons();
  if (e != NAV_NONE) {
    processNav(e);
    delay(150); // basic debounce
  }

  renderMenu();
}
