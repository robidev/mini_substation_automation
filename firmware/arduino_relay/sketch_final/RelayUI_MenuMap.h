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

// 6 charlieplex buttons mapped to navigation
NavEvent buttonMap[6] = {
  NAV_UP,      // 
  NAV_DOWN,    // 
  NAV_LEFT,    // 
  NAV_RIGHT,   // 
  NAV_ENTER,   // 
  NAV_CANCEL   // 
};

/* ------------------------------------------------------
   MENU STRUCTURES
------------------------------------------------------ */

struct Menu;

struct MenuItem {
  const char *label;         // PROGMEM string
  void (*action)();          // callback
  const Menu *submenu;       // pointer to submenu
};

struct Menu {
  const char *title;         // PROGMEM
  const MenuItem *items;     
  uint8_t itemCount;
  void (*renderMenuFn)();    // function to render this menu
  const Menu *parentMenu;
  uint8_t parentIndex;
};

/* ------------------------------------------------------
   ACTION PROTOTYPES
------------------------------------------------------ */

void actionSelectRTU();
void actionShowStatus();

void actionShowMeasurementsVT();
void actionShowMeasurementsCT();
void actionShowBreakerControl();
void actionShowTripHistory();

void actionControlMode();
void actionShowAbout();

/* ------------------------------------------------------
   RENDERMENU PROTOTYPES
------------------------------------------------------ */

void renderMenuMain();
void renderMenuRTU();
void renderConfirmMenu();


/* ------------------------------------------------------
   STRINGS IN PROGMEM
------------------------------------------------------ */

const char strMainTitle[]        PROGMEM = "Main Menu";
const char strRTU1[]             PROGMEM = "Feed RTU blue";
const char strRTU2[]             PROGMEM = "Bus Voltage blue";
const char strRTU3[]             PROGMEM = "Bay RTU blue-1";
const char strRTU4[]             PROGMEM = "Bay RTU blue-2";
const char strRTU5[]             PROGMEM = "Bay RTU blue-3";
const char strRTU6[]             PROGMEM = "Feed RTU red";
const char strRTU7[]             PROGMEM = "Bus voltage red";
const char strRTU8[]             PROGMEM = "Bay RTU red-1";
const char strRTU9[]             PROGMEM = "Bay RTU red-2";
const char strRTU10[]            PROGMEM = "Bay RTU red-3";

const char strMainRTUTitle[]     PROGMEM = "Main RTU Menu";
const char strMainMeasureTitle[] PROGMEM = "Measure Menu";
const char strStatus[]           PROGMEM = "Status";
const char strMeasurements[]     PROGMEM = "Measurements";
const char strBreakerControl[]   PROGMEM = "Breaker Control";
const char strTripHistory[]      PROGMEM = "Trip History";
const char strSettings[]         PROGMEM = "Settings";
const char strAbout[]            PROGMEM = "About";

const char strSettingsTitle[]    PROGMEM = "Settings";
const char strControlMode[]      PROGMEM = "Control Mode";
const char strBack[]             PROGMEM = "Back";

const char strOpen[]             PROGMEM = "Open Breaker";
const char strClose[]            PROGMEM = "Close Breaker";
const char strReset[]            PROGMEM = "Reset Trip";

const char strOk[]               PROGMEM = "<OK>     Cancel ";
const char strCancel[]           PROGMEM = " OK     <Cancel>";

/* ------------------------------------------------------
   MENU DEFINITIONS
------------------------------------------------------ */

extern const Menu mainMenu;
extern const Menu mainRTUMenu;
extern const Menu mainMeasureMenu;
extern const Menu breakerMenu;
extern const Menu settingsMenu;
extern Menu confirmMenu;

// Confirm an action
const MenuItem confirmItems[] = {
  { strOk,              actionShowBreakerControl,    nullptr },
  { strCancel,          nullptr,                     nullptr }
};

//not const, as we rewrite the parent and index dynamic to know where the dialog came from
Menu confirmMenu = {
  nullptr, //signal navevents this is a dialog
  confirmItems,
  2,
  renderConfirmMenu,
  nullptr,// set dynamic
  0       // set dynamic
};


// Breaker control
const MenuItem breakerItems[] = {
  { strOpen,          nullptr,    &confirmMenu },
  { strClose,         nullptr,    &confirmMenu },
  { strReset,         nullptr,    &confirmMenu },
  { strBack,          nullptr,        nullptr }
};

const Menu breakerMenu = {
  strBreakerControl,
  breakerItems,
  4,
  renderMenuRTU,
  &mainRTUMenu,
  2
};

// Settings
const MenuItem settingsItems[] = {
  { strControlMode,   actionControlMode,  nullptr },
  { strBack,          nullptr,            nullptr }
};

const Menu settingsMenu = {
  strSettingsTitle,
  settingsItems,
  2,
  renderMenuRTU,
  &mainRTUMenu,
  4
};

// Main Measure menu
const MenuItem mainMeasureItems[] = {
  { strMeasurements,   actionShowMeasurementsVT, nullptr },
  { strAbout,          actionShowAbout, nullptr }
};

const Menu mainMeasureMenu = {
  strMainMeasureTitle,
  mainMeasureItems,
  2,
  renderMenuRTU,
  &mainMenu,
  0
};

// Main RTU menu
const MenuItem mainRTUItems[] = {
  { strStatus,         actionShowStatus, nullptr },
  { strMeasurements,   actionShowMeasurementsCT, nullptr },
  { strBreakerControl, nullptr, &breakerMenu },
  { strTripHistory,    actionShowTripHistory, nullptr },
  { strSettings,       nullptr, &settingsMenu },
  { strAbout,          actionShowAbout, nullptr }
};

const Menu mainRTUMenu = {
  strMainRTUTitle,
  mainRTUItems,
  6,
  renderMenuRTU,
  &mainMenu,
  0
};

// Main menu
const MenuItem mainItems[] = {
  { strRTU1, actionSelectRTU, &mainRTUMenu },
  { strRTU2, actionSelectRTU, &mainMeasureMenu },
  { strRTU3, actionSelectRTU, &mainRTUMenu },
  { strRTU4, actionSelectRTU, &mainRTUMenu },
  { strRTU5, actionSelectRTU, &mainRTUMenu },
  { strRTU6, actionSelectRTU, &mainRTUMenu },
  { strRTU7, actionSelectRTU, &mainMeasureMenu },
  { strRTU8, actionSelectRTU, &mainRTUMenu },
  { strRTU9, actionSelectRTU, &mainRTUMenu },
  { strRTU10, actionSelectRTU, &mainRTUMenu },
};

const Menu mainMenu = {
  strMainTitle,
  mainItems,
  10,
  renderMenuMain,
  nullptr,
  0
};

