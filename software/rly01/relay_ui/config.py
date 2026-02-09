"""
Configuration and constants for Relay Interface
"""

# =====================================================
# DISPLAY CONFIG
# =====================================================
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480
LCD_W, LCD_H = 480, 272
SCALE = 2
FPS = 30

# =====================================================
# COLORS
# =====================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)
SIEMENS_BLUE = (0, 120, 200)
SIEMENS_DARK_BLUE = (0, 80, 140)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)

# IED LCD Colors
BG = (185, 200, 215)
FG = (35, 50, 85)
INV_BG = FG
INV_FG = BG

# =====================================================
# UNIX SOCKETS
# =====================================================
SOCKET_PATHS = [
    "/tmp/iec61850_relay_1.sock",
    "/tmp/iec61850_relay_2.sock",
    "/tmp/iec61850_relay_3.sock",
    "/tmp/iec61850_relay_4.sock",
    "/tmp/iec61850_relay_5.sock",
    "/tmp/iec61850_relay_6.sock",
]

# =====================================================
# ELEMENT DEFINITIONS (IEC61850 MAPPING)
# =====================================================
# Maps element names to their metadata
ELEMENTS_FEED = {
    # Controllable objects (circuit breakers and switches)
    "cbr1": {
        "type": "breaker",
        "description": "Circuit Breaker 1"
    },
    "swi1": {
        "type": "switch",
        "description": "Switch 1"
    },
    "swi2": {
        "type": "switch",
        "description": "Switch 2"
    },
    "swi3": {
        "type": "switch",
        "description": "Switch 3"
    },
    # Measurement transformers
    "ctr1": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "ctr1_phsA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "ctr1_phsB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "ctr1_phsC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "ctr1_phsAngA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "ctr1_phsAngB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "ctr1_phsAngC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "vtr1": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1"
    },
    "vtr2": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2"
    },
    # Settings
    "set0_loc": {
        "type": "setting",
        "description": "Local/Remote Control"
    },
    "set1_Ilarge": {
        "type": "setting",
        "description": "Overcurrent Pickup"
    },
    "set2_Tm": {
        "type": "setting",
        "description": "Time Multiplier"
    },
}

ELEMENTS = [
    ELEMENTS_FEED,
    ELEMENTS_FEED,
    ELEMENTS_FEED,
    ELEMENTS_FEED,
    ELEMENTS_FEED,
    ELEMENTS_FEED
]

# =====================================================
# SETTINGS MEASUREMENTS AND INDICATORS
# =====================================================
SETTINGS_FEED = [
    ["I> pickup", "set1_Ilarge"],
    ["T> delay", "set2_Tm"],
    ["Local/Remote", "set0_loc"],
]

SETTINGS = [
    SETTINGS_FEED,
    SETTINGS_FEED,
    SETTINGS_FEED,
    SETTINGS_FEED,
    SETTINGS_FEED,
    SETTINGS_FEED
]

MEASUREMENTS_FEED = [
    ("Iph A", "ctr1_phsA", "ctr1_phsAngA"),
    ("Iph B", "ctr1_phsB", "ctr1_phsAngB"),
    ("Iph C", "ctr1_phsC", "ctr1_phsAngC"),
]

MEASUREMENTS = [
    MEASUREMENTS_FEED,
    MEASUREMENTS_FEED,
    MEASUREMENTS_FEED,
    MEASUREMENTS_FEED,
    MEASUREMENTS_FEED,
    MEASUREMENTS_FEED
]

INDICATORS_FEED = [
    "cbr1",
    "swi2",
    "swi3",
    "swi4",
]

INDICATORS_BUS = [
    "cbr1",
    "cbr2",
    "cbr3",
    "cbr4",
]

INDICATORS_TR = [
    "cbr1",
    "swi3",
    "swi4",
]

INDICATORS = [
    INDICATORS_FEED,
    INDICATORS_FEED,
    INDICATORS_BUS,
    INDICATORS_BUS,
    INDICATORS_TR,
    INDICATORS_TR
]

# =====================================================
# DIAGRAM OBJECTS
# =====================================================
DIAGRAM_OBJECTS_FEED = [
    {
        "type": "symbol",
        "name": "busbar",
        "position": (124, 40),
        "rotation": 0,
    },
    {
        "type": "symbol",
        "name": "busbar",
        "position": (124, 60),
        "rotation": 0,
    },        
    {
        "type": "primitive",
        "primitive": {"type": "filled_circle", "center": (80, 41), "radius": 4},
    },
    {
        "type": "primitive",
        "primitive": {"type": "filled_circle", "center": (160, 61), "radius": 4},
    },
    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (80, 40), "end": (80, 80), "width": 2},
    },
    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (160, 60), "end": (160, 80), "width": 2},
    },
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "closed",
        "element": "swi4",
        "position": (80, 100),
        "rotation": 180,
        "selectable": True,
    },   
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "swi3",
        "position": (160, 100),
        "rotation": 180,
        "selectable": True,
    },  
    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (80, 130), "end": (160, 130), "width": 2},
    }, 
    {
        "type": "symbol",
        "name": "circuit_breaker",
        "state": "open",
        "element": "cbr1",
        "position": (120, 160),
        "rotation": 180,
        "selectable": True,
    },  
    {
        "type": "symbol",
        "name": "current_transformer",
        "position": (120, 220),
        "rotation": 0,
    },  
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "swi2",
        "position": (120, 270),
        "rotation": 180,
        "selectable": True,
    },  
]

DIAGRAM_OBJECTS = [
    DIAGRAM_OBJECTS_FEED,
    DIAGRAM_OBJECTS_FEED,
    DIAGRAM_OBJECTS_FEED,
    DIAGRAM_OBJECTS_FEED,
    DIAGRAM_OBJECTS_FEED,
    DIAGRAM_OBJECTS_FEED
]

# =====================================================
# SYMBOL DEFINITIONS
# =====================================================
# Each symbol is centered at origin (0, 0)
SYMBOLS = {
    "circuit_breaker_open": [
        {"type": "line", "start": (0, -30), "end": (0, -20), "width": 2},
        {"type": "line", "start": (0, -20), "end": (25, 5), "width": 2},
        {"type": "line", "start": (-10, 0), "end": (10, 20), "width": 2},
        {"type": "line", "start": (10, 0), "end": (-10, 20), "width": 2},
        {"type": "line", "start": (0, 10), "end": (0, 30), "width": 2},
    ],
    "circuit_breaker_closed": [
        {"type": "line", "start": (0, -30), "end": (0, -20), "width": 2},
        {"type": "filled_circle", "center": (0, -20), "radius": 4},
        {"type": "line", "start": (0, -20), "end": (0, 10), "width": 2},
        {"type": "line", "start": (-10, 0), "end": (10, 20), "width": 2},
        {"type": "line", "start": (10, 0), "end": (-10, 20), "width": 2},
        {"type": "line", "start": (0, 10), "end": (0, 30), "width": 2},
    ],
    "disconnector_open": [
        {"type": "line", "start": (0, -30), "end": (0, -20), "width": 2},
        {"type": "line", "start": (0, -20), "end": (25, 5), "width": 2},
        {"type": "line", "start": (-10, 10), "end": (10, 10), "width": 2},
        {"type": "line", "start": (0, 10), "end": (0, 30), "width": 2},
    ],
    "disconnector_closed": [
        {"type": "line", "start": (0, -30), "end": (0, -20), "width": 2},
        {"type": "filled_circle", "center": (0, -20), "radius": 4},
        {"type": "line", "start": (0, -20), "end": (0, 10), "width": 2},
        {"type": "line", "start": (-10, 10), "end": (10, 10), "width": 2},
        {"type": "line", "start": (0, 10), "end": (0, 30), "width": 2},
    ],
    "current_transformer": [
        {"type": "line", "start": (0, -30), "end": (0, 30), "width": 2},
        {"type": "circle", "center": (0, 0), "radius": 10, "width": 2},
        {"type": "line", "start": (0, -15), "end": (0, 15), "width": 2},
    ],
    "voltage_transformer": [
        {"type": "circle", "center": (0, -10), "radius": 15, "width": 2},
        {"type": "circle", "center": (0, 10), "radius": 15, "width": 2},
        {"type": "line", "start": (0, -40), "end": (0, -25), "width": 2},
        {"type": "line", "start": (0, 25), "end": (0, 40), "width": 2},
    ],
    "power_transformer": [
        {"type": "circle", "center": (0, -10), "radius": 15, "width": 2},
        {"type": "circle", "center": (0, 10), "radius": 15, "width": 2},
        {"type": "line", "start": (0, -40), "end": (0, -25), "width": 2},
        {"type": "line", "start": (0, 25), "end": (0, 40), "width": 2},
    ],
    "earth": [
        {"type": "line", "start": (0, -20), "end": (0, 0), "width": 2},
        {"type": "line", "start": (-10, 0), "end": (10, 0), "width": 2},
        {"type": "line", "start": (-7, 5), "end": (7, 5), "width": 2},
        {"type": "line", "start": (-4, 10), "end": (4, 10), "width": 2},
    ],
    "busbar": [
        {"type": "line", "start": (-120, 0), "end": (120, 0), "width": 4},
    ],
}