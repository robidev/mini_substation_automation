"""
UI Components: buttons, pages, and related UI elements
"""
import pygame
from typing import Optional, List, Tuple

from config import (
    FG, BG, INV_FG, INV_BG, WHITE, BLACK, GRAY, DARK_GRAY, YELLOW, GREEN, RED,
    RELAY_BLUE, SETTINGS, MEASUREMENTS, DIAGRAM_OBJECTS, 
    DBPOS_ON, DBPOS_OFF, DBPOS_INTERMEDIATE, DBPOS_BAD
)
from drawing import (
    draw_single_line, swap_fg_bg, cursor_on, polar_to_xy, text, FONT, FONT_H
)



# =====================================================
# BUTTON CLASSES
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
        super().__init__(x, y, width, height, text, RELAY_BLUE)
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
# PAGE CLASSES
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

    def __init__(self, client):
        self.client = client
        self.right = ""

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            stack.pop()

    def draw(self, surface):
        self.client.enable_measurements = True
        y = 55
        for v in MEASUREMENTS[self.client.relay_id]:
            mag = self.client.get_measurement(v[1])
            ang = self.client.get_measurement(v[2])
            if mag == {}:
                mag = 1.0
            if ang == {}:
                ang = 0
            if v[0][0] == "I":
                text(surface, f"{v[0]:<8} {mag:>5} A {ang:>6}°", 20, y)
            else:
                text(surface, f"{v[0]:<8} {mag:>5} V {ang:>6}°", 20, y)                
            y += FONT_H + 3


class DiagramPage(Page):
    """Single line diagram"""
    title = "Single line"

    def __init__(self, client):
        self.client = client
        self.right = " Menu"

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            if len(stack) > 1:
                stack.pop()

    def draw(self, surface):
        self.client.enable_diagram_values = True
        for obj in DIAGRAM_OBJECTS[self.client.relay_id]:
            if "element" in obj:
                if obj["type"] == "symbol":
                    value = self.client.get_switch_state(obj["element"])
                    if value != "UNKNOWN":
                        if value == DBPOS_OFF:
                            obj["state"] = "open"
                        elif value == DBPOS_ON:
                            obj["state"] = "closed"
                        elif value == DBPOS_INTERMEDIATE:
                            obj["state"] = "intermediate"
                        else:
                            obj["state"] = "error"

                elif obj["type"] == "text":
                    raw = self.client.get_measurement(obj["element"])
                    value = float(raw) if isinstance(raw, (int, float)) else 0.0
                    obj["formatted_text"] = obj["template"].format(value=value)
                else:
                    obj["value"] = value


        draw_single_line(surface, DIAGRAM_OBJECTS[self.client.relay_id], -1)


class ControlPage(Page):
    """Control/selection page for diagram elements"""
    title = "Control"
    
    def __init__(self, client):
        self.client = client
        self.selectable_count = sum('selectable' in obj for obj in DIAGRAM_OBJECTS[self.client.relay_id])
        self.control_index = 0
        self.right = "Switch"
        self.selected_obj = None

    def action_callback_OPEN(self,result):
        if result == True:
            print("clicked OK, OPENING")   
            if self.selected_obj:
                if 'BlkOpn' in self.selected_obj and self.client.get_element_value(self.selected_obj['BlkOpn'],False) == True:
                    #stack.append(PopupPage(str(self.selected_obj["element"]) + " blocked by interlocking", "error"))
                    print("OPEN " + str(self.selected_obj["element"]) + " blocked by interlocking")
                else:
                    self.client.open_switch(self.selected_obj["element"])
                #self.selected_obj['state'] = "open"
        else:
            print("clicked CANCEL")
        self.selected_obj = None

    def action_callback_CLOSE(self,result):
        if result == True:
            print("clicked OK, CLOSING")   
            if self.selected_obj:
                if 'BlkCls' in self.selected_obj and self.client.get_element_value(self.selected_obj['BlkCls'],False) == True:
                    #stack.append(PopupPage(str(self.selected_obj["element"]) + " blocked by interlocking", "error"))
                    print("CLOSE " + str(self.selected_obj["element"]) + " blocked by interlocking")
                else:
                    self.client.close_switch(self.selected_obj["element"])
                #self.selected_obj['state'] = "closed"
        else:
            print("clicked CANCEL")
        self.selected_obj = None

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            if len(stack) > 1:
                stack.pop()
        elif key == pygame.K_DOWN:
            if self.control_index < self.selectable_count - 1:
                self.control_index += 1 
            else:
                self.control_index = 0
        elif key == pygame.K_UP:
            if self.control_index < 1:
                self.control_index = self.selectable_count - 1
            else:
                self.control_index -= 1 
        elif key == pygame.K_RETURN:
            stack.append(PopupPage("Press the red(O) button to open or green(I) to close the selected switch", "error"))
        elif key == pygame.K_o:
            self.selected_obj = [obj for obj in DIAGRAM_OBJECTS[self.client.relay_id] if obj.get("selectable")][self.control_index]
            stack.append(PopupPage("Object selected: " + str(self.selected_obj["element"]) + " Press OK to OPEN", "confirm", self.action_callback_OPEN))
        elif key == pygame.K_i:
            self.selected_obj = [obj for obj in DIAGRAM_OBJECTS[self.client.relay_id] if obj.get("selectable")][self.control_index]
            stack.append(PopupPage("Object selected: " + str(self.selected_obj["element"]) + " Press OK to CLOSE", "confirm", self.action_callback_CLOSE))
        


    def draw(self, surface):
        self.client.enable_diagram_values = True
        for obj in DIAGRAM_OBJECTS[self.client.relay_id]:
            if "element" in obj:
                if obj["type"] == "symbol":
                    value = self.client.get_switch_state(obj["element"])
                    if value != "UNKNOWN":
                        if value == DBPOS_OFF:
                            obj["state"] = "open"
                        elif value == DBPOS_ON:
                            obj["state"] = "closed"
                        elif value == DBPOS_INTERMEDIATE:
                            obj["state"] = "intermediate"
                        else:
                            obj["state"] = "error"

                elif obj["type"] == "text":
                    raw = self.client.get_measurement(obj["element"])
                    value = float(raw) if isinstance(raw, (int, float)) else 0.0
                    obj["formatted_text"] = obj["template"].format(value=value)
                else:
                    obj["value"] = value

        draw_single_line(surface, DIAGRAM_OBJECTS[self.client.relay_id], self.control_index)


class PhasorPage(Page):
    """Phasor diagram"""
    title = "Phasors"

    def __init__(self, client):
        self.client = client
        self.right = "next"
        self.page = 0
        self.pages = (len(MEASUREMENTS[self.client.relay_id]) + 2) // 3

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            stack.pop()
        if key == pygame.K_RETURN:
            self.page = (self.page + 1) % self.pages

    def draw(self, surface):
        self.client.enable_measurements = True
        cx, cy = 120, 126
        r = 50
        pygame.draw.circle(surface, FG, (cx, cy), r, 1)
        pygame.draw.line(surface, FG, (cx - r, cy), (cx + r, cy), 1)
        pygame.draw.line(surface, FG, (cx, cy - r), (cx, cy + r), 1)

        vectors = MEASUREMENTS[self.client.relay_id][(self.page*3):(self.page*3)+3]

        # Step 1: read magnitudes
        mags = []
        angs = []
        for _, mag_ref, ang_ref in vectors:
            mag = self.client.get_measurement(mag_ref) or 1.0
            ang = self.client.get_measurement(ang_ref) or 0
            mags.append(mag)
            angs.append(ang)

        # Step 2: normalize
        max_mag = max(mags) if max(mags) != 0 else 1.0

        # Step 3: draw
        for (name, _, _), mag, ang in zip(vectors, mags, angs):
            norm_mag = (mag / max_mag)
            dx, dy = polar_to_xy(norm_mag, ang, r)

            x, y = int(cx + dx), int(cy + dy)
            pygame.draw.line(surface, FG, (cx, cy), (x, y), 2)
            pygame.draw.circle(surface, FG, (x, y), 3)
            text(surface, name, x + 5, y - 5)
            text(surface, str(mag), x + 5, y + 5)

        text(surface, "Phasor page " + str(self.page + 1) + "/" + str(self.pages), 66, 280)


class SettingsPage(Page):
    """Settings editor page"""
    title = "Settings"

    def __init__(self, client):
        self.client = client
        self.items = [list(item) for item in SETTINGS[self.client.relay_id]]  # Deep copy settings
        for i, (name, ref, value_type, default) in enumerate(SETTINGS[self.client.relay_id]):
            self.items[i][3] = str(value_type( self.client.get_setting(ref) or default ))
        
        self.sel = 0
        self.edit = False
        self.visible = False
        self.cursor = 0

    def handle_key(self, key, stack):
        if not self.edit:
            if key == pygame.K_DOWN:
                self.sel = (self.sel + 1) % len(self.items)
            elif key == pygame.K_UP:
                self.sel = (self.sel - 1) % len(self.items)
            elif key == pygame.K_RETURN:
                self.edit = True
                self.cursor = len(self.items[self.sel][3]) - 1
            elif key == pygame.K_ESCAPE:
                self.visible = False
                stack.pop()
        else:
            ref = self.items[self.sel][1]
            if self.items[self.sel][2] is int or self.items[self.sel][2] is float:
                val = list(self.items[self.sel][3])
                if key == pygame.K_LEFT:
                    self.cursor = max(0, self.cursor - 1)
                elif key == pygame.K_RIGHT:
                    self.cursor = min(len(val) - 1, self.cursor + 1)
                elif key == pygame.K_UP and val[self.cursor].isdigit():
                    val[self.cursor] = str((int(val[self.cursor]) + 1) % 10)
                elif key == pygame.K_DOWN and val[self.cursor].isdigit():
                    val[self.cursor] = str((int(val[self.cursor]) - 1) % 10)
                self.items[self.sel][3] = "".join(val) # store temporary value

            if self.items[self.sel][2] is bool:
                if (key == pygame.K_UP or key == pygame.K_DOWN):
                    self.items[self.sel][3] = str((self.items[self.sel][3]) != "True" ) # invert value
                    
            if key == pygame.K_RETURN:
                value_type = self.items[self.sel][2]
                if value_type is bool:
                    self.client.set_setting(ref,self.items[self.sel][3] == "True")
                else:
                    self.client.set_setting(ref,value_type (self.items[self.sel][3]))
                self.client.write_setting(self.items[self.sel][1],self.items[self.sel][3])
                self.edit = False
                self.visible = False
            elif key == pygame.K_ESCAPE:
                self.edit = False
                self.visible = False
            

    def draw(self, surface):
        if self.visible == False: # init condition; get current values
            for i, (name, ref, value_type, default) in enumerate(SETTINGS[self.client.relay_id]):
                self.items[i][3] = str(value_type( self.client.get_setting(ref) or default ))
            self.visible = True

        y = 40
        for i, (name, ref, _, val) in enumerate(self.items):
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

    def __init__(self, message: str, msg_type: str = "info", on_result = None):
        """
        Args:
            message: Text to display in the popup
            msg_type: Type of message - "info", "confirm", or "error"
        """
        self.message = message
        self.msg_type = msg_type
        self.on_result = on_result
        if msg_type == "confirm":
            self.left = "Cancel"
        else:
            self.left = " OK"
        self.right = "  OK"

    def handle_key(self, key, stack):
        if key == pygame.K_ESCAPE:
            if self.on_result:
                self.on_result(False)
            if len(stack) > 1:
                stack.pop()
        if key == pygame.K_RETURN:
            if self.on_result:
                self.on_result(True)
            if len(stack) > 1:
                stack.pop()

    def draw(self, surface):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(100)
        overlay.fill(INV_BG)
        surface.blit(overlay, (0, 0))

        # Draw popup box
        box_width = 200
        box_height = 100
        box_x = (surface.get_width() - box_width) // 2
        box_y = (surface.get_height() - box_height) // 2
        pygame.draw.rect(surface, BG, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surface, FG, (box_x, box_y, box_width, box_height), 2)

        # Draw message (wrapped)
        max_width = box_width - 16  # padding
        msg_y = box_y + 15 
        words = self.message.split() 
        line = ""
        for word in words:
            test_line = line + (" " if line else "") + word
            if FONT.size(test_line)[0] > max_width:
                text_width, _ = FONT.size(line)
                x = box_x + (box_width - text_width) // 2
                text(surface, line, x, msg_y, FG)
                msg_y += FONT_H + 2
                line = word
            else:
                line = test_line
        if line:
            text_width, _ = FONT.size(line)
            x = box_x + (box_width - text_width) // 2
            text(surface, line, x, msg_y, FG)

        # Draw OK button label
        if self.msg_type == "confirm":
            text(surface, "[CANCEL]", box_x, box_y + box_height - 18, FG)
            text(surface, "[OK]", box_x + 165, box_y + box_height - 18, FG)
        else:
            text(surface, "[OK]", box_x + 83, box_y + box_height - 18, FG)


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


# =====================================================
# LCD UTILITIES
# =====================================================
def draw_lcd_header(surface, breadcrumb):
    """Draw LCD header"""
    pygame.draw.rect(surface, FG, (0, 0, 272, 20))
    breadcrumb_text = " > ".join(breadcrumb)
    if len(breadcrumb_text) > 29:
        breadcrumb_text = breadcrumb_text[-29:]
    text(surface, breadcrumb_text, 10, 3, INV_FG)


def draw_lcd_footer(surface, left="Back", right="Select"):
    """Draw LCD footer at the bottom"""
    footer_y = surface.get_height() - 20
    pygame.draw.rect(surface, FG, (0, footer_y, surface.get_width(), 20))
    text(surface, left, 6, footer_y + 3, INV_FG)
    text(surface, right, 198, footer_y + 3, INV_FG)
