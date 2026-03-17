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
    "/run/iec61850_ui/iec61850_relay_1.sock",
    "/run/iec61850_ui/iec61850_relay_2.sock",
    "/run/iec61850_ui/iec61850_relay_3.sock",
    "/run/iec61850_ui/iec61850_relay_4.sock",
    "/run/iec61850_ui/iec61850_relay_5.sock",
    "/run/iec61850_ui/iec61850_relay_6.sock",
]

UNIX_SOCKETS = [
    "/tmp/api_sock1",
    "/tmp/api_sock2",
    "/tmp/api_sock3",
    "/tmp/api_sock4",
    "/tmp/api_sock5",
    "/tmp/api_sock6"
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
    "s_swi3_blkopn": {
        "type": "status",
        "description": "Switch 3 interlock condition for switch OPEN"
    },
    "s_swi3_blkcls": {
        "type": "status",
        "description": "Switch 3 interlock condition for switch CLOSE"
    },
    "swi4": {
        "type": "switch",
        "description": "Switch 4"
    },
    "s_swi4_blkopn": {
        "type": "status",
        "description": "Switch 4 interlock condition for switch OPEN"
    },
    "s_swi4_blkcls": {
        "type": "status",
        "description": "Switch 4 interlock condition for switch CLOSE"
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
        "description": "Current Transformer 1a"
    },
    "m_ctr1_phsB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1b"
    },
    "m_ctr1_phsC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1c"
    },
    "m_ctr1_phsAngA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 angleA"
    },
    "m_ctr1_phsAngB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 angleB"
    },
    "m_ctr1_phsAngC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 angleC"
    },    

    "vtr1": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 average V"
    },

    "m_v1_pA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 angleA"
    },
    "m_v1_pB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 angleB"
    },
    "m_v1_pC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 angleC"
    },
    "m_v1_aA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 amplitude A"
    },
    "m_v1_aB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 amplitude B"
    },
    "m_v1_aC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 amplitude C"
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
    "s_cilo1": {
        "type": "status",
        "description": "Switch 1 interlock EnaOpn value"
    },
    "s_cilo2": {
        "type": "status",
        "description": "Switch 2 interlock EnaOpn value"
    },
    "s_cilo3": {
        "type": "status",
        "description": "Switch 3 interlock EnaOpn value"
    },
    "s_cilo4": {
        "type": "status",
        "description": "Switch 4 interlock EnaOpn value"
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
        "description": "Current Transformer 1a"
    },
    "m_ctr1_phsB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1b"
    },
    "m_ctr1_phsC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1c"
    },
    "m_ctr1_phsAngA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 angleA"
    },
    "m_ctr1_phsAngB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 angleB"
    },
    "m_ctr1_phsAngC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 1 angleC"
    },    

    "ctr2": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 2 average A"
    },
    "m_ctr2_phsA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 2a"
    },
    "m_ctr2_phsB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 2b"
    },
    "m_ctr2_phsC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 2c"
    },
    "m_ctr2_phsAngA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 2 angleA"
    },
    "m_ctr2_phsAngB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 2 angleB"
    },
    "m_ctr2_phsAngC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 2 angleC"
    },

    "ctr3": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 3 average A"
    },
    "m_ctr3_phsA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 3a"
    },
    "m_ctr3_phsB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 3b"
    },
    "m_ctr3_phsC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 3c"
    },
    "m_ctr3_phsAngA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 3 angleA"
    },
    "m_ctr3_phsAngB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 3 angleB"
    },
    "m_ctr3_phsAngC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 3 angleC"
    },

    "ctr4": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 4 average A"
    },
    "m_ctr4_phsA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 4a"
    },
    "m_ctr4_phsB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 4b"
    },
    "m_ctr4_phsC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 4c"
    },
    "m_ctr4_phsAngA": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 4 angleA"
    },
    "m_ctr4_phsAngB": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 4 angleB"
    },
    "m_ctr4_phsAngC": {
        "type": "measurement",
        "measurement_type": "current",
        "description": "Current Transformer 4 angleC"
    },    

    "vtr1": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 average V"
    },
    "m_v1_pA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 angleA"
    },
    "m_v1_pB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 angleB"
    },
    "m_v1_pC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 angleC"
    },
    "m_v1_aA": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 amplitude A"
    },
    "m_v1_aB": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 amplitude B"
    },
    "m_v1_aC": {
        "type": "measurement",
        "measurement_type": "voltage",
        "description": "Voltage Transformer 1 amplitude C"
    },

    # Settings
    "loc": {
        "type": "setting",
        "description": "Local/Remote Control"
    },
    "s_LoSet": {
        "type": "setting",
        "description": "Low operate value"
    },
    "s_HiSet": {
        "type": "setting",
        "description": "High operate value"
    },
    "s_MinOpTmms": {
        "type": "setting",
        "description": "Minimum operate time"
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
    ["Lo setting",    "s_LoSet", float, 0.0],
    ["Hi setting",    "s_HiSet", float, 0.0],
    ["Min. delay",    "s_MinOpTmms", int, 0],
    ["Local/Remote", "loc",    bool,  False],
]

SETTINGS_TR = [
    ["I> pickup",    "s_Ilarge", float, 0.0],
    ["T> delay",     "s_Tm",     float, 0.0],
    ["Local/Remote", "loc",    bool,  False],
]

SETTINGS = [
    SETTINGS_FEED,
    SETTINGS_FEED,
    SETTINGS_BUS,
    SETTINGS_BUS,
    SETTINGS_TR,
    SETTINGS_TR
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

MEASUREMENTS_BUS = [
    ("Iph 1A", "m_ctr1_phsA", "m_ctr1_phsAngA"),
    ("Iph 1B", "m_ctr1_phsB", "m_ctr1_phsAngB"),
    ("Iph 1C", "m_ctr1_phsC", "m_ctr1_phsAngC"),
    ("Iph 2A", "m_ctr2_phsA", "m_ctr2_phsAngA"),
    ("Iph 2B", "m_ctr2_phsB", "m_ctr2_phsAngB"),
    ("Iph 2C", "m_ctr2_phsC", "m_ctr2_phsAngC"),
    ("Iph 3A", "m_ctr3_phsA", "m_ctr3_phsAngA"),
    ("Iph 3B", "m_ctr3_phsB", "m_ctr3_phsAngB"),
    ("Iph 3C", "m_ctr3_phsC", "m_ctr3_phsAngC"),
    ("Iph 4A", "m_ctr4_phsA", "m_ctr4_phsAngA"),
    ("Iph 4B", "m_ctr4_phsB", "m_ctr4_phsAngB"),
    ("Iph 4C", "m_ctr4_phsC", "m_ctr4_phsAngC"),
    ("Bus Vph A", "m_v1_pA", "m_v1_aA"),
    ("Bus Vph B", "m_v1_pB", "m_v1_aB"),
    ("Bus Vph C", "m_v1_pC", "m_v1_aC"),
]

MEASUREMENTS_TR = [
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
        "BlkOpn": "s_swi3_blkopn",
        "BlkCls": "s_swi3_blkcls",
        "position": (80, 100),
        "rotation": 180,
        "selectable": True,
    },   
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "swi4",
        "BlkOpn": "s_swi4_blkopn",
        "BlkCls": "s_swi4_blkcls",
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
        "BlkOpn": "s_swi2_blkopn",
        "BlkCls": "s_swi2_blkcls",
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
        "type": "primitive",
        "primitive": {"type": "line", "start": (20, 40), "end": (20, 60), "width": 2},
    },
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "s_cilo1",
        "position": (20, 90),
        "rotation": 180,
        "selectable": False,
    },  
    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (20, 120), "end": (20, 140), "width": 2},
    }, 

    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (80, 40), "end": (80, 60), "width": 2},
    },
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "s_cilo2",
        "position": (80, 90),
        "rotation": 180,
        "selectable": False,
    },  
    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (80, 120), "end": (80, 140), "width": 2},
    },

    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (140, 40), "end": (140, 60), "width": 2},
    },
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "s_cilo3",
        "position": (140, 90),
        "rotation": 180,
        "selectable": False,
    },  
    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (140, 120), "end": (140, 140), "width": 2},
    },

    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (200, 40), "end": (200, 60), "width": 2},
    },
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "s_cilo4",
        "position": (200, 90),
        "rotation": 180,
        "selectable": False,
    },  
    {
        "type": "primitive",
        "primitive": {"type": "line", "start": (200, 120), "end": (200, 140), "width": 2},
    },

    {
        "type": "text",
        "position": (10, 150),    
        "formatted_text" : "",
        "element": "ctr1",
        "template": "FEED1\nCT 1:\n{value:.1f}\nAmp",
    },
    {
        "type": "text",
        "position": (70, 150),    
        "formatted_text" : "",
        "element": "ctr2",
        "template": "FEED2\nCT 2:\n{value:.1f}\nAmp",
    },
    {
        "type": "text",
        "position": (130, 150),    
        "formatted_text" : "",
        "element": "ctr3",
        "template": "TR1\nCT 3:\n{value:.1f}\nAmp",
    },
    {
        "type": "text",
        "position": (190, 150),    
        "formatted_text" : "",
        "element": "ctr4",
        "template": "TR2\nCT 4:\n{value:.1f}\nAmp",
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
        "BlkOpn": "s_swi2_blkopn",
        "BlkCls": "s_swi2_blkcls",
        "position": (80, 100),
        "rotation": 180,
        "selectable": True,
    },   
    {
        "type": "symbol",
        "name": "disconnector",
        "state": "open",
        "element": "swi3",
        "BlkOpn": "s_swi3_blkopn",
        "BlkCls": "s_swi3_blkcls",
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
    DIAGRAM_OBJECTS_BUS + [{
        "type": "text",
        "position": (40, 22),    
        "formatted_text" : "Busbar 1"
    }],
    DIAGRAM_OBJECTS_BUS + [{
        "type": "text",
        "position": (40, 22),    
        "formatted_text" : "Busbar 2"
    }],
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



