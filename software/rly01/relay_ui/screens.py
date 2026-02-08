"""
Screen classes for start screen and relay interface
"""
import pygame
from typing import Optional, List

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, LIGHT_GRAY, SIEMENS_BLUE, WHITE, BLACK, 
    GRAY, YELLOW, GREEN, RED, FG, BG, INDICATORS
)
from ui_components import (
    Button, IconButton, DiagramPage, MeasurementPage, ControlPage, 
    PhasorPage, SettingsPage, PopupPage, MenuPage, draw_lcd_header, 
    draw_lcd_footer
)
from client import IEC61850Client
from models import RelayData


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
        title = title_font.render("HS Relay", True, WHITE)
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
        self.page_stack: List = []
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
        
        # Switch control buttons 
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
        
        # Draw switch control buttons
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
        
        # Draw footer at the bottom, with indication of button function
        if len(self.page_stack) > 1:
            if "left" in self.page_stack[-1].__dict__:
                left = self.page_stack[-1].left
            else:
                left = "Back"
        else:
            left = ""

        if "right" in self.page_stack[-1].__dict__:
            right = self.page_stack[-1].right
        else:
            right = "Select"

        draw_lcd_footer(self.lcd_surface, left=left, right=right)
    
    def _draw_status_panel(self, surface: pygame.Surface):
        """Draw LED status panel on the left side"""
        # Create tiny font for 8px text
        tiny_font = pygame.font.Font(None, 12)
        
        # Get relay data
        data = self.client.get_data()
        
        led_size = 8
        padding = 3
        text_bg_padding = 3
        text_bg_width = 30
        y_offset = self.status_panel_y + padding
        
        for label, is_active in INDICATORS:
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
        
        # Switch controls
        if self.select_button.handle_event(event):
            self.page_stack[:] = self.page_stack[:1]
            self.page_stack.append(ControlPage())
        if self.open_button.handle_event(event):
            if isinstance(self.page_stack[-1], DiagramPage): # Show popup only if on DiagramPage
                self.page_stack.append(PopupPage("Open the control menu to select elements to operate", "info"))
            if isinstance(self.page_stack[-1], ControlPage): # only if on ControlPage
                self.page_stack[-1].handle_key(pygame.K_o, self.page_stack)
        if self.close_button.handle_event(event):
            if isinstance(self.page_stack[-1], DiagramPage): # Show popup only if on DiagramPage
                self.page_stack.append(PopupPage("Open the control menu to select elements to operate", "info"))
            if isinstance(self.page_stack[-1], ControlPage): # only if on ControlPage
                self.page_stack[-1].handle_key(pygame.K_i, self.page_stack)
        
        return None

