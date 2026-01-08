#!/usr/bin/env python3
"""
Siprotec 5 Interface Frontend for Raspberry Pi
Displays 6 relay interfaces with IEC61850 communication via Unix sockets

Commands sent:
{"command": "get_measurements"}
{"command": "open_breaker"}
{"command": "close_breaker"}
{"command": "reset_trip"}

Expected response format:
{
  "voltage_l1": 13.8,
  "voltage_l2": 13.7,
  "voltage_l3": 13.9,
  "current_l1": 125.5,
  "current_l2": 124.8,
  "current_l3": 126.2,
  "breaker_state": "CLOSED",
  "trip_active": false
}

"""

import pygame
import socket
import json
import threading
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List

# Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30

# Unix socket paths for each IEC61850 server
SOCKET_PATHS = [
    "/tmp/iec61850_relay_1.sock",
    "/tmp/iec61850_relay_2.sock",
    "/tmp/iec61850_relay_3.sock",
    "/tmp/iec61850_relay_4.sock",
    "/tmp/iec61850_relay_5.sock",
    "/tmp/iec61850_relay_6.sock",
]

# Colors
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


class BreakerState(Enum):
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
    trip_active: bool = False
    connected: bool = False


class IEC61850Client:
    """Handles communication with IEC61850 server via Unix socket"""
    
    def __init__(self, socket_path: str, relay_id: int):
        self.socket_path = socket_path
        self.relay_id = relay_id
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.data = RelayData(name=f"Relay {relay_id + 1}")
        self.lock = threading.Lock()
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
            if self.send_command("get_measurements"):
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
                        self.data.breaker_state = BreakerState[state_str]
                        self.data.trip_active = response.get("trip_active", False)
            
            time.sleep(0.5)  # Update every 500ms
    
    def open_breaker(self):
        """Send command to open breaker"""
        return self.send_command("open_breaker")
    
    def close_breaker(self):
        """Send command to close breaker"""
        return self.send_command("close_breaker")
    
    def reset_trip(self):
        """Send command to reset trip"""
        return self.send_command("reset_trip")
    
    def get_data(self) -> RelayData:
        """Get the current relay data (thread-safe)"""
        with self.lock:
            return RelayData(**self.data.__dict__)
    
    def stop(self):
        """Stop the client"""
        self.running = False
        self.disconnect()


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
            # Lighten color on hover
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
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)
        
        # Draw relay icon (simple representation)
        icon_size = min(self.rect.width, self.rect.height) // 3
        icon_rect = pygame.Rect(0, 0, icon_size, icon_size)
        icon_rect.center = (self.rect.centerx, self.rect.centery - 20)
        pygame.draw.rect(surface, WHITE, icon_rect, 3, border_radius=5)
        
        # Draw text
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
        surface.blit(text_surf, text_rect)


class StartScreen:
    """Start screen with 2x3 grid of relay icons"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buttons: List[IconButton] = []
        self._create_buttons()
    
    def _create_buttons(self):
        """Create the 2x3 grid of icon buttons"""
        margin = 40
        spacing = 20
        button_width = (self.width - 2 * margin - spacing) // 3
        button_height = (self.height - 2 * margin - 2 * spacing) // 2
        
        for row in range(2):
            for col in range(3):
                x = margin + col * (button_width + spacing)
                y = margin + row * (button_height + spacing)
                relay_id = row * 2 + col
                button = IconButton(x, y, button_width, button_height, 
                                   f"Relay {relay_id + 1}", relay_id)
                self.buttons.append(button)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font):
        """Draw the start screen"""
        surface.fill(LIGHT_GRAY)
        
        # Draw title
        title = title_font.render("SIPROTEC 5 - Select Relay", True, SIEMENS_DARK_BLUE)
        title_rect = title.get_rect(center=(self.width // 2, 30))
        surface.blit(title, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface, font)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[int]:
        """Handle events, return relay_id if a button is clicked"""
        for button in self.buttons:
            if button.handle_event(event):
                return button.relay_id
        return None


class RelayScreen:
    """Screen for individual relay interface"""
    
    def __init__(self, width: int, height: int, client: IEC61850Client):
        self.width = width
        self.height = height
        self.client = client
        self.buttons: List[Button] = []
        self._create_buttons()
    
    def _create_buttons(self):
        """Create control buttons"""
        button_width = 150
        button_height = 50
        spacing = 20
        start_y = self.height - button_height - 20
        
        # Back button
        self.back_button = Button(20, 20, 100, 40, "← Back", GRAY, BLACK)
        
        # Control buttons
        x = (self.width - 3 * button_width - 2 * spacing) // 2
        self.open_button = Button(x, start_y, button_width, button_height, 
                                  "OPEN", RED)
        self.close_button = Button(x + button_width + spacing, start_y, 
                                   button_width, button_height, "CLOSE", GREEN)
        self.reset_button = Button(x + 2 * (button_width + spacing), start_y, 
                                   button_width, button_height, "RESET TRIP", ORANGE)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, 
             small_font: pygame.font.Font, title_font: pygame.font.Font):
        """Draw the relay interface"""
        surface.fill(WHITE)
        
        data = self.client.get_data()
        
        # Draw header
        pygame.draw.rect(surface, SIEMENS_BLUE, (0, 0, self.width, 70))
        title = title_font.render(f"SIPROTEC 5 - {data.name}", True, WHITE)
        surface.blit(title, (140, 15))
        
        # Connection status
        status_color = GREEN if data.connected else RED
        status_text = "CONNECTED" if data.connected else "DISCONNECTED"
        pygame.draw.circle(surface, status_color, (self.width - 80, 35), 10)
        status_surf = small_font.render(status_text, True, WHITE)
        surface.blit(status_surf, (self.width - 150, 25))
        
        # Draw back button
        self.back_button.draw(surface, font)
        
        # Draw measurements section
        y_offset = 100
        
        # Voltages
        self._draw_section(surface, "VOLTAGES (kV)", y_offset, font, small_font)
        self._draw_measurement(surface, "L1:", data.voltage_l1, "kV", 
                              y_offset + 40, small_font, SIEMENS_BLUE)
        self._draw_measurement(surface, "L2:", data.voltage_l2, "kV", 
                              y_offset + 70, small_font, SIEMENS_BLUE)
        self._draw_measurement(surface, "L3:", data.voltage_l3, "kV", 
                              y_offset + 100, small_font, SIEMENS_BLUE)
        
        # Currents
        y_offset = 240
        self._draw_section(surface, "CURRENTS (A)", y_offset, font, small_font)
        self._draw_measurement(surface, "L1:", data.current_l1, "A", 
                              y_offset + 40, small_font, SIEMENS_DARK_BLUE)
        self._draw_measurement(surface, "L2:", data.current_l2, "A", 
                              y_offset + 70, small_font, SIEMENS_DARK_BLUE)
        self._draw_measurement(surface, "L3:", data.current_l3, "A", 
                              y_offset + 100, small_font, SIEMENS_DARK_BLUE)
        
        # Breaker status
        self._draw_breaker_status(surface, data, font, small_font)
        
        # Draw control buttons
        self.open_button.draw(surface, font)
        self.close_button.draw(surface, font)
        self.reset_button.draw(surface, font)
    
    def _draw_section(self, surface: pygame.Surface, title: str, y: int, 
                     font: pygame.font.Font, small_font: pygame.font.Font):
        """Draw a section header"""
        pygame.draw.line(surface, DARK_GRAY, (50, y), (self.width - 50, y), 2)
        text = font.render(title, True, SIEMENS_DARK_BLUE)
        surface.blit(text, (60, y + 5))
    
    def _draw_measurement(self, surface: pygame.Surface, label: str, value: float, 
                         unit: str, y: int, font: pygame.font.Font, color: tuple):
        """Draw a measurement line"""
        label_surf = font.render(label, True, BLACK)
        surface.blit(label_surf, (80, y))
        
        value_text = f"{value:.2f} {unit}"
        value_surf = font.render(value_text, True, color)
        surface.blit(value_surf, (200, y))
    
    def _draw_breaker_status(self, surface: pygame.Surface, data: RelayData, 
                           font: pygame.font.Font, small_font: pygame.font.Font):
        """Draw breaker status indicator"""
        x = 450
        y = 150
        
        # Status box
        status_rect = pygame.Rect(x, y, 300, 150)
        pygame.draw.rect(surface, LIGHT_GRAY, status_rect, border_radius=10)
        pygame.draw.rect(surface, DARK_GRAY, status_rect, 3, border_radius=10)
        
        # Title
        title = font.render("BREAKER STATUS", True, SIEMENS_DARK_BLUE)
        surface.blit(title, (x + 50, y + 10))
        
        # State indicator
        state_color = GREEN if data.breaker_state == BreakerState.CLOSED else RED
        if data.breaker_state == BreakerState.UNKNOWN:
            state_color = GRAY
        
        pygame.draw.circle(surface, state_color, (x + 80, y + 70), 25)
        state_text = small_font.render(data.breaker_state.value, True, BLACK)
        surface.blit(state_text, (x + 130, y + 60))
        
        # Trip indicator
        if data.trip_active:
            trip_text = font.render("⚠ TRIP ACTIVE", True, RED)
            surface.blit(trip_text, (x + 60, y + 110))
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle events, return action string if needed"""
        if self.back_button.handle_event(event):
            return "back"
        if self.open_button.handle_event(event):
            self.client.open_breaker()
        if self.close_button.handle_event(event):
            self.client.close_breaker()
        if self.reset_button.handle_event(event):
            self.client.reset_trip()
        return None


class Application:
    """Main application class"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SIPROTEC 5 Interface")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
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
                        self.current_screen = "start"
                        self.current_relay = None
                    else:
                        self.running = False
            
            if self.current_screen == "start":
                relay_id = self.start_screen.handle_event(event)
                if relay_id is not None:
                    self.current_screen = "relay"
                    self.current_relay = relay_id
            
            elif self.current_screen == "relay":
                action = self.relay_screens[self.current_relay].handle_event(event)
                if action == "back":
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