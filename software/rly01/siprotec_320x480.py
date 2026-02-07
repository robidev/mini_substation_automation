import pygame
import socket
import json
import threading
import time
import math
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List

# =====================================================
# DISPLAY CONFIG
# =====================================================
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480
LCD_W, LCD_H = 480, 272
SCALE = 2
FPS = 30

# Pygame initialization
pygame.init()

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

# Unix socket paths for each IEC61850 server
SOCKET_PATHS = [
    "/tmp/iec61850_relay_1.sock",
    "/tmp/iec61850_relay_2.sock",
    "/tmp/iec61850_relay_3.sock",
    "/tmp/iec61850_relay_4.sock",
    "/tmp/iec61850_relay_5.sock",
    "/tmp/iec61850_relay_6.sock",
]

# IEC61850 Keys mapping
IEC_KEYS = {
    "cbr1": "FEED1LD1/XCBR1",
    "swi1": "FEED1LD1/XSWI2",
    "swi2": "FEED1LD1/XSWI3",
    "swi3": "FEED1LD1/XSWI4",
    "ctr1": "FEED1LD1/MMXU1",
    "vtr1": "FEED1LD1/MMXU2",
    "vtr2": "FEED1LD1/MMXU3",
    "set0_loc": "FEED1LD1/LLN0, Beh.stVal",
    "set1_Ilarge": "FEED1LD1/PTOC1, StrVal.setMag.f",
    "set2_Tm": "FEED1LD1/PTOC1, TmMult.setMag.f",
}


class BreakerState(Enum):
    INTERMEDIATE = "INTERMEDIATE"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


@dataclass
class RelayData:
    """Data structure for relay measurements and status"""
    name: str
    voltage_l1: float = 0.0
    voltage_l2: float = 0.0
    voltage_l3: float = 0.0
    current_l1: float = 0.0
    current_l2: float = 0.0
    current_l3: float = 0.0
    breaker_state: BreakerState = BreakerState.UNKNOWN
    connected: bool = False
    # Additional IEC61850 data
    cbr1_state: str = "UNKNOWN"
    swi1_state: str = "UNKNOWN"
    swi2_state: str = "UNKNOWN"
    swi3_state: str = "UNKNOWN"
    ctr1_data: Dict = None
    vtr1_data: Dict = None
    vtr2_data: Dict = None
    set0_loc: str = "UNKNOWN"
    set1_Ilarge: float = 0.0
    set2_Tm: float = 0.0


class IEC61850Client:
    """Handles communication with IEC61850 server via Unix socket"""
    
    def __init__(self, socket_path: str, relay_id: int):
        self.socket_path = socket_path
        self.relay_id = relay_id
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.data = RelayData(name=f"Relay {relay_id + 1}")
        self.lock = threading.Lock()
        self.visible = False
        self.running = True
        
    def connect(self):
        """Attempt to connect to the Unix socket"""
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(2.0)
            self.sock.connect(self.socket_path)
            self.connected = True
            self.data.connected = True
            print(f"Connected to {self.socket_path}")
        except Exception as e:
            print(f"Failed to connect to {self.socket_path}: {e}")
            self.connected = False
            self.data.connected = False
            self.sock = None
    
    def disconnect(self):
        """Close the socket connection"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.connected = False
        self.data.connected = False
    
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send a command to the IEC61850 server"""
        if not self.connected or not self.sock:
            return False
        
        try:
            message = {"command": command}
            if params:
                message.update(params)
            
            data = json.dumps(message) + "\n"
            self.sock.sendall(data.encode())
            return True
        except Exception as e:
            print(f"Error sending command to {self.socket_path}: {e}")
            self.disconnect()
            return False
    
    def receive_data(self) -> Optional[Dict]:
        """Receive data from the IEC61850 server"""
        if not self.connected or not self.sock:
            return None
        
        try:
            # Receive data (assuming newline-delimited JSON)
            buffer = b""
            while b"\n" not in buffer:
                chunk = self.sock.recv(1024)
                if not chunk:
                    raise ConnectionError("Connection closed")
                buffer += chunk
            
            data = buffer.split(b"\n")[0]
            return json.loads(data.decode())
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Error receiving data from {self.socket_path}: {e}")
            self.disconnect()
            return None
    
    def update_loop(self):
        """Background thread to continuously update data"""
        while self.running:
            if not self.connected:
                self.connect()
                time.sleep(2)
                continue
            
            # Request data update
            if self.visible and self.send_command("get_measurements"):
                response = self.receive_data()
                if response:
                    with self.lock:
                        self.data.voltage_l1 = response.get("voltage_l1", 0.0)
                        self.data.voltage_l2 = response.get("voltage_l2", 0.0)
                        self.data.voltage_l3 = response.get("voltage_l3", 0.0)
                        self.data.current_l1 = response.get("current_l1", 0.0)
                        self.data.current_l2 = response.get("current_l2", 0.0)
                        self.data.current_l3 = response.get("current_l3", 0.0)
                        
                        state_str = response.get("breaker_state", "UNKNOWN")
                        try:
                            self.data.breaker_state = BreakerState[state_str]
                        except KeyError:
                            self.data.breaker_state = BreakerState.UNKNOWN
                        
                        # Update IEC61850 specific data
                        self.data.cbr1_state = response.get("cbr1_state", "UNKNOWN")
                        self.data.swi1_state = response.get("swi1_state", "UNKNOWN")
                        self.data.swi2_state = response.get("swi2_state", "UNKNOWN")
                        self.data.swi3_state = response.get("swi3_state", "UNKNOWN")
                        
                        self.data.ctr1_data = response.get("ctr1_data", {})
                        self.data.vtr1_data = response.get("vtr1_data", {})
                        self.data.vtr2_data = response.get("vtr2_data", {})
                        
                        self.data.set0_loc = response.get("set0_loc", "UNKNOWN")
                        self.data.set1_Ilarge = response.get("set1_Ilarge", 0.0)
                        self.data.set2_Tm = response.get("set2_Tm", 0.0)
            
            time.sleep(0.5)  # Update every 500ms
    
    def open_breaker(self):
        """Send command to open breaker"""
        return self.send_command("open_breaker")
    
    def close_breaker(self):
        """Send command to close breaker"""
        return self.send_command("close_breaker")
    
    def get_data(self) -> RelayData:
        """Get the current relay data (thread-safe)"""
        with self.lock:
            return RelayData(**self.data.__dict__)
    
    def set_visible(self, visible):
        self.visible = visible

    def stop(self):
        """Stop the client"""
        self.running = False
        self.disconnect()


# =====================================================
# FONT UTILITIES
# =====================================================
FONT_H = 14
FONT = pygame.font.SysFont("courier", FONT_H, bold=True)

def text(surface, txt, x, y, fg=FG, bg=None):
    """Render text on surface"""
    surf = FONT.render(txt, False, fg, bg)
    surface.blit(surf, (x, y))


# =====================================================
# IED HELPER FUNCTIONS
# =====================================================
def polar_to_xy(mag, angle_deg, scale):
    """Convert polar coordinates to XY"""
    rad = math.radians(angle_deg)
    return (
        mag * math.cos(rad) * scale,
        -mag * math.sin(rad) * scale
    )


# =====================================================
# IED PAGE CLASSES
# =====================================================
class Page:
    """Base page class"""
    title = ""

    def handle_key(self, key, stack):
        return

    def draw(self, surface):
        pass


class MeasurementPage(Page):
    """Display measurements from relay data"""
    title = "Measurements"

    def __init__(self, relay_data):
        self.relay_data = relay_data

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            stack.pop()

    def draw(self, surface):
        data = self.relay_data.get_data() if self.relay_data else RelayData("N/A")
        text(surface, "Side 1", 20, 30)
        values = [
            ("Iph A", f"{data.current_l1:.1f} A", "0°"),
            ("Iph B", f"{data.current_l2:.1f} A", "-120°"),
            ("Iph C", f"{data.current_l3:.1f} A", "120°"),
            ("Vph A", f"{data.voltage_l1:.1f} V", "0°"),
            ("Vph B", f"{data.voltage_l2:.1f} V", "-120°"),
            ("Vph C", f"{data.voltage_l3:.1f} V", "120°"),
        ]
        y = 55
        for v in values:
            text(surface, f"{v[0]:<8} {v[1]:>7} {v[2]:>6}", 40, y)
            y += FONT_H + 3

# Symbol definitions - each symbol is centered at origin (0, 0)
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

objects = [
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
            "name": "disconnector_closed",
            "position": (80, 100),
            "rotation": 180,
            "selectable": True,
        },   
        {
            "type": "symbol",
            "name": "disconnector_open",
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
            "name": "circuit_breaker_closed",
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
            "name": "disconnector_open",
            "position": (120, 270),
            "rotation": 180,
            "selectable": True,
        },  
        
]



class DiagramPage(Page):
    """Single line diagram"""
    title = "Single line"

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            if len(stack) > 1:
                stack.pop()

    def draw(self, surface):
        draw_singe_line(surface, objects, -1)


class ControlPage(Page):
    """Single line diagram"""
    title = "Control"

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            if len(stack) > 1:
                stack.pop()

    def draw(self, surface):
        draw_singe_line(surface, objects, 3)


def rotate_point(point, angle_deg):
    """Rotate a point around origin by angle_deg degrees."""
    if angle_deg == 0:
        return point
    
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    x, y = point
    
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    return (new_x, new_y)


def transform_primitive(primitive, position, rotation=0):
    """Transform a primitive shape by position and rotation."""
    transformed = {"type": primitive["type"]}
    
    if primitive["type"] in ["line"]:
        start = rotate_point(primitive["start"], rotation)
        end = rotate_point(primitive["end"], rotation)
        transformed["start"] = (position[0] + start[0], position[1] + start[1])
        transformed["end"] = (position[0] + end[0], position[1] + end[1])
        transformed["width"] = primitive["width"]
        
    elif primitive["type"] in ["circle", "filled_circle"]:
        center = rotate_point(primitive["center"], rotation)
        transformed["center"] = (position[0] + center[0], position[1] + center[1])
        transformed["radius"] = primitive["radius"]
        if "width" in primitive:
            transformed["width"] = primitive["width"]
    
    return transformed


def draw_primitive(surface, primitive):
    """Draw a single primitive shape."""
    if primitive["type"] == "line":
        pygame.draw.line(
            surface, FG, primitive["start"], primitive["end"], primitive["width"]
        )
    elif primitive["type"] == "circle":
        pygame.draw.circle(
            surface, FG, primitive["center"], primitive["radius"], primitive["width"]
        )
    elif primitive["type"] == "filled_circle":
        pygame.draw.circle(
            surface, FG, primitive["center"], primitive["radius"]
        )


def draw_symbol(surface, symbol_name, position, rotation=0):
    """Draw a symbol at the given position with optional rotation."""
    if symbol_name not in SYMBOLS:
        print(f"Warning: Symbol '{symbol_name}' not found")
        return
    
    symbol_primitives = SYMBOLS[symbol_name]
    
    for primitive in symbol_primitives:
        transformed = transform_primitive(primitive, position, rotation)
        draw_primitive(surface, transformed)


def cursor_on(period_ms=500):
    return (pygame.time.get_ticks() // period_ms) % 2 == 0


def draw_singe_line(surface, object_list, highlighted_object):
    index = -1
    for i, obj in enumerate(object_list):
        if obj["type"] == "symbol":
            draw_symbol(
                surface,
                obj["name"],
                obj["position"],
                obj.get("rotation", 0),
            )
            if "selectable" in obj:
                index = index + 1
                if index != -1 and index == highlighted_object and cursor_on():
                    swap_fg_bg(surface, pygame.Rect(obj["position"][0]-15, obj["position"][1]-15, 30, 30), FG, BG)
        elif obj["type"] == "text":
            text(surface, obj["label"], obj["position"])
        elif obj["type"] == "primitive":
            draw_primitive(surface, obj["primitive"])



def swap_fg_bg(surface, rect, fg, bg):
    sub = surface.subsurface(rect).copy()
    px = pygame.PixelArray(sub)

    fg_c = sub.map_rgb(fg)
    bg_c = sub.map_rgb(bg)

    for x in range(sub.get_width()):
        for y in range(sub.get_height()):
            if px[x, y] == fg_c:
                px[x, y] = bg_c
            elif px[x, y] == bg_c:
                px[x, y] = fg_c

    del px
    surface.blit(sub, rect.topleft)



class PhasorPage(Page):
    """Phasor diagram"""
    title = "Phasors"

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            stack.pop()

    def draw(self, surface):
        cx, cy = 120, 76
        r = 35
        pygame.draw.circle(surface, FG, (cx, cy), r, 1)
        pygame.draw.line(surface, FG, (cx - r, cy), (cx + r, cy), 1)
        pygame.draw.line(surface, FG, (cx, cy - r), (cx, cy + r), 1)

        for name, ang in [("IA", 0), ("IB", -120), ("IC", 120)]:
            dx, dy = polar_to_xy(1.0, ang, r)
            x, y = int(cx + dx), int(cy + dy)
            pygame.draw.line(surface, FG, (cx, cy), (x, y), 2)
            pygame.draw.circle(surface, FG, (x, y), 3)
            text(surface, name, x + 5, y - 5)


class SettingsPage(Page):
    """Settings editor page"""
    title = "Settings"

    def __init__(self, relay_data):
        self.relay_data = relay_data
        self.items = [
            ["I> pickup", "120.0"],
            ["T> delay", "0.50"],
            ["CT ratio", "400.0"],
        ]
        self.sel = 0
        self.edit = False
        self.cursor = 0

    def handle_key(self, key, stack):
        if not self.edit:
            if key == pygame.K_DOWN:
                self.sel = (self.sel + 1) % len(self.items)
            elif key == pygame.K_UP:
                self.sel = (self.sel - 1) % len(self.items)
            elif key == pygame.K_RETURN:
                self.edit = True
                self.cursor = len(self.items[self.sel][1]) - 1
            elif key == pygame.K_ESCAPE:
                stack.pop()
        else:
            val = list(self.items[self.sel][1])
            if key == pygame.K_LEFT:
                self.cursor = max(0, self.cursor - 1)
            elif key == pygame.K_RIGHT:
                self.cursor = min(len(val) - 1, self.cursor + 1)
            elif key == pygame.K_UP and val[self.cursor].isdigit():
                val[self.cursor] = str((int(val[self.cursor]) + 1) % 10)
            elif key == pygame.K_DOWN and val[self.cursor].isdigit():
                val[self.cursor] = str((int(val[self.cursor]) - 1) % 10)
            elif key == pygame.K_RETURN:
                self.edit = False
            elif key == pygame.K_ESCAPE:
                self.edit = False
            self.items[self.sel][1] = "".join(val)

    def draw(self, surface):
        y = 40
        for i, (name, val) in enumerate(self.items):
            if i == self.sel and not self.edit:
                text(surface, f"{name:<12} {val:>7}", 20, y, INV_FG, INV_BG)
            else:
                text(surface, f"{name:<12} {val:>7}", 20, y)
            if i == self.sel and self.edit:
                cx = 140 + self.cursor * 8
                pygame.draw.line(surface, INV_FG, (cx, y + FONT_H), (cx + 7, y + FONT_H), 1)
            y += FONT_H + 6


class PopupPage(Page):
    """Popup modal page for displaying messages"""
    title = "Notification"

    def __init__(self, message: str, msg_type: str = "info"):
        """
        Args:
            message: Text to display in the popup
            msg_type: Type of message - "info", "confirm", or "error"
        """
        self.message = message
        self.msg_type = msg_type

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE or key == pygame.K_RETURN:
            if len(stack) > 1:
                stack.pop()

    def draw(self, surface):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        # Draw popup box
        box_width = 150
        box_height = 80
        box_x = (surface.get_width() - box_width) // 2
        box_y = (surface.get_height() - box_height) // 2
        pygame.draw.rect(surface, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surface, FG, (box_x, box_y, box_width, box_height), 2)

        # Draw message (wrapped)
        msg_y = box_y + 15
        words = self.message.split()
        line = ""
        for word in words:
            test_line = line + (" " if line else "") + word
            if len(test_line) > 18:
                text(surface, line, box_x + 8, msg_y, FG)
                msg_y += FONT_H + 2
                line = word
            else:
                line = test_line
        if line:
            text(surface, line, box_x + 8, msg_y, FG)

        # Draw OK button label
        text(surface, "[OK]", box_x + 53, box_y + box_height - 18, FG)


class MenuPage(Page):
    """Menu page with navigation"""
    def __init__(self, title, items):
        self.title = title
        self.items = items
        self.sel = 0

    def handle_key(self, key, stack):
        if key == pygame.K_DOWN:
            self.sel = (self.sel + 1) % len(self.items)
        elif key == pygame.K_UP:
            self.sel = (self.sel - 1) % len(self.items)
        elif key == pygame.K_RETURN:
            stack.append(self.items[self.sel][1])
        elif key == pygame.K_ESCAPE and len(stack) > 1:
            stack.pop()

    def draw(self, surface):
        y = 30
        for i, (name, _) in enumerate(self.items):
            if i == self.sel:
                text(surface, name, 20, y, INV_FG, INV_BG)
            else:
                text(surface, name, 20, y)
            y += FONT_H + 4


def draw_lcd_header(surface, breadcrumb):
    """Draw LCD header"""
    pygame.draw.rect(surface, FG, (0, 0, 272, 20))
    breadcrumb_text =  " > ".join(breadcrumb)
    snip = 0
    if len(breadcrumb_text) > 29:
        breadcrumb_text = breadcrumb_text[-29:]
    text(surface,breadcrumb_text, 10, 3, INV_FG)


def draw_lcd_footer(surface, left="Back", right="Select"):
    """Draw LCD footer at the bottom"""
    # Draw footer at bottom of surface with dynamic height
    footer_y = surface.get_height() - 20
    pygame.draw.rect(surface, FG, (0, footer_y, surface.get_width(), 20))
    text(surface, left, 6, footer_y + 3, INV_FG)
    text(surface, right, 198, footer_y + 3, INV_FG)


# =====================================================
# BUTTON CLASS
# =====================================================
class Button:
    """Simple button widget"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: tuple, text_color: tuple = WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False
        self.pressed = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the button"""
        color = self.color
        if self.hover:
            color = tuple(min(c + 30, 255) for c in self.color)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=5)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, return True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                return True
            self.pressed = False
        return False


class IconButton(Button):
    """Icon button for the start screen"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, relay_id: int):
        super().__init__(x, y, width, height, text, SIEMENS_BLUE)
        self.relay_id = relay_id
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the icon button with relay number"""
        color = self.color
        if self.hover:
            color = tuple(min(c + 30, 255) for c in self.color)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        
        # Draw relay icon (simple representation)
        icon_size = min(self.rect.width, self.rect.height) // 3
        icon_rect = pygame.Rect(0, 0, icon_size, icon_size)
        icon_rect.center = (self.rect.centerx, self.rect.centery - 15)
        pygame.draw.rect(surface, WHITE, icon_rect, 2, border_radius=3)
        
        # Draw text
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 20))
        surface.blit(text_surf, text_rect)


# =====================================================
# START SCREEN
# =====================================================
class StartScreen:
    """Start screen with 3x2 grid of relay icons (portrait layout)"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buttons: List[IconButton] = []
        self._create_buttons()
    
    def _create_buttons(self):
        """Create the 3x2 grid of icon buttons"""
        margin = 20
        spacing = 15
        button_width = (self.width - 2 * margin - spacing) // 2
        button_height = (self.height - 80 - 2 * margin - 2 * spacing) // 3
        
        for row in range(3):
            for col in range(2):
                x = margin + col * (button_width + spacing)
                y = 70 + margin + row * (button_height + spacing)
                relay_id = row * 2 + col
                button = IconButton(x, y, button_width, button_height, 
                                   f"Relay {relay_id + 1}", relay_id)
                self.buttons.append(button)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font):
        """Draw the start screen"""
        surface.fill(LIGHT_GRAY)
        
        # Draw title bar
        pygame.draw.rect(surface, SIEMENS_BLUE, (0, 0, self.width, 60))
        title = title_font.render("SIPROTEC 5", True, WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 20))
        surface.blit(title, title_rect)
        
        subtitle = font.render("Select Relay", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 42))
        surface.blit(subtitle, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface, font)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle events, return relay_id if a button is clicked"""
        for button in self.buttons:
            if button.handle_event(event):
                return button.relay_id
        return None


# =====================================================
# RELAY SCREEN
# =====================================================
class RelayScreen:
    """Screen for individual relay interface with integrated IED display"""
    
    def __init__(self, width: int, height: int, client: IEC61850Client):
        self.width = width
        self.height = height
        self.client = client
        
        # Create LCD surface for IED display (246x356 to fill allocated area)
        self.lcd_surface = pygame.Surface((248, 322))
        
        # Navigation buttons
        self.buttons: List[Button] = []
        self._create_buttons()
        
        # Page stack for IED navigation
        self.page_stack: List[Page] = []
        self._init_pages()
        
    def _create_buttons(self):
        """Create control buttons"""
        button_width = 50
        button_height = 35
        spacing = 5
        
        # Back button (top-left)
        self.back_button = Button(5, 5, button_width, 20, "← Back", GRAY, BLACK)
        
        # Status panel dimensions
        self.status_panel_x = 7
        self.status_panel_y = 40
        self.status_panel_width = 50
        self.status_panel_height = 150
        
        # Navigation buttons 
        self.up_button = Button(160, 340, button_width, button_height, "↑", GRAY, BLACK)
        self.down_button = Button(160, 380, button_width, button_height, "↓", GRAY, BLACK)
        self.left_button = Button(105, 360, button_width, button_height, "←", GRAY, BLACK)
        self.right_button = Button(215, 360, button_width, button_height, "→", GRAY, BLACK)
        
        # Action buttons 
        self.cancel_button = Button(62, 332, 50, 25, "*", GRAY, BLACK)
        self.enter_button = Button(262, 332, 50, 25, "*", GRAY, BLACK)
        
        # Breaker control buttons 
        self.select_button = Button(275, 369, 35, button_height, "Ctrl", YELLOW)
        self.close_button = Button(275, 406, 35, button_height, "I", GREEN)
        self.open_button = Button(275, 443, 35, button_height, "O", RED)

    def _init_pages(self):
        """Initialize page menu"""
        self.root_menu = MenuPage("Main menu", [
            ("Measurements", MeasurementPage(self.client)),
            ("Control", ControlPage()),
            ("Phasors", PhasorPage()),
            ("Settings", SettingsPage(self.client)),
        ])
        # Make the single-line diagram the main (initial) page
        self.page_stack = [DiagramPage()]
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, 
             small_font: pygame.font.Font, title_font: pygame.font.Font):
        """Draw the relay interface"""
        surface.fill(LIGHT_GRAY)
        
        # Draw back button
        self.back_button.draw(surface, small_font)
        
        # Draw status panel with LED indicators
        self._draw_status_panel(surface)
        
        # Draw LCD area (with border)
        pygame.draw.rect(surface, BLACK, (62, 5, 252, 325), 2)
        pygame.draw.rect(surface, BG, (64, 7, 248, 321))
        
        # Draw IED content on LCD surface
        self._draw_ied_content()
        surface.blit(self.lcd_surface, (64, 7))
        
        # Draw navigation buttons
        self.up_button.draw(surface, small_font)
        self.down_button.draw(surface, small_font)
        self.left_button.draw(surface, small_font)
        self.right_button.draw(surface, small_font)
        
        # Draw action buttons
        self.enter_button.draw(surface, small_font)
        self.cancel_button.draw(surface, small_font)
        
        # Draw breaker control buttons
        self.select_button.draw(surface, small_font)
        self.open_button.draw(surface, small_font)
        self.close_button.draw(surface, small_font)
    
    def _draw_ied_content(self):
        """Draw the IED page content"""
        self.lcd_surface.fill(BG)
        
        # Draw header
        data = self.client.get_data()
        breadcrumb = [p.title for p in self.page_stack]
        draw_lcd_header(self.lcd_surface, breadcrumb)
        
        # Draw page content (between header and footer)
        self.page_stack[-1].draw(self.lcd_surface)
        
        # Draw footer at the bottom
        if len(self.page_stack) > 1:
            left = "Back"
        else:
            left = ""

        # When on the main single-line diagram page, show "Menu" on the right
        if isinstance(self.page_stack[-1], DiagramPage):
            right = " Menu"
        elif isinstance(self.page_stack[-1], ControlPage):
            right = "Switch"
        else:
            right = "Select"

        draw_lcd_footer(self.lcd_surface, left=left, right=right)
    
    def _draw_status_panel(self, surface: pygame.Surface):
        """Draw LED status panel on the left side"""
        # Draw panel background
        panel_rect = pygame.Rect(self.status_panel_x, self.status_panel_y, 
                                 self.status_panel_width, self.status_panel_height)
        #pygame.draw.rect(surface, WHITE, panel_rect)
        #pygame.draw.rect(surface, DARK_GRAY, panel_rect, 2)
        
        # Create tiny font for 8px text
        tiny_font = pygame.font.Font(None, 12)
        
        # Get relay data
        data = self.client.get_data()
        
        # Define status indicators (LED and label)
        indicators = [
            ("Fault", True),
            ("Trip", True),
            ("CBR1", data.cbr1_state == "CLOSED"),
            ("SWI1", data.swi1_state == "CLOSED"),
            ("SWI2", True),
            ("SWI3", True),
            ("Conn", data.connected),
        ]
        
        led_size = 8
        padding = 3
        text_bg_padding = 3
        text_bg_width = 30
        y_offset = self.status_panel_y + padding
        
        for label, is_active in indicators:
            # Draw LED circle
            led_color = GREEN if is_active else RED
            led_x = self.status_panel_x + padding + led_size // 2
            led_y = y_offset + led_size // 2
            pygame.draw.circle(surface, led_color, (led_x, led_y), led_size // 2)
            pygame.draw.circle(surface, BLACK, (led_x, led_y), led_size // 2, 1)
            
            # Draw label text background with padding and fixed width
            text_x = self.status_panel_x + led_size + padding + 4
            text_bg_rect = pygame.Rect(text_x - text_bg_padding, y_offset - text_bg_padding, 
                                       text_bg_width, led_size + 2 * text_bg_padding)
            pygame.draw.rect(surface, WHITE, text_bg_rect)
            
            # Draw label text on top of background
            label_surf = tiny_font.render(label, True, BLACK)
            surface.blit(label_surf, (text_x, y_offset))
            
            # Move to next row
            y_offset += led_size + padding + 5
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle events, return action string if needed"""
        if self.back_button.handle_event(event):
            return "back"
        
        if event.type == pygame.KEYDOWN:
            self.page_stack[-1].handle_key(event.key, self.page_stack)
        
        # Navigation buttons
        if self.up_button.handle_event(event):
            self.page_stack[-1].handle_key(pygame.K_UP, self.page_stack)
        if self.down_button.handle_event(event):
            self.page_stack[-1].handle_key(pygame.K_DOWN, self.page_stack)
        if self.left_button.handle_event(event):
            self.page_stack[-1].handle_key(pygame.K_LEFT, self.page_stack)
        if self.right_button.handle_event(event):
            self.page_stack[-1].handle_key(pygame.K_RIGHT, self.page_stack)
        
        # Action buttons
        if self.enter_button.handle_event(event):
            # If we're on the main diagram page, push the main menu when Enter is pressed
            if isinstance(self.page_stack[-1], DiagramPage):
                self.page_stack.append(self.root_menu)
            else:
                self.page_stack[-1].handle_key(pygame.K_RETURN, self.page_stack)
        if self.cancel_button.handle_event(event):
            self.page_stack[-1].handle_key(pygame.K_ESCAPE, self.page_stack)
        
        # Breaker controls
        if self.select_button.handle_event(event):
            self.page_stack[:] = self.page_stack[:1]
            self.page_stack.append(ControlPage())
        if self.open_button.handle_event(event):
            if isinstance(self.page_stack[-1], DiagramPage): # Show popup only if on DiagramPage
                self.page_stack.append(PopupPage("Operation selected", "info"))
            self.client.open_breaker()
        if self.close_button.handle_event(event):
            self.client.close_breaker()
        
        return None


# =====================================================
# APPLICATION
# =====================================================
class Application:
    """Main application class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("SIPROTEC 5 Interface - Combined IED")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        
        # Create IEC61850 clients
        self.clients = [IEC61850Client(path, i) for i, path in enumerate(SOCKET_PATHS)]
        
        # Start client threads
        self.threads = []
        for client in self.clients:
            thread = threading.Thread(target=client.update_loop, daemon=True)
            thread.start()
            self.threads.append(thread)
        
        # Screens
        self.start_screen = StartScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.relay_screens = [RelayScreen(SCREEN_WIDTH, SCREEN_HEIGHT, client) 
                             for client in self.clients]
        
        self.current_screen = "start"
        self.current_relay = None
        self.running = True
    
    def run(self):
        """Main application loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        self.cleanup()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_screen == "relay":
                        self.relay_screens[self.current_relay].client.set_visible(False) # only update a visible relay screen
                        self.current_screen = "start"
                        self.current_relay = None
                    else:
                        self.running = False # quit program
            
            if self.current_screen == "start":
                relay_id = self.start_screen.handle_event(event)
                if relay_id is not None:
                    self.current_screen = "relay"
                    self.current_relay = relay_id
                    self.relay_screens[self.current_relay].client.set_visible(True) # only update a visible relay screen
            
            elif self.current_screen == "relay":
                action = self.relay_screens[self.current_relay].handle_event(event)
                if action == "back":
                    self.relay_screens[self.current_relay].client.set_visible(False) # only update a visible relay screen
                    self.current_screen = "start"
                    self.current_relay = None
    
    def draw(self):
        """Draw the current screen"""
        if self.current_screen == "start":
            self.start_screen.draw(self.screen, self.font, self.title_font)
        elif self.current_screen == "relay":
            self.relay_screens[self.current_relay].draw(
                self.screen, self.font, self.small_font, self.title_font)
        
        pygame.display.flip()
    
    def cleanup(self):
        """Clean up resources"""
        for client in self.clients:
            client.stop()
        pygame.quit()


def main():
    """Entry point"""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
