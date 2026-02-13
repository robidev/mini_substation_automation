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
RELAY_BLUE = (0, 120, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)

# IED LCD Colors
BG = (185, 200, 215)
FG = (35, 50, 85)
INV_BG = FG
INV_FG = BG

DBPOS_INTERMEDIATE = 0 # moving
DBPOS_ON = 1  # closed
DBPOS_OFF = 2 # open
DBPOS_BAD = 3 # error


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
    "swi2": {
        "type": "switch",
        "description": "Switch 2"
    },
    "s_swi2_blkopn": {
        "type": "status",
        "description": "Switch 2 interlock condition for switch OPEN"
    },
    "s_swi2_blkcls": {
        "type": "status",
        "description": "Switch 2 interlock condition for switch CLOSE"
    },
    "swi3": {
        "type": "switch",
        "description": "Switch 3"
    },
    "swi4": {
        "type": "switch",
        "description": "Switch 4"
    },
    # Measurement transformers
    "ctr1": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 average A"
    },
    "m_ctr1_phsA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "m_ctr1_phsB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "m_ctr1_phsC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "m_ctr1_phsAngA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "m_ctr1_phsAngB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "m_ctr1_phsAngC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1"
    },
    "vtr1": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 average V"
    },

    "m_v1_pA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1"
    },
    "m_v1_pB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1"
    },
    "m_v1_pC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1"
    },
    "m_v1_aA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1"
    },
    "m_v1_aB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1"
    },
    "m_v1_aC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1"
    },

    "vtr2": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2 average V"
    },

    "m_v2_pA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2"
    },
    "m_v2_pB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2"
    },
    "m_v2_pC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2"
    },
    "m_v2_aA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2"
    },
    "m_v2_aB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2"
    },
    "m_v2_aC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 2"
    },

    # Settings
    "loc": {
        "type": "setting",
        "description": "Local/Remote Control"
    },
    "s_Ilarge": {
        "type": "setting",
        "description": "Overcurrent Pickup"
    },
    "s_Tm": {
        "type": "setting",
        "description": "Time Multiplier"
    },
}

ELEMENTS_BUS = {
    # Measurement transformers
    "ctr1": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 average A"
    },
    "ctr2": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 average A"
    },
    "ctr3": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 average A"
    },
    "ctr4": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 average A"
    },
    "vtr1": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 average V"
    },


    # Settings
    "loc": {
        "type": "setting",
        "description": "Local/Remote Control"
    },
}

ELEMENTS = [
    ELEMENTS_FEED,
    ELEMENTS_FEED,
    ELEMENTS_BUS,
    ELEMENTS_BUS,
    ELEMENTS_FEED,
    ELEMENTS_FEED
]

# =====================================================
# SETTINGS MEASUREMENTS AND INDICATORS
# =====================================================
SETTINGS_FEED = [
    ["I> pickup",    "s_Ilarge", float, 0.0],
    ["T> delay",     "s_Tm",     float, 0.0],
    ["Local/Remote", "loc",    bool,  False],
]

SETTINGS_BUS = [
    ["Local/Remote", "loc",    bool,  False],
]

SETTINGS = [
    SETTINGS_FEED,
    SETTINGS_FEED,
    SETTINGS_BUS,
    SETTINGS_BUS,
    SETTINGS_FEED,
    SETTINGS_FEED
]

MEASUREMENTS_FEED = [
    ("Iph A", "m_ctr1_phsA", "m_ctr1_phsAngA"),
    ("Iph B", "m_ctr1_phsB", "m_ctr1_phsAngB"),
    ("Iph C", "m_ctr1_phsC", "m_ctr1_phsAngC"),
    ("Bus1 Vph A", "m_v1_pA", "m_v1_aA"),
    ("Bus1 Vph B", "m_v1_pB", "m_v1_aB"),
    ("Bus1 Vph C", "m_v1_pC", "m_v1_aC"),
    ("Bus2 Vph A", "m_v2_pA", "m_v2_aA"),
    ("Bus2 Vph B", "m_v2_pB", "m_v2_aB"),
    ("Bus2 Vph C", "m_v2_pC", "m_v2_aC"),
]

MEASUREMENTS_BUS = []
MEASUREMENTS_TR = []

MEASUREMENTS = [
    MEASUREMENTS_FEED,
    MEASUREMENTS_FEED,
    MEASUREMENTS_BUS,
    MEASUREMENTS_BUS,
    MEASUREMENTS_TR,
    MEASUREMENTS_TR
]

INDICATORS_FEED = [
    ("cbr1","cbr1","swi"),
    ("swi2","swi2","swi"),
    ("swi3","swi3","swi"),
    ("swi4","swi4","swi"),
    ("Loc","loc","bool"),
    ("conn", "connected","bool")    
]

INDICATORS_BUS = [
    ("Loc","loc","bool"),
    ("conn", "connected","bool")  
]

INDICATORS_TR = [
    ("cbr1","cbr1","swi"),
    ("swi2","swi2","swi"),
    ("swi3","swi3","swi"),
    ("Loc","loc","bool"),
    ("conn", "connected","bool")  
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
        "element": "swi3",
        "position": (80, 100),
        "rotation": 180,
        "selectable": True,
    },   
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "swi4",
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
        "BlkOpn": "_swi2_blkopn",
        "BlkCls": "_swi2_blkcls",
        "position": (120, 270),
        "rotation": 180,
        "selectable": True,
    },  
    {
        "type": "text",
        "position": (140, 210),    
        "formatted_text" : "",
        "element": "ctr1",
        "template": "CT 1:{value:.1f} A",
    },
    {
        "type": "text",
        "position": (140, 22),    
        "formatted_text" : "",
        "element": "vtr1",
        "template": "Bus 1:{value:.1f} V",
    },
    {
        "type": "text",
        "position": (140, 42),    
        "formatted_text" : "",
        "element": "vtr2",
        "template": "Bus 2:{value:.1f} V",
    },
]


DIAGRAM_OBJECTS_BUS = [
    {
        "type": "symbol",
        "name": "busbar",
        "position": (124, 40),
        "rotation": 0,
    },    
    {
        "type": "text",
        "position": (20, 150),    
        "formatted_text" : "",
        "element": "ctr1",
        "template": "CT 1:{value:.1f} A",
    },
    {
        "type": "text",
        "position": (60, 170),    
        "formatted_text" : "",
        "element": "ctr2",
        "template": "CT 2:{value:.1f} A",
    },
    {
        "type": "text",
        "position": (100, 190),    
        "formatted_text" : "",
        "element": "ctr3",
        "template": "CT 3:{value:.1f} A",
    },
    {
        "type": "text",
        "position": (140, 210),    
        "formatted_text" : "",
        "element": "ctr4",
        "template": "CT 4:{value:.1f} A",
    },
    {
        "type": "text",
        "position": (140, 22),    
        "formatted_text" : "",
        "element": "vtr1",
        "template": "Bus:{value:.1f} V",
    },
]

DIAGRAM_OBJECTS_TR = [
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
        "element": "swi2",
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
        "name": "power_transformer",
        "position": (120, 270),
        "rotation": 180,
    },  
    {
        "type": "text",
        "position": (140, 210),    
        "formatted_text" : "",
        "element": "ctr1",
        "template": "CT 1:{value:.1f} A",
    },
    {
        "type": "text",
        "position": (140, 22),    
        "formatted_text" : "",
        "element": "vtr1",
        "template": "Bus 1:{value:.1f} V",
    },
    {
        "type": "text",
        "position": (140, 42),    
        "formatted_text" : "",
        "element": "vtr2",
        "template": "Bus 2:{value:.1f} V",
    },
]



DIAGRAM_OBJECTS = [
    DIAGRAM_OBJECTS_FEED,
    DIAGRAM_OBJECTS_FEED,
    DIAGRAM_OBJECTS_BUS,
    DIAGRAM_OBJECTS_BUS,
    DIAGRAM_OBJECTS_TR,
    DIAGRAM_OBJECTS_TR
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
    "circuit_breaker_intermediate": [
        {"type": "line", "start": (0, -30), "end": (0, -20), "width": 2},
        {"type": "line", "start": (0.0, -20.0), "end": (2.395, -14.601),  "width": 2},
        {"type": "line", "start": (4.79, -9.202), "end": (7.185, -3.803),  "width": 2},
        {"type": "line", "start": (9.58, 1.596), "end": (12.0, 7.0), "width": 2},
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
    "disconnector_intermediate": [
        {"type": "line", "start": (0, -30), "end": (0, -20), "width": 2},
        {"type": "line", "start": (0.0, -20.0), "end": (2.395, -14.601),  "width": 2},
        {"type": "line", "start": (4.79, -9.202), "end": (7.185, -3.803),  "width": 2},
        {"type": "line", "start": (9.58, 1.596), "end": (12.0, 7.0), "width": 2},
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



