"""
Drawing utilities for single-line diagrams and symbols
"""
import math
import pygame

from config import FG, BG, SYMBOLS


# =====================================================
# FONT UTILITIES
# =====================================================
FONT_H = 14
FONT = pygame.font.SysFont("courier", FONT_H, bold=True)


def text(surface, txt, x, y, fg=FG, bg=None):
    """Render text on surface"""
    surf = FONT.render(txt, False, fg, bg)
    surface.blit(surf, (x, y))


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


def draw_single_line(surface, object_list, highlighted_object):
    """Draw single-line diagram with optional highlighting"""
    index = -1
    for i, obj in enumerate(object_list):
        if obj["type"] == "symbol":
            name = obj["name"]
            if "state" in obj: # use a drawing, depending on the state, open, close, intermediate, error, etc.
                name = name + "_" + obj['state']
                
            draw_symbol(
                surface,
                name,
                obj["position"],
                obj.get("rotation", 0),
            )
            if "selectable" in obj:
                index = index + 1
                if index != -1 and index == highlighted_object and cursor_on():
                    swap_fg_bg(surface, pygame.Rect(obj["position"][0]-15, obj["position"][1]-15, 30, 30), FG, (185, 200, 215))
        elif obj["type"] == "text":
            text(surface, obj["formatted_text"], obj["position"][0],obj["position"][1])
        elif obj["type"] == "primitive":
            draw_primitive(surface, obj["primitive"])


def swap_fg_bg(surface, rect, fg, bg):
    """Swap foreground and background colors in a rectangular region"""
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


def cursor_on(period_ms=500):
    """Return True if cursor should be visible based on blink period"""
    return (pygame.time.get_ticks() // period_ms) % 2 == 0


def polar_to_xy(mag, angle_deg, scale):
    """Convert polar coordinates to XY"""
    rad = math.radians(angle_deg)
    return (
        mag * math.cos(rad) * scale,
        -mag * math.sin(rad) * scale
    )
