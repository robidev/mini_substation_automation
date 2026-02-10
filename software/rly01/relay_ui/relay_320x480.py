"""
Relay Interface - Combined IED Control System
Main application entry point
"""
import pygame
import threading
from typing import Optional, List

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SOCKET_PATHS
from client import IEC61850Client

# Pygame initialization
pygame.init()

from screens import StartScreen, RelayScreen


# =====================================================
# APPLICATION
# =====================================================
class Application:
    """Main application class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Relay interface - Combined IED")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        
        # Create IEC61850 clients
        self.clients = [IEC61850Client(path, i) for i, path in enumerate(SOCKET_PATHS)]
        
        # Start client threads
        self.threads: List[threading.Thread] = []
        for client in self.clients:
            thread = threading.Thread(target=client.update_loop, daemon=True)
            thread.start()
            self.threads.append(thread)
        
        # Screens
        self.start_screen = StartScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.relay_screens = [RelayScreen(SCREEN_WIDTH, SCREEN_HEIGHT, client) 
                             for client in self.clients]
        
        self.current_screen = "start"
        self.current_relay: Optional[int] = None
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
            
            if self.current_screen == "start":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                        
                relay_id = self.start_screen.handle_event(event)
                if relay_id is not None:
                    self.current_screen = "relay"
                    self.current_relay = relay_id
                    self.relay_screens[self.current_relay].client.set_visible(True)
            
            elif self.current_screen == "relay" and self.current_relay is not None:
                action = self.relay_screens[self.current_relay].handle_event(event)
                if action == "back":
                    self.relay_screens[self.current_relay].client.set_visible(False)
                    self.current_screen = "start"
                    self.current_relay = None
    
    def draw(self):
        """Draw the current screen"""
        if self.current_screen == "start":
            self.start_screen.draw(self.screen, self.font, self.title_font)
        elif self.current_screen == "relay" and self.current_relay is not None:
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
