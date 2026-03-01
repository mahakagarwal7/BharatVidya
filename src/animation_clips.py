# src/animation_clips.py

"""
Topic-based animation clip generators.
Creates MoviePy VideoClip objects with frame-by-frame animations for educational topics.
This is an ADDITIVE module - does not modify existing rendering pipeline.

DOMAIN-SPECIFIC VISUAL GRAMMARS:
================================
Each scientific domain has a distinct visual language to prevent conceptual mode collapse:

1. PHYSICS - Lab/experiment aesthetic
   - Dark blue/purple gradients (night sky feel)
   - Vector arrows, trajectory paths
   - Grid backgrounds, measurement markers
   - Motion blur effects, dotted paths
   - Colors: Blue, cyan, orange highlights

2. CHEMISTRY - Molecular/lab aesthetic
   - Dark green/teal gradients (chemical feel)
   - Spherical atoms, bond lines
   - Periodic table colors (CPK convention)
   - Glowing orbitals, particle effects
   - Colors: Element-specific (C=gray, O=red, H=white, N=blue)

3. MATHEMATICS - Clean/geometric aesthetic
   - Pure black or dark gray backgrounds
   - Crisp white/colored lines
   - Coordinate grids, axes
   - Number labels, equation overlays
   - Colors: White, gold, purple for highlights

4. COMPUTER SCIENCE - Digital/tech aesthetic
   - Dark backgrounds with neon accents
   - Rectangular boxes, binary patterns
   - Step-by-step highlighting
   - Code-like typography
   - Colors: Neon green, cyan, magenta
"""

import numpy as np
import math
import random
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip
from typing import Optional, Tuple, List, Dict

# Video dimensions
WIDTH = 960
HEIGHT = 540


# ============================================================
# DOMAIN-SPECIFIC VISUAL THEMES
# ============================================================

class DomainTheme:
    """Base class for domain-specific visual themes."""
    
    # Physics theme - Lab/experiment aesthetic
    PHYSICS = {
        "bg_top": (15, 20, 45),          # Deep navy
        "bg_bottom": (30, 45, 80),        # Lighter navy
        "primary": (100, 180, 255),       # Sky blue
        "secondary": (255, 180, 100),     # Orange
        "accent": (150, 255, 200),        # Cyan-green
        "text": (220, 235, 255),          # Light blue-white
        "grid": (40, 60, 100),            # Subtle blue grid
        "highlight": (255, 220, 100),     # Golden highlight
        "border_style": "dashed",         # Measurement style
        "particle_style": "glow",         # Glowing particles
    }
    
    # Chemistry theme - Molecular/lab aesthetic
    CHEMISTRY = {
        "bg_top": (15, 35, 30),           # Dark teal
        "bg_bottom": (25, 55, 50),        # Lighter teal
        "primary": (100, 255, 200),       # Mint green
        "secondary": (255, 100, 100),     # Oxygen red
        "accent": (200, 150, 255),        # Violet
        "text": (220, 255, 240),          # Light mint
        "grid": (30, 50, 45),             # Subtle teal grid
        "highlight": (255, 220, 150),     # Warm glow
        "border_style": "orbital",        # Electron orbit style
        "particle_style": "molecular",    # Solid spheres
        # CPK atom colors
        "carbon": (80, 80, 80),
        "hydrogen": (220, 220, 255),
        "oxygen": (255, 80, 80),
        "nitrogen": (80, 80, 255),
        "sulfur": (255, 255, 80),
    }
    
    # Mathematics theme - Clean geometric aesthetic
    MATH = {
        "bg_top": (10, 10, 15),           # Near black
        "bg_bottom": (25, 25, 35),        # Dark gray
        "primary": (255, 255, 255),       # Pure white
        "secondary": (255, 200, 100),     # Gold
        "accent": (180, 100, 255),        # Purple
        "text": (255, 255, 255),          # White
        "grid": (50, 50, 70),             # Visible gray grid
        "highlight": (100, 255, 200),     # Teal highlight
        "border_style": "solid",          # Clean lines
        "particle_style": "point",        # Mathematical points
        "axis_color": (150, 150, 180),    # Gray axes
    }
    
    # Computer Science theme - Digital/tech aesthetic
    CS = {
        "bg_top": (5, 15, 20),            # Almost black with tint
        "bg_bottom": (15, 30, 40),        # Dark with blue tint
        "primary": (0, 255, 180),         # Neon green
        "secondary": (255, 100, 200),     # Magenta
        "accent": (100, 200, 255),        # Cyan
        "text": (200, 255, 230),          # Greenish white
        "grid": (20, 40, 50),             # Subtle tech grid
        "highlight": (255, 255, 100),     # Yellow highlight
        "border_style": "pixel",          # Sharp edges
        "particle_style": "binary",       # Digital particles
        "box_fill": (20, 50, 60),         # Dark box fill
        "box_active": (40, 80, 100),      # Active box
        "box_highlight": (80, 200, 150),  # Highlighted box
    }


def _get_theme(domain: str) -> Dict:
    """Get the visual theme for a domain."""
    themes = {
        "physics": DomainTheme.PHYSICS,
        "chemistry": DomainTheme.CHEMISTRY,
        "math": DomainTheme.MATH,
        "cs": DomainTheme.CS,
    }
    return themes.get(domain, DomainTheme.PHYSICS)


def _draw_domain_background(draw: ImageDraw, size: Tuple[int, int], 
                            theme: Dict, domain: str):
    """Draw domain-specific background with visual grammar."""
    w, h = size
    color_top = theme["bg_top"]
    color_bottom = theme["bg_bottom"]
    grid_color = theme["grid"]
    
    # Base gradient
    for y in range(h):
        ratio = y / h
        r = int(color_top[0] + ratio * (color_bottom[0] - color_top[0]))
        g = int(color_top[1] + ratio * (color_bottom[1] - color_top[1]))
        b = int(color_top[2] + ratio * (color_bottom[2] - color_top[2]))
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    # Domain-specific overlays
    if domain == "physics":
        # Draw subtle measurement grid (lab aesthetic)
        for x in range(0, w, 80):
            for y_pos in range(0, h, 5):
                if y_pos % 20 == 0:
                    draw.line([(x, y_pos), (x, y_pos + 2)], fill=grid_color, width=1)
        for y in range(0, h, 80):
            for x_pos in range(0, w, 5):
                if x_pos % 20 == 0:
                    draw.line([(x_pos, y), (x_pos + 2, y)], fill=grid_color, width=1)
    
    elif domain == "chemistry":
        # Draw hexagonal pattern overlay (molecular aesthetic)
        hex_size = 60
        for row in range(0, h + hex_size, int(hex_size * 1.5)):
            offset = (row // int(hex_size * 1.5)) % 2 * (hex_size // 2)
            for col in range(-hex_size, w + hex_size, hex_size):
                cx = col + offset
                cy = row
                # Subtle hexagon outline
                for i in range(6):
                    angle1 = math.pi / 6 + i * math.pi / 3
                    angle2 = math.pi / 6 + (i + 1) * math.pi / 3
                    x1 = cx + 20 * math.cos(angle1)
                    y1 = cy + 20 * math.sin(angle1)
                    x2 = cx + 20 * math.cos(angle2)
                    y2 = cy + 20 * math.sin(angle2)
                    if 0 <= cx <= w and 0 <= cy <= h:
                        draw.line([(x1, y1), (x2, y2)], fill=grid_color, width=1)
    
    elif domain == "math":
        # Draw coordinate grid (mathematical aesthetic)
        for x in range(0, w, 40):
            alpha = 30 if x % 80 == 0 else 15
            line_color = tuple(min(255, c + alpha) for c in color_bottom)
            draw.line([(x, 0), (x, h)], fill=line_color, width=1)
        for y in range(0, h, 40):
            alpha = 30 if y % 80 == 0 else 15
            line_color = tuple(min(255, c + alpha) for c in color_bottom)
            draw.line([(0, y), (w, y)], fill=line_color, width=1)
    
    elif domain == "cs":
        # Draw binary/digital pattern (tech aesthetic)
        random.seed(42)  # Consistent pattern
        for row in range(0, h, 30):
            for col in range(0, w, 20):
                if random.random() < 0.15:
                    # Binary-like dots
                    draw.ellipse([col, row, col + 3, row + 3], fill=grid_color)


def _draw_domain_title(draw: ImageDraw, title: str, theme: Dict, domain: str, 
                       font, y_pos: int = 25):
    """Draw domain-styled title with visual grammar."""
    text_color = theme["text"]
    accent = theme["accent"]
    
    # Calculate title width for centering
    try:
        bbox = draw.textbbox((0, 0), title, font=font)
        title_w = bbox[2] - bbox[0]
    except:
        title_w = len(title) * 15
    
    title_x = (WIDTH - title_w) // 2
    
    # Domain-specific title styling
    if domain == "physics":
        # Underline with measurement markers
        draw.text((title_x, y_pos), title, fill=text_color, font=font)
        line_y = y_pos + 35
        draw.line([(title_x - 20, line_y), (title_x + title_w + 20, line_y)], 
                  fill=accent, width=2)
        # Small tick marks
        for i in range(0, title_w + 40, 20):
            tick_h = 5 if i % 40 == 0 else 3
            draw.line([(title_x - 20 + i, line_y), (title_x - 20 + i, line_y + tick_h)],
                     fill=accent, width=1)
    
    elif domain == "chemistry":
        # Orbital-style decoration
        draw.text((title_x, y_pos), title, fill=text_color, font=font)
        # Electron orbit ellipse around title
        draw.arc([title_x - 30, y_pos - 10, title_x + title_w + 30, y_pos + 45],
                0, 360, fill=accent, width=1)
    
    elif domain == "math":
        # Clean mathematical style with brackets
        draw.text((title_x, y_pos), title, fill=text_color, font=font)
        # Mathematical brackets
        bracket_h = 35
        draw.line([(title_x - 25, y_pos), (title_x - 15, y_pos)], fill=accent, width=2)
        draw.line([(title_x - 25, y_pos), (title_x - 25, y_pos + bracket_h)], fill=accent, width=2)
        draw.line([(title_x - 25, y_pos + bracket_h), (title_x - 15, y_pos + bracket_h)], fill=accent, width=2)
        # Right bracket
        draw.line([(title_x + title_w + 15, y_pos), (title_x + title_w + 25, y_pos)], fill=accent, width=2)
        draw.line([(title_x + title_w + 25, y_pos), (title_x + title_w + 25, y_pos + bracket_h)], fill=accent, width=2)
        draw.line([(title_x + title_w + 15, y_pos + bracket_h), (title_x + title_w + 25, y_pos + bracket_h)], fill=accent, width=2)
    
    elif domain == "cs":
        # Terminal/code style
        # Prompt-like prefix
        draw.text((title_x - 30, y_pos), ">", fill=theme["primary"], font=font)
        draw.text((title_x, y_pos), title, fill=text_color, font=font)
        # Blinking cursor effect (static in animation)
        draw.rectangle([title_x + title_w + 10, y_pos + 5, title_x + title_w + 20, y_pos + 30],
                      fill=theme["primary"])


def _load_font(size: int):
    """Load a font with fallbacks."""
    font_paths = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _draw_gradient_bg(draw: ImageDraw, size: Tuple[int, int], 
                       color_top: Tuple[int, int, int], 
                       color_bottom: Tuple[int, int, int]):
    """Draw vertical gradient background."""
    w, h = size
    for y in range(h):
        ratio = y / h
        r = int(color_top[0] + ratio * (color_bottom[0] - color_top[0]))
        g = int(color_top[1] + ratio * (color_bottom[1] - color_top[1]))
        b = int(color_top[2] + ratio * (color_bottom[2] - color_top[2]))
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_arrow_head(draw: ImageDraw, x1: float, y1: float, x2: float, y2: float,
                     color: Tuple[int, int, int], size: int = 10):
    """Draw an arrow head at the end of a vector."""
    angle = math.atan2(y2 - y1, x2 - x1)
    # Calculate arrow head points
    angle1 = angle + math.pi * 0.85
    angle2 = angle - math.pi * 0.85
    ax1 = x2 + size * math.cos(angle1)
    ay1 = y2 + size * math.sin(angle1)
    ax2 = x2 + size * math.cos(angle2)
    ay2 = y2 + size * math.sin(angle2)
    draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=color)


# ============================================================
# PROJECTILE MOTION ANIMATION (PHYSICS DOMAIN)
# ============================================================

def create_projectile_clip(duration: float = 5.0, 
                           velocity: float = 50.0, 
                           angle: float = 45.0,
                           title: str = "Projectile Motion") -> VideoClip:
    """
    Create animated projectile motion clip.
    Shows parabolic trajectory with velocity vectors.
    Uses PHYSICS visual grammar: measurement grid, vector arrows, lab aesthetic.
    """
    theme = _get_theme("physics")
    g = 9.8
    angle_rad = math.radians(angle)
    vx = velocity * math.cos(angle_rad)
    vy = velocity * math.sin(angle_rad)
    
    # Calculate trajectory range
    t_flight = 2 * vy / g
    max_range = vx * t_flight
    max_height = (vy ** 2) / (2 * g)
    
    # Scaling for display
    margin = 100
    scale_x = (WIDTH - 2 * margin) / max(max_range, 1)
    scale_y = (HEIGHT - 250) / max(max_height, 1)
    scale = min(scale_x, scale_y) * 0.8
    
    ground_y = HEIGHT - 100
    origin_x = margin
    
    font_title = _load_font(28)
    font_label = _load_font(16)
    font_info = _load_font(18)
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background with measurement grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title with measurement markers
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Ground line with measurement markers
        draw.line([(margin - 20, ground_y), (WIDTH - margin + 20, ground_y)], 
                  fill=theme["primary"], width=2)
        # Distance markers on ground
        for i in range(0, int(WIDTH - 2 * margin), 50):
            marker_x = margin + i
            draw.line([(marker_x, ground_y), (marker_x, ground_y + 8)], 
                     fill=theme["grid"], width=1)
        
        # Draw trajectory path (full parabola) - dotted physics style
        path_points = []
        for i in range(100):
            ti = i * t_flight / 100
            px = origin_x + vx * ti * scale
            py = ground_y - (vy * ti - 0.5 * g * ti * ti) * scale
            path_points.append((px, py))
        
        # Draw as dotted path (physics lab style)
        for i in range(0, len(path_points) - 1, 2):
            if i + 1 < len(path_points):
                draw.line([path_points[i], path_points[i + 1]], 
                         fill=theme["accent"], width=1)
        
        # Current position based on animation time
        progress = min(t / duration, 1.0)
        current_t = progress * t_flight
        
        ball_x = origin_x + vx * current_t * scale
        ball_y = ground_y - (vy * current_t - 0.5 * g * current_t * current_t) * scale
        
        # Trail (previous positions) - motion blur physics effect
        for i in range(20):
            past_t = current_t - (i + 1) * 0.05
            if past_t > 0:
                px = origin_x + vx * past_t * scale
                py = ground_y - (vy * past_t - 0.5 * g * past_t * past_t) * scale
                alpha = int(255 * (1 - i / 20))
                radius = max(2, 8 - i // 3)
                # Fading trail with theme primary color
                fade_color = tuple(int(c * (1 - i/20)) for c in theme["primary"])
                draw.ellipse([px - radius, py - radius, px + radius, py + radius],
                            fill=fade_color)
        
        # Ball (highlighted physics object)
        radius = 12
        draw.ellipse([ball_x - radius, ball_y - radius, ball_x + radius, ball_y + radius],
                    fill=theme["secondary"], outline=theme["highlight"], width=2)
        
        # Velocity vector arrow (physics vector style)
        current_vy = vy - g * current_t
        arrow_scale = 1.5
        arrow_end_x = ball_x + vx * arrow_scale
        arrow_end_y = ball_y - current_vy * arrow_scale
        draw.line([(ball_x, ball_y), (arrow_end_x, arrow_end_y)], 
                 fill=theme["accent"], width=3)
        # Arrowhead
        _draw_arrow_head(draw, ball_x, ball_y, arrow_end_x, arrow_end_y, theme["accent"])
        
        # Info box with physics styling
        info_y = HEIGHT - 70
        draw.rectangle([margin - 10, info_y - 5, WIDTH - margin + 10, HEIGHT - 15],
                      outline=theme["grid"], width=1)
        draw.text((margin, info_y), f"v₀ = {velocity} m/s  θ = {angle}°", 
                  fill=theme["text"], font=font_info)
        draw.text((margin, info_y + 25), f"Range: {max_range:.1f}m  Max Height: {max_height:.1f}m",
                  fill=theme["primary"], font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# SINE WAVE ANIMATION
# ============================================================

def create_sine_wave_clip(duration: float = 5.0,
                          amplitude: float = 1.0,
                          frequency: float = 1.0,
                          title: str = "Sine Wave") -> VideoClip:
    """
    Create animated sine wave clip.
    Shows wave propagation with amplitude and period labels.
    Uses PHYSICS visual grammar: measurement markers, wave annotations.
    """
    theme = _get_theme("physics")
    
    font_title = _load_font(28)
    font_label = _load_font(16)
    font_info = _load_font(18)
    
    center_y = HEIGHT // 2
    wave_amplitude = 120  # pixels
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Axis lines with physics styling
        draw.line([(50, center_y), (WIDTH - 50, center_y)], fill=theme["primary"], width=1)
        draw.line([(100, center_y - 150), (100, center_y + 150)], fill=theme["primary"], width=1)
        
        # Phase shift based on time
        phase = t * 2 * math.pi * frequency
        
        # Draw sine wave
        wave_points = []
        for x in range(100, WIDTH - 50):
            x_val = (x - 100) / 80  # Scale for wave display
            y_val = wave_amplitude * amplitude * math.sin(x_val * frequency * 2 + phase)
            wave_points.append((x, center_y - y_val))
        
        if len(wave_points) >= 2:
            draw.line(wave_points, fill=(80, 230, 255), width=3)
        
        # Moving point on wave
        point_x = 100 + (t % 2) * 200  # Moves along wave
        x_val = (point_x - 100) / 80
        point_y = center_y - wave_amplitude * amplitude * math.sin(x_val * frequency * 2 + phase)
        draw.ellipse([point_x - 8, point_y - 8, point_x + 8, point_y + 8],
                    fill=(255, 200, 100), outline=(255, 255, 255))
        
        # Amplitude indicator
        amp_x = 70
        draw.line([(amp_x, center_y), (amp_x, center_y - wave_amplitude)], 
                  fill=(255, 150, 150), width=2)
        draw.line([(amp_x - 5, center_y - wave_amplitude), (amp_x + 5, center_y - wave_amplitude)],
                  fill=(255, 150, 150), width=2)
        draw.text((amp_x - 50, center_y - wave_amplitude // 2 - 8), "A", 
                  fill=(255, 180, 180), font=font_label)
        
        # Info box
        info_y = HEIGHT - 70
        draw.text((100, info_y), f"y = A·sin(ωt + φ)", fill=(200, 230, 255), font=font_info)
        draw.text((100, info_y + 25), f"Amplitude: {amplitude}  Frequency: {frequency} Hz",
                  fill=(180, 210, 240), font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# BUBBLE SORT ANIMATION (CS DOMAIN)
# ============================================================

def create_bubble_sort_clip(duration: float = 8.0,
                            array: Optional[List[int]] = None,
                            title: str = "Bubble Sort") -> VideoClip:
    """
    Create animated bubble sort visualization.
    Shows step-by-step sorting with comparisons highlighted.
    Uses CS visual grammar: neon accents, digital boxes, tech aesthetic.
    """
    theme = _get_theme("cs")
    
    if array is None:
        array = [64, 34, 25, 12, 22, 11, 90]
    
    arr = list(array)
    n = len(arr)
    max_val = max(arr)
    
    # Pre-compute all sorting states
    states = [list(arr)]
    comparisons = []  # (i, j, swapped)
    
    arr_copy = list(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr_copy[j] > arr_copy[j + 1]:
                arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                comparisons.append((j, j + 1, True))
            else:
                comparisons.append((j, j + 1, False))
            states.append(list(arr_copy))
    
    total_steps = len(states)
    
    font_title = _load_font(28)
    font_value = _load_font(16)
    font_info = _load_font(18)
    
    bar_width = min(80, (WIDTH - 200) // n)
    bar_gap = 10
    start_x = (WIDTH - (bar_width + bar_gap) * n) // 2
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # CS themed background with digital pattern
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "cs")
        
        # CS styled title (terminal prompt style)
        _draw_domain_title(draw, title, theme, "cs", font_title)
        
        # Current state based on time
        progress = min(t / duration, 0.99)
        state_idx = int(progress * total_steps)
        current_state = states[min(state_idx, len(states) - 1)]
        
        # Get comparison info
        compare_i, compare_j, swapped = -1, -1, False
        if state_idx > 0 and state_idx <= len(comparisons):
            compare_i, compare_j, swapped = comparisons[state_idx - 1]
        
        # Draw bars with CS neon styling
        ground_y = HEIGHT - 120
        max_bar_height = 280
        
        for i, val in enumerate(current_state):
            bar_height = int((val / max_val) * max_bar_height)
            x = start_x + i * (bar_width + bar_gap)
            y = ground_y - bar_height
            
            # Color based on comparison state - CS neon colors
            if i == compare_i or i == compare_j:
                if swapped:
                    color = theme["secondary"]  # Magenta for swap
                    outline_color = (255, 150, 220)
                else:
                    color = theme["primary"]  # Neon green for no swap
                    outline_color = (100, 255, 200)
            else:
                color = theme["box_fill"]  # Dark tech fill
                outline_color = theme["accent"]  # Cyan outline
            
            # Sharp pixel-style boxes
            draw.rectangle([x, y, x + bar_width, ground_y], 
                          fill=color, outline=outline_color, width=2)
            
            # Value label with monospace-style look
            text_x = x + bar_width // 2 - 10
            draw.text((text_x, y - 25), str(val), fill=theme["text"], font=font_value)
        
        # Index labels below bars
        for i in range(len(current_state)):
            x = start_x + i * (bar_width + bar_gap)
            draw.text((x + bar_width // 2 - 5, ground_y + 5), f"[{i}]", 
                     fill=theme["grid"], font=_load_font(12))
        
        # Info box with terminal styling
        info_y = HEIGHT - 50
        step_text = f"Step {state_idx}/{total_steps - 1}"
        if state_idx == total_steps - 1:
            step_text = "// SORTED"
            draw.text((WIDTH // 2 - 50, info_y), step_text, fill=theme["primary"], font=font_info)
        else:
            draw.text((WIDTH // 2 - 50, info_y), step_text, fill=theme["text"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# BINARY SEARCH ANIMATION (CS DOMAIN)
# ============================================================

def create_binary_search_clip(duration: float = 8.0,
                              array: Optional[List[int]] = None,
                              target: int = 7,
                              title: str = "Binary Search") -> VideoClip:
    """
    Create animated binary search visualization.
    Shows narrowing search range with low/mid/high pointers.
    Uses CS visual grammar: neon accents, array boxes, algorithm steps.
    """
    theme = _get_theme("cs")
    
    if array is None:
        array = [1, 3, 5, 7, 9, 11, 13, 15]
    
    arr = list(array)
    n = len(arr)
    
    # Pre-compute search states: (low, high, mid, found)
    states = []
    low, high = 0, n - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            states.append((low, high, mid, True))
            break
        elif arr[mid] < target:
            states.append((low, high, mid, False))
            low = mid + 1
        else:
            states.append((low, high, mid, False))
            high = mid - 1
    
    # Handle case where target is not found - show "not found" state with valid indices
    if not states:
        # Empty array edge case
        states.append((0, 0, 0, False))
    elif not states[-1][3]:
        # Target not found - add final state showing search ended
        # Use the last valid mid position, clamped to array bounds
        last_low, last_high, last_mid, _ = states[-1]
        final_mid = max(0, min(n - 1, last_mid))
        states.append((last_low, last_high, final_mid, False))
    
    total_steps = len(states)
    
    font_title = _load_font(28)
    font_value = _load_font(18)
    font_label = _load_font(14)
    font_info = _load_font(18)
    
    box_size = min(70, (WIDTH - 150) // n)
    box_gap = 8
    start_x = (WIDTH - (box_size + box_gap) * n) // 2
    center_y = HEIGHT // 2 - 20
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # CS themed background with digital pattern
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "cs")
        
        # CS styled title
        _draw_domain_title(draw, title, theme, "cs", font_title)
        
        # Target indicator with terminal style
        draw.text((WIDTH // 2 - 80, 65), f"target = {target}", fill=theme["secondary"], font=font_info)
        
        # Current state
        progress = min(t / duration, 0.99)
        state_idx = int(progress * total_steps)
        low, high, mid, found = states[min(state_idx, len(states) - 1)]
        
        # Draw array boxes with CS styling
        for i, val in enumerate(arr):
            x = start_x + i * (box_size + box_gap)
            y = center_y
            
            # Color based on state - CS neon colors
            if found and i == mid:
                fill_color = theme["primary"]  # Neon green - found!
                outline_color = (150, 255, 220)
            elif i < low or i > high:
                fill_color = (15, 25, 35)  # Very dark - eliminated
                outline_color = theme["grid"]
            elif i == mid:
                fill_color = theme["highlight"]  # Yellow - current check
                outline_color = (255, 255, 150)
            elif i == low or i == high:
                fill_color = theme["accent"]  # Cyan - boundaries
                outline_color = (150, 220, 255)
            else:
                fill_color = theme["box_active"]  # Active area
                outline_color = theme["accent"]
            
            # Sharp pixel-style boxes
            draw.rectangle([x, y, x + box_size, y + box_size], 
                          fill=fill_color, outline=outline_color, width=2)
            
            # Value in monospace style
            text_x = x + box_size // 2 - 8
            text_color = theme["text"] if not (i < low or i > high) else theme["grid"]
            draw.text((text_x, y + box_size // 2 - 10), str(val), fill=text_color, font=font_value)
            
            # Index label below
            draw.text((text_x, y + box_size + 5), f"[{i}]", fill=theme["grid"], font=font_label)
        
        # Pointer labels with neon styling
        pointer_y = center_y - 35
        if low <= n - 1:
            lx = start_x + low * (box_size + box_gap) + box_size // 2 - 15
            draw.text((lx, pointer_y), "low", fill=theme["accent"], font=font_label)
            # Arrow down
            draw.polygon([(lx + 12, pointer_y + 20), (lx + 7, pointer_y + 12), (lx + 17, pointer_y + 12)],
                        fill=theme["accent"])
        
        if high >= 0 and high <= n - 1:
            hx = start_x + high * (box_size + box_gap) + box_size // 2 - 15
            draw.text((hx, pointer_y - 15), "high", fill=theme["accent"], font=font_label)
            draw.polygon([(hx + 12, pointer_y + 5), (hx + 7, pointer_y - 3), (hx + 17, pointer_y - 3)],
                        fill=theme["accent"])
        
        if 0 <= mid < n:
            mx = start_x + mid * (box_size + box_gap) + box_size // 2 - 15
            draw.text((mx, center_y + box_size + 25), "mid", fill=theme["highlight"], font=font_label)
        
        # Status with terminal styling
        info_y = HEIGHT - 80
        if found:
            status = f"// FOUND: arr[{mid}] == {target}"
            status_color = theme["primary"]
        else:
            status = f"// Step {state_idx + 1}: checking arr[{mid}] = {arr[mid] if mid < n else '?'}"
            status_color = theme["text"]
        draw.text((WIDTH // 2 - 150, info_y), status, fill=status_color, font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# QUADRATIC GRAPH ANIMATION (MATH DOMAIN)
# ============================================================

def create_quadratic_clip(duration: float = 5.0,
                          a: float = 1.0,
                          b: float = -3.0,
                          c: float = 2.0,
                          title: str = "Quadratic Function") -> VideoClip:
    """
    Create animated quadratic function graph.
    Shows parabola being drawn with vertex and roots marked.
    Uses MATH visual grammar: clean grid, coordinate axes, precise labels.
    """
    theme = _get_theme("math")
    
    # Calculate properties
    discriminant = b * b - 4 * a * c
    vertex_x = -b / (2 * a)
    vertex_y = a * vertex_x ** 2 + b * vertex_x + c
    
    roots = []
    if discriminant >= 0:
        r1 = (-b + math.sqrt(discriminant)) / (2 * a)
        r2 = (-b - math.sqrt(discriminant)) / (2 * a)
        roots = sorted([r1, r2])
    
    font_title = _load_font(26)
    font_eq = _load_font(22)
    font_label = _load_font(14)
    font_info = _load_font(16)
    
    # Graph area
    graph_center_x = WIDTH // 2
    graph_center_y = HEIGHT // 2 + 20
    scale = 40  # pixels per unit
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # MATH themed background with coordinate grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "math")
        
        # MATH styled title with brackets
        _draw_domain_title(draw, title, theme, "math", font_title)
        
        # Equation display (mathematical notation)
        eq_text = f"f(x) = {a}x² + {b}x + {c}" if b >= 0 else f"f(x) = {a}x² {b}x + {c}"
        draw.text((WIDTH // 2 - 90, 60), eq_text, fill=theme["secondary"], font=font_eq)
        
        # Draw coordinate axes with tick marks
        draw.line([(50, graph_center_y), (WIDTH - 50, graph_center_y)], 
                 fill=theme["axis_color"], width=2)
        draw.line([(graph_center_x, 100), (graph_center_x, HEIGHT - 80)], 
                 fill=theme["axis_color"], width=2)
        
        # Tick marks on axes
        for x_tick in range(-5, 6):
            tick_px = graph_center_x + x_tick * scale
            if 50 < tick_px < WIDTH - 50 and x_tick != 0:
                draw.line([(tick_px, graph_center_y - 4), (tick_px, graph_center_y + 4)],
                         fill=theme["primary"], width=1)
                draw.text((tick_px - 5, graph_center_y + 8), str(x_tick),
                         fill=theme["grid"], font=_load_font(10))
        
        for y_tick in range(-3, 4):
            tick_py = graph_center_y - y_tick * scale
            if 100 < tick_py < HEIGHT - 80 and y_tick != 0:
                draw.line([(graph_center_x - 4, tick_py), (graph_center_x + 4, tick_py)],
                         fill=theme["primary"], width=1)
                draw.text((graph_center_x + 8, tick_py - 6), str(y_tick),
                         fill=theme["grid"], font=_load_font(10))
        
        # Axis labels with mathematical style
        draw.text((WIDTH - 45, graph_center_y - 25), "x", fill=theme["primary"], font=font_label)
        draw.text((graph_center_x + 12, 102), "y", fill=theme["primary"], font=font_label)
        
        # Draw parabola progressively
        progress = min(t / (duration * 0.7), 1.0)  # Complete by 70% of duration
        
        x_range = 5
        points = []
        num_points = int(200 * progress)
        
        for i in range(num_points):
            x = -x_range + (2 * x_range * i / 200)
            y = a * x * x + b * x + c
            px = graph_center_x + x * scale
            py = graph_center_y - y * scale
            
            if 50 < px < WIDTH - 50 and 90 < py < HEIGHT - 70:
                points.append((px, py))
        
        if len(points) >= 2:
            draw.line(points, fill=theme["secondary"], width=3)
        
        # Mark vertex (after curve is drawn) - mathematical point
        if progress > 0.7:
            vx_px = graph_center_x + vertex_x * scale
            vy_px = graph_center_y - vertex_y * scale
            if 50 < vx_px < WIDTH - 50 and 90 < vy_px < HEIGHT - 70:
                draw.ellipse([vx_px - 6, vy_px - 6, vx_px + 6, vy_px + 6],
                            fill=theme["highlight"], outline=theme["primary"])
                draw.text((vx_px + 10, vy_px - 5), f"V({vertex_x:.1f}, {vertex_y:.1f})",
                          fill=theme["highlight"], font=font_label)
        
        # Mark roots (after vertex) - mathematical points on x-axis
        if progress > 0.85 and roots:
            for root in roots:
                rx_px = graph_center_x + root * scale
                if 50 < rx_px < WIDTH - 50:
                    draw.ellipse([rx_px - 5, graph_center_y - 5, rx_px + 5, graph_center_y + 5],
                                fill=theme["accent"])
                    draw.text((rx_px - 10, graph_center_y + 12), f"{root:.1f}",
                              fill=theme["accent"], font=font_label)
        
        # Info box with mathematical precision
        info_y = HEIGHT - 55
        draw.rectangle([80, info_y - 5, WIDTH - 80, HEIGHT - 15],
                      outline=theme["grid"], width=1)
        info_text = f"Vertex: ({vertex_x:.2f}, {vertex_y:.2f})"
        if roots:
            info_text += f"  |  Roots: x = {roots[0]:.2f}, {roots[1]:.2f}"
        draw.text((100, info_y), info_text, fill=theme["primary"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# PENDULUM ANIMATION (PHYSICS DOMAIN)
# ============================================================

def create_pendulum_clip(duration: float = 5.0,
                         length: float = 1.0,
                         max_angle: float = 30.0,
                         title: str = "Simple Pendulum") -> VideoClip:
    """
    Create animated pendulum motion.
    Shows oscillation with angle and period information.
    Uses PHYSICS visual grammar: vector annotations, measurement style.
    """
    theme = _get_theme("physics")
    
    g = 9.8
    period = 2 * math.pi * math.sqrt(length / g)
    omega = 2 * math.pi / period
    max_angle_rad = math.radians(max_angle)
    
    pivot_x = WIDTH // 2
    pivot_y = 120
    rope_length = 250  # pixels
    
    font_title = _load_font(28)
    font_info = _load_font(18)
    font_label = _load_font(14)
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background with measurement grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Current angle (simple harmonic motion)
        angle = max_angle_rad * math.cos(omega * t)
        
        # Calculate bob position
        bob_x = pivot_x + rope_length * math.sin(angle)
        bob_y = pivot_y + rope_length * math.cos(angle)
        
        # Draw pivot with physics lab style
        draw.ellipse([pivot_x - 8, pivot_y - 8, pivot_x + 8, pivot_y + 8],
                    fill=theme["grid"], outline=theme["primary"])
        
        # Draw rope/string
        draw.line([(pivot_x, pivot_y), (bob_x, bob_y)], fill=theme["text"], width=3)
        
        # Draw bob with physics highlighting
        bob_radius = 25
        draw.ellipse([bob_x - bob_radius, bob_y - bob_radius, 
                     bob_x + bob_radius, bob_y + bob_radius],
                    fill=theme["secondary"], outline=theme["highlight"], width=2)
        
        # Draw arc showing swing range (measurement style)
        arc_radius = 80
        left_angle = 90 - max_angle
        right_angle = 90 + max_angle
        draw.arc([pivot_x - arc_radius, pivot_y - arc_radius,
                 pivot_x + arc_radius, pivot_y + arc_radius],
                left_angle, right_angle, fill=theme["primary"], width=2)
        
        # Angle indicator line (vertical reference - dashed style)
        for y_dash in range(pivot_y, pivot_y + 100, 8):
            draw.line([(pivot_x, y_dash), (pivot_x, min(y_dash + 4, pivot_y + 100))],
                      fill=theme["grid"], width=1)
        
        # Current angle text with physics notation
        angle_deg = math.degrees(angle)
        draw.text((pivot_x + 50, pivot_y + 40), f"θ = {angle_deg:.1f}°",
                  fill=theme["accent"], font=font_label)
        
        # Velocity vector at bob (tangent to motion)
        velocity = -max_angle_rad * omega * rope_length * math.sin(omega * t) / 5
        v_dx = velocity * math.cos(angle)
        v_dy = -velocity * math.sin(angle)
        if abs(velocity) > 5:
            draw.line([(bob_x, bob_y), (bob_x + v_dx, bob_y + v_dy)], 
                     fill=theme["accent"], width=2)
            _draw_arrow_head(draw, bob_x, bob_y, bob_x + v_dx, bob_y + v_dy, theme["accent"], 8)
        
        # Info box with physics measurements
        info_y = HEIGHT - 80
        draw.rectangle([80, info_y - 10, WIDTH - 80, HEIGHT - 20],
                      outline=theme["grid"], width=1)
        draw.text((100, info_y), f"L = {length} m  |  T = {period:.2f} s",
                  fill=theme["text"], font=font_info)
        draw.text((100, info_y + 25), f"θ_max = ±{max_angle}°  |  g = 9.8 m/s²",
                  fill=theme["primary"], font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# LINEAR EQUATION / GRAPH ANIMATION (MATH DOMAIN)
# ============================================================

def create_linear_equation_clip(duration: float = 5.0,
                                 slope: float = 2.0,
                                 intercept: float = 1.0,
                                 title: str = "Linear Equation") -> VideoClip:
    """
    Create animated linear equation graph.
    Shows line being drawn with slope and y-intercept highlighted.
    Uses MATH visual grammar: clean coordinate grid, mathematical notation.
    """
    theme = _get_theme("math")
    
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(16)
    
    # Graph area
    margin = 80
    graph_left = margin + 40
    graph_right = WIDTH - margin
    graph_top = 100
    graph_bottom = HEIGHT - 80
    graph_width = graph_right - graph_left
    graph_height = graph_bottom - graph_top
    
    # X and Y ranges
    x_range = (-5, 5)
    y_range = (-5, 10)
    
    def world_to_screen(x, y):
        sx = graph_left + (x - x_range[0]) / (x_range[1] - x_range[0]) * graph_width
        sy = graph_bottom - (y - y_range[0]) / (y_range[1] - y_range[0]) * graph_height
        return int(sx), int(sy)
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # MATH themed background with coordinate grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "math")
        
        # MATH styled title
        _draw_domain_title(draw, title, theme, "math", font_title)
        
        # Draw axes with math styling
        origin = world_to_screen(0, 0)
        
        # X-axis
        draw.line([world_to_screen(x_range[0], 0), world_to_screen(x_range[1], 0)],
                  fill=theme["axis_color"], width=2)
        # Y-axis  
        draw.line([world_to_screen(0, y_range[0]), world_to_screen(0, y_range[1])],
                  fill=theme["axis_color"], width=2)
        
        # Axis labels (mathematical style)
        draw.text((graph_right - 20, origin[1] + 5), "x", fill=theme["primary"], font=font_label)
        draw.text((origin[0] + 10, graph_top - 5), "y", fill=theme["primary"], font=font_label)
        
        # Grid lines (subtle math grid)
        for x in range(int(x_range[0]), int(x_range[1]) + 1):
            if x != 0:
                sx, _ = world_to_screen(x, 0)
                draw.line([(sx, graph_top), (sx, graph_bottom)], fill=theme["grid"], width=1)
                draw.text((sx - 5, origin[1] + 10), str(x), fill=theme["grid"], font=font_info)
        
        for y in range(int(y_range[0]), int(y_range[1]) + 1):
            if y != 0:
                _, sy = world_to_screen(0, y)
                draw.line([(graph_left, sy), (graph_right, sy)], fill=theme["grid"], width=1)
                draw.text((origin[0] - 25, sy - 8), str(y), fill=theme["grid"], font=font_info)
        
        # Animate line drawing
        progress = min(1.0, t / (duration * 0.6))
        
        # Calculate line points
        x_start = x_range[0]
        x_end = x_range[0] + (x_range[1] - x_range[0]) * progress
        
        if progress > 0:
            y_start = slope * x_start + intercept
            y_end = slope * x_end + intercept
            
            # Clip to graph bounds
            points = []
            for px in np.linspace(x_start, x_end, 50):
                py = slope * px + intercept
                if y_range[0] <= py <= y_range[1]:
                    points.append(world_to_screen(px, py))
            
            if len(points) >= 2:
                draw.line(points, fill=theme["secondary"], width=3)
        
        # Show y-intercept (mathematical point)
        if t > duration * 0.3:
            y_int_pos = world_to_screen(0, intercept)
            draw.ellipse([y_int_pos[0] - 6, y_int_pos[1] - 6, 
                         y_int_pos[0] + 6, y_int_pos[1] + 6],
                        fill=theme["accent"], outline=theme["primary"])
            draw.text((y_int_pos[0] + 15, y_int_pos[1] - 10), 
                     f"b = {intercept:.1f}", fill=theme["accent"], font=font_label)
        
        # Show equation (mathematical notation)
        if t > duration * 0.5:
            eq_text = f"y = {slope:.1f}x + {intercept:.1f}" if intercept >= 0 else f"y = {slope:.1f}x - {abs(intercept):.1f}"
            draw.text((50, HEIGHT - 60), eq_text, fill=theme["highlight"], font=font_title)
        
        # Show slope visualization
        if t > duration * 0.7:
            # Draw rise/run triangle
            x1, y1 = 1, slope * 1 + intercept
            x2, y2 = 2, slope * 2 + intercept
            p1 = world_to_screen(x1, y1)
            p2 = world_to_screen(x2, y1)  # Horizontal
            p3 = world_to_screen(x2, y2)
            
            draw.line([p1, p2], fill=theme["secondary"], width=2)  # Run
            draw.line([p2, p3], fill=theme["accent"], width=2)  # Rise
            draw.text((p2[0] + 10, (p2[1] + p3[1]) // 2), f"m = {slope:.1f}",
                     fill=theme["highlight"], font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# HEAT / THERMODYNAMICS ANIMATION (PHYSICS DOMAIN)
# ============================================================

def create_heat_clip(duration: float = 5.0,
                     title: str = "Heat & Temperature") -> VideoClip:
    """
    Create animated heat/thermodynamics visualization.
    Shows temperature gauge, particle motion, and heat transfer.
    Uses PHYSICS visual grammar: measurement style, particle motion.
    """
    theme = _get_theme("physics")
    
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(16)
    
    import random
    random.seed(42)
    
    # Create particles for visualization
    class Particle:
        def __init__(self, x, y, temp_zone):
            self.x = x
            self.y = y
            self.temp_zone = temp_zone  # 'hot' or 'cold'
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-2, 2)
            
        def update(self, t, speed_mult):
            self.x += self.vx * speed_mult
            self.y += self.vy * speed_mult
            
            # Bounce off boundaries
            if self.temp_zone == 'hot':
                if self.x < 500 or self.x > 850:
                    self.vx *= -1
                if self.y < 150 or self.y > 400:
                    self.vy *= -1
            else:
                if self.x < 100 or self.x > 450:
                    self.vx *= -1
                if self.y < 150 or self.y > 400:
                    self.vy *= -1
    
    # Initialize particles
    hot_particles = [Particle(random.randint(520, 830), random.randint(170, 380), 'hot') for _ in range(25)]
    cold_particles = [Particle(random.randint(120, 430), random.randint(170, 380), 'cold') for _ in range(25)]
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Draw two containers
        # Cold container (left)
        draw.rectangle([100, 150, 450, 400], outline=theme["primary"], width=3)
        draw.text((220, 410), "Cold", fill=theme["primary"], font=font_label)
        
        # Hot container (right) - use highlight color for heat
        hot_color = theme["highlight"]
        draw.rectangle([500, 150, 850, 400], outline=hot_color, width=3)
        draw.text((630, 410), "Hot", fill=hot_color, font=font_label)
        
        # Animated temperature transfer
        transfer_progress = min(1.0, t / (duration * 0.8))
        
        # Draw heat flow arrows with physics vector styling
        if t > duration * 0.3:
            arrow_alpha = int(200 * (0.5 + 0.5 * math.sin(t * 4)))
            for i in range(3):
                y_pos = 200 + i * 70
                # Arrow from hot to cold using highlight color
                draw.line([(480, y_pos), (460, y_pos)], fill=theme["secondary"], width=2)
                _draw_arrow_head(draw, 480, y_pos, 460, y_pos, theme["secondary"], 12)
        
        # Update and draw particles
        for p in hot_particles:
            p.update(t, 1.5)  # Hot particles move faster
            # Use highlight colors for hot particles
            h_r, h_g, h_b = theme["highlight"]
            color = (h_r, int(h_g + 50 * math.sin(t * 5 + p.x)), h_b)
            draw.ellipse([p.x - 4, p.y - 4, p.x + 4, p.y + 4], fill=color)
        
        for p in cold_particles:
            p.update(t, 0.5)  # Cold particles move slower
            # Use primary colors for cold particles
            c_r, c_g, c_b = theme["primary"]
            color = (c_r, int(c_g + 50 * math.sin(t * 2 + p.y)), c_b)
            draw.ellipse([p.x - 4, p.y - 4, p.x + 4, p.y + 4], fill=color)
        
        # Temperature gauge with physics lab styling
        gauge_x = 50
        gauge_y = 150
        gauge_height = 250
        temp = 0.3 + 0.4 * transfer_progress + 0.1 * math.sin(t * 2)
        
        # Gauge background
        draw.rectangle([gauge_x - 10, gauge_y, gauge_x + 10, gauge_y + gauge_height],
                      outline=theme["grid"], fill=theme["bg_bottom"], width=2)
        
        # Temperature fill - gradient from primary to highlight
        fill_height = int(gauge_height * temp)
        p_r, p_g, p_b = theme["primary"]
        h_r, h_g, h_b = theme["highlight"]
        for i in range(fill_height):
            ratio = i / gauge_height
            r = int(p_r + (h_r - p_r) * ratio)
            g = int(p_g + (h_g - p_g) * ratio)
            b = int(p_b + (h_b - p_b) * ratio)
            y = gauge_y + gauge_height - i
            draw.line([(gauge_x - 8, y), (gauge_x + 8, y)], fill=(r, g, b))
        
        # Gauge bulb
        draw.ellipse([gauge_x - 15, gauge_y + gauge_height - 5, 
                     gauge_x + 15, gauge_y + gauge_height + 25],
                    fill=theme["highlight"], outline=theme["secondary"])
        
        # Temperature label
        temp_c = int(20 + 80 * temp)
        draw.text((gauge_x - 20, gauge_y - 30), f"{temp_c}°C", 
                 fill=theme["secondary"], font=font_label)
        
        # Info text with physics styling
        info_y = HEIGHT - 50
        draw.text((WIDTH // 2 - 200, info_y), 
                 "Heat flows from hot to cold regions",
                 fill=theme["text"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# GEOMETRY / SHAPES ANIMATION
# ============================================================

def create_geometry_clip(duration: float = 5.0,
                         title: str = "Geometry") -> VideoClip:
    """
    Create animated geometry visualization.
    Shows shapes, angles, and geometric properties.
    """
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(16)
    
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 + 20
    
    # MATH domain theme for geometry
    theme = _get_theme("math")
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # MATH themed background with coordinate grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "math")
        
        # MATH styled title
        _draw_domain_title(draw, title, theme, "math", font_title)
        
        # Rotating shapes
        rotation = t * 0.5  # Radians per second
        
        # Draw triangle (rotating) - using primary color
        tri_radius = 80
        tri_center = (center_x - 200, center_y)
        tri_points = []
        for i in range(3):
            angle = rotation + i * (2 * math.pi / 3) - math.pi / 2
            x = tri_center[0] + tri_radius * math.cos(angle)
            y = tri_center[1] + tri_radius * math.sin(angle)
            tri_points.append((x, y))
        draw.polygon(tri_points, outline=theme["primary"], width=3)
        draw.text((tri_center[0] - 30, tri_center[1] + 100), "Triangle", 
                 fill=theme["primary"], font=font_label)
        
        # Draw square (rotating) - using secondary color
        sq_radius = 60
        sq_center = (center_x, center_y)
        sq_points = []
        for i in range(4):
            angle = -rotation + i * (2 * math.pi / 4) + math.pi / 4
            x = sq_center[0] + sq_radius * math.cos(angle)
            y = sq_center[1] + sq_radius * math.sin(angle)
            sq_points.append((x, y))
        draw.polygon(sq_points, outline=theme["secondary"], width=3)
        draw.text((sq_center[0] - 25, sq_center[1] + 100), "Square", 
                 fill=theme["secondary"], font=font_label)
        
        # Draw circle (pulsing) - using highlight color
        circle_center = (center_x + 200, center_y)
        pulse = 1 + 0.1 * math.sin(t * 3)
        circle_radius = int(60 * pulse)
        draw.ellipse([circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                     circle_center[0] + circle_radius, circle_center[1] + circle_radius],
                    outline=theme["highlight"], width=3)
        draw.text((circle_center[0] - 20, circle_center[1] + 100), "Circle", 
                 fill=theme["highlight"], font=font_label)
        
        # Show angle measurement in triangle
        if t > duration * 0.3:
            angle_arc_radius = 25
            # Draw angle arc at first vertex
            p0, p1, p2 = tri_points[0], tri_points[1], tri_points[2]
            draw.arc([p0[0] - angle_arc_radius, p0[1] - angle_arc_radius,
                     p0[0] + angle_arc_radius, p0[1] + angle_arc_radius],
                    0, 60, fill=theme["accent"], width=2)
            draw.text((p0[0] + 15, p0[1] - 25), "60°", fill=theme["accent"], font=font_info)
        
        # Show formulas with math notation styling
        if t > duration * 0.5:
            formula_y = HEIGHT - 80
            draw.text((100, formula_y), "A = ½bh", fill=theme["primary"], font=font_label)
            draw.text((400, formula_y), "A = s²", fill=theme["secondary"], font=font_label)
            draw.text((700, formula_y), "A = πr²", fill=theme["highlight"], font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# CHEMISTRY / ATOMS ANIMATION (CHEMISTRY DOMAIN)
# ============================================================

def create_chemistry_clip(duration: float = 5.0,
                          title: str = "Chemistry") -> VideoClip:
    """
    Create animated chemistry/atomic visualization.
    Shows atoms, electron orbits, and molecular bonds.
    Uses CHEMISTRY visual grammar: hexagonal patterns, CPK colors, orbital style.
    """
    theme = _get_theme("chemistry")
    
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(16)
    
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 + 20
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # CHEMISTRY themed background with hexagonal molecular pattern
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "chemistry")
        
        # CHEMISTRY styled title with orbital decoration
        _draw_domain_title(draw, title, theme, "chemistry", font_title)
        
        # Draw atom model
        atom_center = (center_x, center_y)
        
        # Nucleus (using chemistry theme colors)
        nucleus_radius = 25
        draw.ellipse([atom_center[0] - nucleus_radius, atom_center[1] - nucleus_radius,
                     atom_center[0] + nucleus_radius, atom_center[1] + nucleus_radius],
                    fill=theme["secondary"], outline=theme["highlight"])
        
        # Protons and neutrons in nucleus (CPK-inspired colors)
        for i in range(4):
            angle = i * math.pi / 2 + t * 0.5
            px = atom_center[0] + 10 * math.cos(angle)
            py = atom_center[1] + 10 * math.sin(angle)
            color = theme["secondary"] if i % 2 == 0 else theme["nitrogen"]  # Red/Blue
            draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=color)
        
        # Electron orbits (chemistry orbital style)
        orbit_radii = [70, 120, 170]
        electrons_per_orbit = [2, 4, 2]
        
        for orbit_idx, (radius, n_electrons) in enumerate(zip(orbit_radii, electrons_per_orbit)):
            # Draw orbit path with chemistry styling
            draw.ellipse([atom_center[0] - radius, atom_center[1] - radius,
                         atom_center[0] + radius, atom_center[1] + radius],
                        outline=theme["accent"], width=1)
            
            # Draw electrons with molecular glow
            speed = (3 - orbit_idx) * 0.8  # Inner orbits faster
            for e in range(n_electrons):
                angle = t * speed + e * (2 * math.pi / n_electrons)
                ex = atom_center[0] + radius * math.cos(angle)
                ey = atom_center[1] + radius * math.sin(angle)
                
                # Electron glow (chemistry style)
                draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], 
                           fill=theme["grid"])
                draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], 
                           fill=theme["primary"])
        
        # Labels with chemistry styling
        draw.text((atom_center[0] - 45, atom_center[1] + 190), "Atomic Model",
                 fill=theme["text"], font=font_label)
        
        # Info panel (chemistry legend style)
        if t > duration * 0.3:
            info_x = 50
            info_y = HEIGHT - 100
            # Draw legend box
            draw.rectangle([info_x - 10, info_y - 10, info_x + 160, info_y + 70],
                          outline=theme["grid"], width=1)
            draw.text((info_x, info_y), "● Protons (+)", fill=theme["secondary"], font=font_info)
            draw.text((info_x, info_y + 22), "● Neutrons", fill=theme["nitrogen"], font=font_info)
            draw.text((info_x, info_y + 44), "● Electrons (-)", fill=theme["primary"], font=font_info)
        
        # Energy levels (shell notation)
        if t > duration * 0.5:
            draw.text((WIDTH - 150, 120), "K shell (n=1)", fill=theme["primary"], font=font_info)
            draw.text((WIDTH - 150, 145), "L shell (n=2)", fill=theme["primary"], font=font_info)
            draw.text((WIDTH - 150, 170), "M shell (n=3)", fill=theme["primary"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# WAVE / PHYSICS ANIMATION (PHYSICS DOMAIN)
# ============================================================

def create_wave_clip(duration: float = 5.0,
                     title: str = "Wave Motion") -> VideoClip:
    """
    Create animated wave visualization for general physics topics.
    Shows wave propagation, amplitude, wavelength.
    Uses PHYSICS visual grammar: measurement markers, vector annotations.
    """
    theme = _get_theme("physics")
    
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(16)
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background with measurement grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Wave parameters
        amplitude = 80
        wavelength = 200
        wave_y = HEIGHT // 2
        
        # Draw axis
        draw.line([(50, wave_y), (WIDTH - 50, wave_y)], fill=(100, 140, 180), width=1)
        
        # Draw wave
        points = []
        phase = t * 2  # Wave moves right
        
        for x in range(50, WIDTH - 50, 3):
            y = wave_y - amplitude * math.sin(2 * math.pi * (x - 50) / wavelength - phase)
            points.append((x, int(y)))
        
        if len(points) >= 2:
            draw.line(points, fill=(100, 200, 255), width=3)
        
        # Second wave (different phase for interference visualization)
        if t > duration * 0.4:
            points2 = []
            for x in range(50, WIDTH - 50, 3):
                y = wave_y - (amplitude * 0.6) * math.sin(2 * math.pi * (x - 50) / (wavelength * 0.7) - phase * 1.3)
                points2.append((x, int(y)))
            
            if len(points2) >= 2:
                draw.line(points2, fill=(255, 180, 100), width=2)
        
        # Amplitude indicator
        if t > duration * 0.2:
            amp_x = 100
            draw.line([(amp_x, wave_y), (amp_x, wave_y - amplitude)], 
                     fill=(255, 150, 200), width=2)
            draw.line([(amp_x - 10, wave_y - amplitude), (amp_x + 10, wave_y - amplitude)],
                     fill=(255, 150, 200), width=2)
            draw.text((amp_x + 15, wave_y - amplitude // 2 - 10), "A",
                     fill=(255, 150, 200), font=font_label)
        
        # Wavelength indicator
        if t > duration * 0.3:
            wl_y = wave_y + 60
            wl_x1 = 150
            wl_x2 = 150 + wavelength
            draw.line([(wl_x1, wl_y), (wl_x2, wl_y)], fill=(150, 255, 150), width=2)
            draw.line([(wl_x1, wl_y - 10), (wl_x1, wl_y + 10)], fill=(150, 255, 150), width=2)
            draw.line([(wl_x2, wl_y - 10), (wl_x2, wl_y + 10)], fill=(150, 255, 150), width=2)
            draw.text([(wl_x1 + wl_x2) // 2 - 10, wl_y + 15], "λ",
                     fill=(150, 255, 150), font=font_label)
        
        # Wave equation
        if t > duration * 0.6:
            draw.text((WIDTH // 2 - 80, HEIGHT - 60), "y = A sin(kx - ωt)",
                     fill=(180, 220, 255), font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# STATISTICS / DATA VISUALIZATION ANIMATION
# ============================================================

def create_statistics_clip(duration: float = 5.0,
                           title: str = "Statistics") -> VideoClip:
    """
    Create animated statistics/data visualization.
    Shows bar chart, distribution curve, mean/median.
    """
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(14)
    
    import random
    random.seed(123)
    
    # Sample data
    data = [random.gauss(50, 15) for _ in range(7)]
    data = [max(10, min(90, d)) for d in data]  # Clamp values
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    
    # MATH domain theme for statistics
    theme = _get_theme("math")
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # MATH themed background with coordinate grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "math")
        
        # MATH styled title
        _draw_domain_title(draw, title, theme, "math", font_title)
        
        # Chart area
        chart_left = 100
        chart_right = WIDTH - 100
        chart_top = 100
        chart_bottom = HEIGHT - 100
        chart_height = chart_bottom - chart_top
        
        # Animate bar growth
        progress = min(1.0, t / (duration * 0.5))
        
        # Draw bars with math-themed color progression
        bar_width = (chart_right - chart_left) // len(data) - 20
        
        # Math theme colors - variations based on theme
        base_colors = [
            theme["primary"],      # White
            theme["secondary"],    # Gold
            theme["highlight"],    # Cyan
            theme["accent"],       # Yellow
            (180, 180, 255),       # Soft purple
            (255, 180, 180),       # Soft red
            (180, 255, 200)        # Soft green
        ]
        
        for i, (value, label) in enumerate(zip(data, labels)):
            x = chart_left + i * (bar_width + 20) + 10
            bar_height = int((value / 100) * chart_height * progress)
            y_top = chart_bottom - bar_height
            
            # Bar with gradient effect
            for j in range(bar_height):
                ratio = j / max(1, bar_height)
                color = tuple(int(c * (0.6 + 0.4 * ratio)) for c in base_colors[i])
                draw.line([(x, chart_bottom - j), (x + bar_width, chart_bottom - j)], fill=color)
            
            # Bar outline with grid color
            draw.rectangle([x, y_top, x + bar_width, chart_bottom], outline=theme["grid"], width=1)
            
            # Label
            draw.text((x + bar_width // 2 - 5, chart_bottom + 10), label,
                     fill=theme["text"], font=font_info)
            
            # Value
            if progress > 0.8:
                draw.text((x + bar_width // 2 - 10, y_top - 25), f"{value:.0f}",
                         fill=theme["primary"], font=font_info)
        
        # Calculate and show statistics
        if t > duration * 0.6:
            mean_val = sum(data) / len(data)
            sorted_data = sorted(data)
            median_val = sorted_data[len(data) // 2]
            
            stats_x = 50
            stats_y = 80
            draw.text((stats_x, stats_y), f"Mean: {mean_val:.1f}", 
                     fill=theme["highlight"], font=font_label)
            draw.text((stats_x + 150, stats_y), f"Median: {median_val:.1f}", 
                     fill=theme["secondary"], font=font_label)
        
        # Draw mean line
        if t > duration * 0.7:
            mean_val = sum(data) / len(data)
            mean_y = chart_bottom - int((mean_val / 100) * chart_height)
            draw.line([(chart_left, mean_y), (chart_right, mean_y)],
                     fill=theme["highlight"], width=2)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# GENERIC TOPIC ANIMATION (for any topic)
# ============================================================

def create_generic_clip(duration: float = 5.0,
                        title: str = "Educational Topic",
                        keywords: Optional[List[str]] = None) -> VideoClip:
    """
    Create a generic animated clip for any topic.
    Uses floating keywords, particles, and dynamic visuals.
    
    Args:
        duration: Animation duration in seconds
        title: Topic title to display
        keywords: Optional list of keywords to animate (extracted from title if not provided)
    """
    import re
    import random
    
    # Use PHYSICS theme as default for generic content
    theme = _get_theme("physics")
    
    # Extract keywords from title if not provided
    if not keywords:
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'of', 'in', 'to', 'for', 'and', 'or', 'is', 
                      'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
                      'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                      'may', 'might', 'must', 'shall', 'can', 'with', 'by', 'from',
                      'up', 'about', 'into', 'through', 'during', 'before', 'after',
                      'above', 'below', 'between', 'under', 'again', 'further', 'then',
                      'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                      'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                      'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                      'just', 'also', 'now', 'explain', 'understanding', 'introduction'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
        keywords = [w.capitalize() for w in words if w.lower() not in stop_words][:6]
    
    if not keywords:
        keywords = ["Learn", "Explore", "Discover"]
    
    # Generate random seed for consistent animation
    random.seed(hash(title) % 10000)
    
    # Create floating keyword particles with random properties
    class KeywordParticle:
        def __init__(self, word, index, total):
            self.word = word
            self.start_x = random.randint(100, WIDTH - 200)
            self.start_y = random.randint(150, HEIGHT - 150)
            self.amplitude_x = random.uniform(20, 60)
            self.amplitude_y = random.uniform(15, 40)
            self.freq_x = random.uniform(0.3, 0.8)
            self.freq_y = random.uniform(0.4, 0.9)
            self.phase = random.uniform(0, 2 * math.pi)
            self.appear_time = index * 0.3  # Stagger appearance
            self.color = self._get_color(index)
            
        def _get_color(self, index):
            # Use physics theme colors
            colors = [
                theme["primary"],    # Cyan-blue
                theme["secondary"],  # Light cyan
                theme["highlight"],  # Orange/highlight
                theme["accent"],     # Yellow
                (150, 200, 255),     # Light blue
                (200, 230, 255),     # Pale blue
            ]
            return colors[index % len(colors)]
        
        def get_position(self, t):
            x = self.start_x + self.amplitude_x * math.sin(self.freq_x * t * 2 * math.pi + self.phase)
            y = self.start_y + self.amplitude_y * math.sin(self.freq_y * t * 2 * math.pi + self.phase * 1.5)
            return int(x), int(y)
        
        def get_alpha(self, t):
            if t < self.appear_time:
                return 0
            fade_in = min(1.0, (t - self.appear_time) / 0.5)
            return fade_in
    
    # Create background particles
    class BackgroundParticle:
        def __init__(self):
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
            self.speed = random.uniform(20, 60)
            self.size = random.randint(2, 5)
            self.alpha = random.uniform(0.3, 0.7)
            
        def get_position(self, t):
            x = (self.x + self.speed * t) % WIDTH
            y = self.y + 10 * math.sin(t * 2 + self.x / 50)
            return int(x), int(y)
    
    # Initialize particles
    keyword_particles = [KeywordParticle(kw, i, len(keywords)) for i, kw in enumerate(keywords)]
    bg_particles = [BackgroundParticle() for _ in range(30)]
    
    font_title = _load_font(32)
    font_keyword = _load_font(24)
    font_small = _load_font(14)
    
    # Reset random seed
    random.seed()
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # Draw background particles using theme colors
        for bp in bg_particles:
            px, py = bp.get_position(t)
            p_r, p_g, p_b = theme["primary"]
            color = (p_r // 2, p_g // 2, p_b // 2)
            draw.ellipse([px - bp.size, py - bp.size, px + bp.size, py + bp.size],
                        fill=color)
        
        # Draw connecting lines between keywords (constellation effect)
        positions = []
        for kp in keyword_particles:
            if kp.get_alpha(t) > 0.5:
                positions.append(kp.get_position(t))
        
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                if dist < 300:
                    alpha = int(100 * (1 - dist / 300))
                    draw.line([pos1, pos2], fill=theme["grid"], width=1)
        
        # Draw floating keywords
        for kp in keyword_particles:
            alpha = kp.get_alpha(t)
            if alpha > 0:
                x, y = kp.get_position(t)
                # Glow effect
                glow_color = tuple(int(c * 0.3) for c in kp.color)
                for offset in range(3, 0, -1):
                    draw.text((x - offset, y), kp.word, fill=glow_color, font=font_keyword)
                # Main text
                color = tuple(int(c * alpha) for c in kp.color)
                draw.text((x, y), kp.word, fill=kp.color, font=font_keyword)
        
        # Draw title at top with pulsing effect
        pulse = 0.9 + 0.1 * math.sin(t * 3)
        title_color = tuple(int(c * pulse) for c in theme["text"])
        
        # Center title
        try:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            title_w = bbox[2] - bbox[0]
        except:
            title_w = len(title) * 15
        title_x = (WIDTH - title_w) // 2
        draw.text((title_x, 40), title, fill=title_color, font=font_title)
        
        # Decorative line under title
        line_y = 85
        line_progress = min(1.0, t / 1.0)
        line_w = int(300 * line_progress)
        draw.line([(WIDTH // 2 - line_w // 2, line_y), (WIDTH // 2 + line_w // 2, line_y)],
                  fill=theme["primary"], width=2)
        
        # Animated corner decorations
        corner_size = 40 + int(10 * math.sin(t * 2))
        corners = [(20, 20), (WIDTH - 60, 20), (20, HEIGHT - 60), (WIDTH - 60, HEIGHT - 60)]
        for cx, cy in corners:
            draw.arc([cx, cy, cx + corner_size, cy + corner_size],
                    0, 90, fill=theme["secondary"], width=2)
        
        # Progress indicator at bottom
        progress = t / duration
        bar_width = int((WIDTH - 200) * progress)
        draw.rectangle([100, HEIGHT - 30, 100 + bar_width, HEIGHT - 25],
                       fill=theme["primary"])
        draw.rectangle([100, HEIGHT - 30, WIDTH - 100, HEIGHT - 25],
                       outline=theme["grid"], width=1)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# COORDINATE GEOMETRY / GRAPHICAL ANALYSIS ANIMATION
# ============================================================

def create_coordinate_geometry_clip(duration: float = 5.0,
                                    title: str = "Coordinate Geometry") -> VideoClip:
    """
    Create animated coordinate geometry visualization.
    Shows coordinate axes, point plotting, distance formula, and midpoint.
    """
    font_title = _load_font(28)
    font_label = _load_font(16)
    font_info = _load_font(18)
    font_small = _load_font(14)
    
    # MATH domain theme for coordinate geometry
    theme = _get_theme("math")
    
    # Coordinate system setup
    origin_x = WIDTH // 2
    origin_y = HEIGHT // 2 + 30
    scale = 40  # pixels per unit
    
    # Points to plot
    point_a = (-3, 2)
    point_b = (4, -1)
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # MATH themed background with coordinate grid
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "math")
        
        # MATH styled title
        _draw_domain_title(draw, title, theme, "math", font_title)
        
        # Draw grid using theme colors
        for i in range(-10, 11):
            x = origin_x + i * scale
            y = origin_y - i * scale
            # Vertical grid lines
            if -5 <= i <= 5:
                draw.line([(x, origin_y - 5 * scale), (x, origin_y + 4 * scale)],
                         fill=theme["grid"], width=1)
                # Horizontal grid lines
                draw.line([(origin_x - 5 * scale, y), (origin_x + 5 * scale, y)],
                         fill=theme["grid"], width=1)
        
        # Draw axes with theme primary color
        draw.line([(origin_x - 220, origin_y), (origin_x + 220, origin_y)],
                  fill=theme["primary"], width=2)
        draw.line([(origin_x, origin_y - 180), (origin_x, origin_y + 160)],
                  fill=theme["primary"], width=2)
        
        # Axis labels
        draw.text((origin_x + 225, origin_y - 10), "X", fill=theme["primary"], font=font_label)
        draw.text((origin_x + 5, origin_y - 195), "Y", fill=theme["primary"], font=font_label)
        draw.text((origin_x + 5, origin_y + 5), "O", fill=theme["primary"], font=font_small)
        
        # Animate point plotting
        plot_time = duration * 0.3
        
        # Point A - appears first - using highlight color
        if t > duration * 0.15:
            ax = origin_x + point_a[0] * scale
            ay = origin_y - point_a[1] * scale
            # Pulsing effect
            pulse = 1 + 0.2 * math.sin(t * 4)
            r = int(8 * pulse)
            draw.ellipse([ax - r, ay - r, ax + r, ay + r], fill=theme["highlight"])
            draw.text((ax + 12, ay - 20), f"A({point_a[0]}, {point_a[1]})", 
                     fill=theme["highlight"], font=font_label)
        
        # Point B - appears second - using secondary color
        if t > duration * 0.3:
            bx = origin_x + point_b[0] * scale
            by = origin_y - point_b[1] * scale
            pulse = 1 + 0.2 * math.sin(t * 4 + 1)
            r = int(8 * pulse)
            draw.ellipse([bx - r, by - r, bx + r, by + r], fill=theme["secondary"])
            draw.text((bx + 12, by - 20), f"B({point_b[0]}, {point_b[1]})", 
                     fill=theme["secondary"], font=font_label)
        
        # Draw line segment connecting points
        if t > duration * 0.45:
            ax = origin_x + point_a[0] * scale
            ay = origin_y - point_a[1] * scale
            bx = origin_x + point_b[0] * scale
            by = origin_y - point_b[1] * scale
            
            # Animated line drawing
            line_progress = min(1.0, (t - duration * 0.45) / (duration * 0.2))
            curr_x = ax + (bx - ax) * line_progress
            curr_y = ay + (by - ay) * line_progress
            draw.line([(ax, ay), (curr_x, curr_y)], fill=theme["accent"], width=2)
        
        # Midpoint calculation
        if t > duration * 0.6:
            ax = origin_x + point_a[0] * scale
            ay = origin_y - point_a[1] * scale
            bx = origin_x + point_b[0] * scale
            by = origin_y - point_b[1] * scale
            
            mid_x = (ax + bx) // 2
            mid_y = (ay + by) // 2
            mid_coords = ((point_a[0] + point_b[0]) / 2, (point_a[1] + point_b[1]) / 2)
            
            # Draw midpoint using accent color
            pulse = 1 + 0.15 * math.sin(t * 5)
            r = int(6 * pulse)
            draw.ellipse([mid_x - r, mid_y - r, mid_x + r, mid_y + r], fill=theme["accent"])
            draw.text((mid_x + 10, mid_y + 5), f"M({mid_coords[0]}, {mid_coords[1]})", 
                     fill=theme["accent"], font=font_small)
        
        # Show distance formula with math notation styling
        if t > duration * 0.75:
            dx = point_b[0] - point_a[0]
            dy = point_b[1] - point_a[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            formula_y = HEIGHT - 60
            draw.text((80, formula_y), f"Distance = √[(x₂-x₁)² + (y₂-y₁)²]", 
                     fill=theme["text"], font=font_label)
            draw.text((520, formula_y), f"= √[{dx}² + {dy}²] = {dist:.2f}", 
                     fill=theme["highlight"], font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# ELECTRIC CIRCUIT ANIMATION
# ============================================================

def create_circuit_clip(duration: float = 5.0,
                        title: str = "Electric Circuit") -> VideoClip:
    """
    Create animated electric circuit visualization.
    Shows current flow, resistors, and voltage source.
    """
    font_title = _load_font(28)
    font_label = _load_font(16)
    font_info = _load_font(14)
    
    # PHYSICS domain theme for circuits
    theme = _get_theme("physics")
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Circuit layout
        cx, cy = WIDTH // 2, HEIGHT // 2 + 20
        rect_w, rect_h = 400, 200
        
        # Draw circuit rectangle (wires) using theme colors
        wire_color = theme["text"]
        # Top wire
        draw.line([(cx - rect_w//2, cy - rect_h//2), (cx + rect_w//2, cy - rect_h//2)],
                  fill=wire_color, width=3)
        # Right wire
        draw.line([(cx + rect_w//2, cy - rect_h//2), (cx + rect_w//2, cy + rect_h//2)],
                  fill=wire_color, width=3)
        # Bottom wire
        draw.line([(cx - rect_w//2, cy + rect_h//2), (cx + rect_w//2, cy + rect_h//2)],
                  fill=wire_color, width=3)
        # Left wire
        draw.line([(cx - rect_w//2, cy - rect_h//2), (cx - rect_w//2, cy + rect_h//2)],
                  fill=wire_color, width=3)
        
        # Draw battery (left side) - using highlight and primary colors
        batt_x = cx - rect_w//2 - 15
        batt_y = cy
        # Long line (positive) - highlight color
        draw.line([(batt_x, batt_y - 20), (batt_x, batt_y + 20)], fill=theme["highlight"], width=4)
        # Short line (negative) - primary color
        draw.line([(batt_x + 15, batt_y - 12), (batt_x + 15, batt_y + 12)], fill=theme["primary"], width=3)
        draw.text((batt_x - 30, batt_y + 30), "+  -", fill=theme["text"], font=font_info)
        draw.text((batt_x - 25, batt_y - 50), "9V", fill=theme["accent"], font=font_label)
        
        # Draw resistor (top) - using secondary color
        res_x = cx
        res_y = cy - rect_h//2
        zigzag_w = 60
        zigzag_h = 15
        points = [(res_x - zigzag_w, res_y)]
        for i in range(6):
            y_offset = zigzag_h if i % 2 == 0 else -zigzag_h
            points.append((res_x - zigzag_w + (i + 1) * 20, res_y + y_offset))
        points.append((res_x + zigzag_w, res_y))
        
        # Draw zigzag resistor with secondary color
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=theme["secondary"], width=3)
        draw.text((res_x - 15, res_y - 40), "R = 3Ω", fill=theme["secondary"], font=font_label)
        
        # Draw bulb (right side) - glowing with highlight color
        bulb_x = cx + rect_w//2 + 15
        bulb_y = cy
        bulb_r = 25
        # Bulb glow effect (pulsing)
        glow_intensity = 0.6 + 0.4 * math.sin(t * 5)
        h_r, h_g, h_b = theme["highlight"]
        glow_color = (int(h_r * glow_intensity), int(h_g * glow_intensity), int(h_b * 0.5 * glow_intensity))
        for r_off in range(15, 0, -3):
            alpha = int(100 * (1 - r_off / 15) * glow_intensity)
            draw.ellipse([bulb_x - bulb_r - r_off, bulb_y - bulb_r - r_off,
                         bulb_x + bulb_r + r_off, bulb_y + bulb_r + r_off],
                        fill=(int(h_r * alpha/255), int(h_g * 0.7 * alpha/255), int(50 * alpha/255)))
        draw.ellipse([bulb_x - bulb_r, bulb_y - bulb_r, bulb_x + bulb_r, bulb_y + bulb_r],
                    outline=theme["accent"], fill=glow_color, width=2)
        draw.text((bulb_x - 20, bulb_y + 35), "Bulb", fill=theme["accent"], font=font_info)
        
        # Animated current flow (electrons) - using primary color
        num_electrons = 12
        for i in range(num_electrons):
            phase = (t * 2 + i * 0.5) % 4
            
            if phase < 1:  # Top wire (left to right)
                ex = cx - rect_w//2 + phase * rect_w
                ey = cy - rect_h//2
            elif phase < 2:  # Right wire (top to bottom)
                ex = cx + rect_w//2
                ey = cy - rect_h//2 + (phase - 1) * rect_h
            elif phase < 3:  # Bottom wire (right to left)
                ex = cx + rect_w//2 - (phase - 2) * rect_w
                ey = cy + rect_h//2
            else:  # Left wire (bottom to top)
                ex = cx - rect_w//2
                ey = cy + rect_h//2 - (phase - 3) * rect_h
            
            # Draw electron with primary color
            e_size = 6
            draw.ellipse([ex - e_size, ey - e_size, ex + e_size, ey + e_size],
                        fill=theme["primary"])
            draw.text((ex - 3, ey - 5), "-", fill=theme["text"], font=font_info)
        
        # Current direction arrow
        arrow_x = cx
        arrow_y = cy + rect_h//2 + 30
        draw.line([(arrow_x - 50, arrow_y), (arrow_x + 50, arrow_y)], fill=theme["primary"], width=2)
        _draw_arrow_head(draw, arrow_x - 50, arrow_y, arrow_x - 60, arrow_y, theme["primary"], 12)
        draw.text((arrow_x - 70, arrow_y + 10), "Current (I)", fill=theme["primary"], font=font_info)
        
        # Ohm's law text with physics styling
        if t > duration * 0.4:
            draw.text((80, HEIGHT - 50), "Ohm's Law: V = I × R", fill=theme["text"], font=font_label)
            draw.text((350, HEIGHT - 50), "I = V/R = 9V/3Ω = 3A", fill=theme["highlight"], font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# OPTICS / LIGHT ANIMATION
# ============================================================

def create_optics_clip(duration: float = 5.0,
                       title: str = "Light & Optics") -> VideoClip:
    """
    Create animated optics visualization.
    Shows light reflection and refraction.
    Uses PHYSICS visual grammar: ray diagrams, measurement style.
    """
    theme = _get_theme("physics")
    
    font_title = _load_font(28)
    font_label = _load_font(16)
    font_info = _load_font(14)
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Mirror/glass surface (horizontal)
        surface_y = HEIGHT // 2 + 30
        surface_x1 = 100
        surface_x2 = WIDTH - 100
        
        # Draw surface with physics styling
        draw.line([(surface_x1, surface_y), (surface_x2, surface_y)], 
                  fill=theme["primary"], width=4)
        
        # Label surfaces
        draw.text((120, surface_y - 70), "Air (n=1.0)", fill=(180, 200, 220), font=font_label)
        draw.text((120, surface_y + 50), "Glass (n=1.5)", fill=(180, 200, 220), font=font_label)
        
        # Normal line (dashed)
        normal_x = WIDTH // 2 - 50
        for y in range(surface_y - 120, surface_y + 120, 15):
            draw.line([(normal_x, y), (normal_x, y + 8)], fill=(150, 150, 180), width=1)
        draw.text((normal_x - 35, surface_y - 140), "Normal", fill=(150, 150, 180), font=font_info)
        
        # Incident ray animation
        incident_start = (normal_x - 150, surface_y - 150)
        incident_end = (normal_x, surface_y)
        
        # Calculate ray animation progress
        ray_progress = min(1.0, t / (duration * 0.4))
        
        if ray_progress > 0:
            # Draw incident ray with animated glow
            for width in range(8, 1, -2):
                alpha = 100 - width * 10
                color = (255, int(200 + 55 * math.sin(t * 8)), 50)
                curr_x = incident_start[0] + (incident_end[0] - incident_start[0]) * ray_progress
                curr_y = incident_start[1] + (incident_end[1] - incident_start[1]) * ray_progress
                draw.line([incident_start, (curr_x, curr_y)], fill=color, width=width)
            
            draw.text((incident_start[0] - 30, incident_start[1] - 20), "Incident Ray", 
                     fill=(255, 220, 100), font=font_info)
        
        # After incident ray reaches surface
        if t > duration * 0.4:
            # Draw angle of incidence arc
            angle_radius = 40
            draw.arc([normal_x - angle_radius, surface_y - angle_radius,
                     normal_x + angle_radius, surface_y + angle_radius],
                    225, 270, fill=(255, 200, 100), width=2)
            draw.text((normal_x - 70, surface_y - 60), "θ₁=45°", fill=(255, 200, 100), font=font_info)
            
            # Reflected ray
            reflect_progress = min(1.0, (t - duration * 0.4) / (duration * 0.25))
            if reflect_progress > 0:
                reflect_end = (normal_x + 150, surface_y - 150)
                curr_x = incident_end[0] + (reflect_end[0] - incident_end[0]) * reflect_progress
                curr_y = incident_end[1] + (reflect_end[1] - incident_end[1]) * reflect_progress
                
                for width in range(6, 1, -2):
                    color = (100, 200, 255)
                    draw.line([incident_end, (curr_x, curr_y)], fill=color, width=width)
                
                if reflect_progress > 0.8:
                    draw.text((reflect_end[0] - 20, reflect_end[1] - 20), "Reflected Ray", 
                             fill=(100, 200, 255), font=font_info)
                    # Angle of reflection
                    draw.arc([normal_x - angle_radius, surface_y - angle_radius,
                             normal_x + angle_radius, surface_y + angle_radius],
                            270, 315, fill=(100, 200, 255), width=2)
                    draw.text((normal_x + 25, surface_y - 60), "θ₁'=45°", fill=(100, 200, 255), font=font_info)
            
            # Refracted ray
            refract_progress = min(1.0, (t - duration * 0.5) / (duration * 0.3))
            if refract_progress > 0:
                # Snell's law: n1*sin(θ1) = n2*sin(θ2)
                # θ2 = arcsin(1.0/1.5 * sin(45°)) ≈ 28°
                refract_end = (normal_x + 80, surface_y + 150)
                curr_x = incident_end[0] + (refract_end[0] - incident_end[0]) * refract_progress
                curr_y = incident_end[1] + (refract_end[1] - incident_end[1]) * refract_progress
                
                for width in range(6, 1, -2):
                    color = (150, 255, 150)
                    draw.line([incident_end, (curr_x, curr_y)], fill=color, width=width)
                
                if refract_progress > 0.8:
                    draw.text((refract_end[0] - 20, refract_end[1] + 5), "Refracted Ray", 
                             fill=(150, 255, 150), font=font_info)
                    # Angle of refraction
                    draw.arc([normal_x - angle_radius, surface_y - angle_radius,
                             normal_x + angle_radius, surface_y + angle_radius],
                            90, 118, fill=(150, 255, 150), width=2)
                    draw.text((normal_x - 70, surface_y + 25), "θ₂=28°", fill=(150, 255, 150), font=font_info)
        
        # Snell's law text
        if t > duration * 0.7:
            draw.text((80, HEIGHT - 55), "Snell's Law: n₁ sin θ₁ = n₂ sin θ₂", 
                     fill=(180, 220, 255), font=font_label)
            draw.text((450, HEIGHT - 55), "1.0 × sin(45°) = 1.5 × sin(28°)", 
                     fill=(150, 255, 150), font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# FORCE / NEWTON'S LAWS ANIMATION
# ============================================================

def create_force_clip(duration: float = 5.0,
                      title: str = "Forces & Newton's Laws") -> VideoClip:
    """
    Create animated force/Newton's laws visualization.
    Shows force vectors, mass, and acceleration.
    """
    font_title = _load_font(28)
    font_label = _load_font(16)
    font_info = _load_font(14)
    
    # PHYSICS domain theme for forces/mechanics
    theme = _get_theme("physics")
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # PHYSICS themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # PHYSICS styled title
        _draw_domain_title(draw, title, theme, "physics", font_title)
        
        # Ground line using grid color
        ground_y = HEIGHT - 100
        draw.line([(50, ground_y), (WIDTH - 50, ground_y)], fill=theme["grid"], width=2)
        
        # Moving box
        box_w, box_h = 80, 60
        # Accelerating motion
        acceleration = 50  # pixels per second^2
        initial_x = 150
        box_x = initial_x + 0.5 * acceleration * t * t
        box_x = min(box_x, WIDTH - 200)  # Limit position
        box_y = ground_y - box_h
        
        # Draw box with physics styled colors
        draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h],
                      fill=(100, 120, 150), outline=theme["text"], width=2)
        draw.text((box_x + 15, box_y + 20), "5 kg", fill=theme["primary"], font=font_label)
        
        # Force arrows - using theme colors
        arrow_y = box_y + box_h // 2
        
        # Applied force (right arrow) - pulsing - using highlight color
        pulse = 0.9 + 0.1 * math.sin(t * 6)
        f_length = int(120 * pulse)
        f_color = theme["highlight"]
        draw.line([(box_x + box_w, arrow_y), (box_x + box_w + f_length, arrow_y)],
                  fill=f_color, width=4)
        # Arrowhead using helper function
        _draw_arrow_head(draw, box_x + box_w + f_length, arrow_y, box_x + box_w + f_length + 15, arrow_y, f_color, 15)
        draw.text((box_x + box_w + 30, arrow_y - 35), "F = 20 N", fill=f_color, font=font_label)
        
        # Friction force (left arrow) - using accent color
        friction_length = 60
        fr_color = theme["accent"]
        draw.line([(box_x, arrow_y), (box_x - friction_length, arrow_y)],
                  fill=fr_color, width=3)
        _draw_arrow_head(draw, box_x - friction_length, arrow_y, box_x - friction_length - 12, arrow_y, fr_color, 12)
        draw.text((box_x - friction_length - 10, arrow_y - 30), "f = 5 N", fill=fr_color, font=font_info)
        
        # Normal force (up arrow) - using secondary color
        normal_length = 80
        n_color = theme["secondary"]
        draw.line([(box_x + box_w // 2, box_y + box_h), 
                  (box_x + box_w // 2, box_y + box_h + normal_length)],
                  fill=n_color, width=3)
        # Draw at bottom going down then flip
        n_start_y = box_y
        draw.line([(box_x + box_w // 2, n_start_y), 
                  (box_x + box_w // 2, n_start_y - normal_length)],
                  fill=n_color, width=3)
        _draw_arrow_head(draw, box_x + box_w // 2, n_start_y - normal_length, box_x + box_w // 2, n_start_y - normal_length - 12, n_color, 12)
        draw.text((box_x + box_w // 2 + 10, n_start_y - normal_length - 10), "N", 
                 fill=n_color, font=font_label)
        
        # Weight/Gravity (down arrow) - using primary color
        w_color = theme["primary"]
        w_start_y = box_y + box_h
        draw.line([(box_x + box_w // 2, w_start_y), 
                  (box_x + box_w // 2, w_start_y + normal_length)],
                  fill=w_color, width=3)
        _draw_arrow_head(draw, box_x + box_w // 2, w_start_y + normal_length, box_x + box_w // 2, w_start_y + normal_length + 12, w_color, 12)
        draw.text((box_x + box_w // 2 + 10, w_start_y + normal_length - 5), "W = mg", 
                 fill=w_color, font=font_info)
        
        # Acceleration indicator (animated) - using accent color
        accel_x = box_x + box_w + 180
        accel_y = arrow_y
        accel_phase = (t * 3) % 1
        for i in range(3):
            offset = int(20 * accel_phase) + i * 25
            alpha = int(200 * (1 - accel_phase))
            a_color = theme["accent"]
            draw.line([(accel_x + offset, accel_y - 15), (accel_x + offset, accel_y + 15)],
                     fill=a_color, width=2)
        draw.text((accel_x, accel_y + 25), "a = 3 m/s²", fill=theme["accent"], font=font_label)
        
        # Newton's Second Law - using theme colors
        if t > duration * 0.3:
            law_y = 70
            draw.text((80, law_y), "Newton's Second Law:", fill=theme["text"], font=font_label)
            draw.text((300, law_y), "F_net = ma", fill=theme["highlight"], font=font_label)
            
            if t > duration * 0.5:
                draw.text((80, law_y + 30), "F_net = F - f = 20 - 5 = 15 N", 
                         fill=theme["secondary"], font=font_info)
                draw.text((80, law_y + 55), "a = F_net / m = 15 / 5 = 3 m/s²", 
                         fill=theme["secondary"], font=font_info)
        
        # Speed indicator
        velocity = acceleration * t  # v = at (starting from rest)
        speed_text = f"v = {velocity:.1f} m/s"
        draw.text((WIDTH - 180, ground_y + 20), speed_text, fill=(180, 220, 255), font=font_label)
        
        # Motion lines behind box
        for i in range(5):
            line_x = box_x - 20 - i * 15
            if line_x > 100:
                alpha = 150 - i * 25
                line_y = arrow_y
                draw.line([(line_x, line_y - 10), (line_x, line_y + 10)],
                         fill=(100, 150, 200), width=2)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)

# ============================================================
# ORGANIC CHEMISTRY ANIMATION (CHEMISTRY DOMAIN)
# ============================================================

def create_organic_chemistry_clip(duration: float = 5.0,
                                  title: str = "Organic Chemistry") -> VideoClip:
    """
    Create animated organic chemistry visualization.
    Shows carbon chains, functional groups, and molecular structures.
    Uses CHEMISTRY visual grammar: CPK colors, hexagonal patterns, molecular bonds.
    """
    theme = _get_theme("chemistry")
    
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(14)
    font_small = _load_font(12)
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # CHEMISTRY themed background with hexagonal molecular pattern
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "chemistry")
        
        # CHEMISTRY styled title with orbital decoration
        _draw_domain_title(draw, title, theme, "chemistry", font_title)
        
        # ============================================
        # Draw a carbon chain (backbone of organic molecule)
        # ============================================
        
        # Ethanol molecule: CH3-CH2-OH
        chain_center_x = WIDTH // 2
        chain_center_y = HEIGHT // 2 + 20
        
        # Carbon atom positions
        carbon_spacing = 100
        
        # Animated building of molecule
        build_progress = min(1.0, t / (duration * 0.6))
        
        # Carbon 1 (CH3)
        c1_x = chain_center_x - 120
        c1_y = chain_center_y
        
        # Carbon 2 (CH2)
        c2_x = chain_center_x + 20
        c2_y = chain_center_y
        
        # Oxygen (OH)
        o_x = chain_center_x + 160
        o_y = chain_center_y
        
        # Draw atoms with animation
        atom_radius = 25
        
        # Helper to draw atom with label (CPK colors from theme)
        def draw_atom(x, y, label, color, appear_time):
            if t < appear_time:
                return
            
            # Pulse effect
            pulse = 1 + 0.05 * math.sin(t * 3 + x * 0.01)
            r = int(atom_radius * pulse)
            
            # Glow effect (chemistry molecular glow)
            for glow_r in range(r + 10, r, -2):
                glow_alpha = int(50 * (1 - (glow_r - r) / 10))
                glow_color = tuple(max(0, min(255, c - 100 + glow_alpha)) for c in color)
                draw.ellipse([x - glow_r, y - glow_r, x + glow_r, y + glow_r],
                            fill=glow_color)
            
            # Main atom (CPK style)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color, 
                        outline=theme["highlight"], width=2)
            
            # Label
            label_x = x - len(label) * 5
            draw.text((label_x, y - 8), label, fill=theme["text"], font=font_label)
        
        # Draw Carbon 1 (grey - CPK convention)
        draw_atom(c1_x, c1_y, "C", theme["carbon"], 0)
        
        # Draw bond between C1 and C2 (covalent bond style)
        if t > duration * 0.15:
            bond_progress = min(1.0, (t - duration * 0.15) / (duration * 0.15))
            bond_end_x = c1_x + (c2_x - c1_x - 2 * atom_radius) * bond_progress + atom_radius
            draw.line([(c1_x + atom_radius, c1_y), (bond_end_x, c2_y)], 
                     fill=theme["text"], width=4)
        
        # Draw Carbon 2
        if t > duration * 0.25:
            draw_atom(c2_x, c2_y, "C", theme["carbon"], duration * 0.25)
        
        # Draw bond between C2 and O
        if t > duration * 0.35:
            bond_progress = min(1.0, (t - duration * 0.35) / (duration * 0.15))
            bond_end_x = c2_x + (o_x - c2_x - 2 * atom_radius) * bond_progress + atom_radius
            draw.line([(c2_x + atom_radius, c2_y), (bond_end_x, o_y)], 
                     fill=theme["text"], width=4)
        
        # Draw Oxygen (red - CPK convention)
        if t > duration * 0.45:
            draw_atom(o_x, o_y, "O", theme["oxygen"], duration * 0.45)
        
        # Draw hydrogen atoms on C1 (CH3) - white/light blue CPK
        if t > duration * 0.2:
            h_radius = 15
            h_color = theme["hydrogen"]
            
            # H atoms around C1
            h_positions_c1 = [
                (c1_x - 50, c1_y - 40),
                (c1_x - 50, c1_y + 40),
                (c1_x - 60, c1_y),
            ]
            for i, (hx, hy) in enumerate(h_positions_c1):
                if t > duration * (0.2 + i * 0.02):
                    # Bond
                    draw.line([(c1_x - atom_radius, c1_y), (hx + h_radius, hy)], 
                             fill=theme["grid"], width=2)
                    # H atom
                    draw.ellipse([hx - h_radius, hy - h_radius, hx + h_radius, hy + h_radius],
                                fill=h_color, outline=theme["primary"], width=1)
                    draw.text((hx - 4, hy - 6), "H", fill=theme["carbon"], font=font_info)
        
        # Draw hydrogen atoms on C2 (CH2)
        if t > duration * 0.35:
            h_positions_c2 = [
                (c2_x, c2_y - 55),
                (c2_x, c2_y + 55),
            ]
            for i, (hx, hy) in enumerate(h_positions_c2):
                if t > duration * (0.35 + i * 0.02):
                    # Bond
                    if hy < c2_y:
                        draw.line([(c2_x, c2_y - atom_radius), (hx, hy + h_radius)],
                                 fill=(150, 150, 180), width=2)
                    else:
                        draw.line([(c2_x, c2_y + atom_radius), (hx, hy - h_radius)],
                                 fill=(150, 150, 180), width=2)
                    # H atom
                    draw.ellipse([hx - h_radius, hy - h_radius, hx + h_radius, hy + h_radius],
                                fill=h_color, outline=(255, 255, 255), width=1)
                    draw.text((hx - 4, hy - 6), "H", fill=(50, 50, 100), font=font_info)
        
        # Draw hydrogen on O (OH group)
        if t > duration * 0.55:
            hx, hy = o_x + 50, o_y - 40
            # Bond
            draw.line([(o_x + atom_radius - 10, o_y - 15), (hx - h_radius + 5, hy + h_radius - 5)],
                     fill=(150, 150, 180), width=2)
            # H atom
            draw.ellipse([hx - h_radius, hy - h_radius, hx + h_radius, hy + h_radius],
                        fill=h_color, outline=(255, 255, 255), width=1)
            draw.text((hx - 4, hy - 6), "H", fill=(50, 50, 100), font=font_info)
        
        # Molecule name and formula
        if t > duration * 0.65:
            draw.text((WIDTH // 2 - 80, HEIGHT - 100), "Ethanol", fill=(180, 255, 180), font=font_label)
            draw.text((WIDTH // 2 - 90, HEIGHT - 75), "C₂H₅OH", fill=(150, 200, 255), font=font_label)
        
        # Functional group highlight
        if t > duration * 0.75:
            # Highlight OH group with dashed circle
            highlight_x = o_x + 20
            highlight_y = o_y - 20
            highlight_r = 60
            
            # Pulsing highlight
            pulse = 0.8 + 0.2 * math.sin(t * 4)
            draw.arc([highlight_x - highlight_r, highlight_y - highlight_r,
                     highlight_x + highlight_r, highlight_y + highlight_r],
                    0, 360, fill=(100, 255, 150), width=2)
            
            draw.text((o_x - 10, o_y + 50), "Hydroxyl", fill=(100, 255, 150), font=font_info)
            draw.text((o_x - 5, o_y + 68), "(-OH)", fill=(100, 255, 150), font=font_info)
        
        # Legend
        legend_x = 50
        legend_y = 120
        if t > duration * 0.3:
            draw.text((legend_x, legend_y), "Legend:", fill=(200, 220, 240), font=font_info)
            # Carbon
            draw.ellipse([legend_x, legend_y + 20, legend_x + 16, legend_y + 36],
                        fill=(80, 80, 80), outline=(255, 255, 255), width=1)
            draw.text((legend_x + 25, legend_y + 22), "Carbon (C)", fill=(180, 180, 180), font=font_small)
            # Hydrogen
            draw.ellipse([legend_x, legend_y + 45, legend_x + 12, legend_y + 57],
                        fill=(200, 200, 255), outline=(255, 255, 255), width=1)
            draw.text((legend_x + 25, legend_y + 45), "Hydrogen (H)", fill=(180, 180, 180), font=font_small)
            # Oxygen
            draw.ellipse([legend_x, legend_y + 68, legend_x + 16, legend_y + 84],
                        fill=(255, 80, 80), outline=(255, 255, 255), width=1)
            draw.text((legend_x + 25, legend_y + 68), "Oxygen (O)", fill=(180, 180, 180), font=font_small)
        
        # Bond type info
        if t > duration * 0.85:
            bond_info_x = WIDTH - 180
            bond_info_y = 120
            draw.text((bond_info_x, bond_info_y), "Bond Types:", fill=(200, 220, 240), font=font_info)
            draw.line([(bond_info_x, bond_info_y + 25), (bond_info_x + 30, bond_info_y + 25)],
                     fill=(200, 200, 200), width=3)
            draw.text((bond_info_x + 40, bond_info_y + 20), "Single", fill=(180, 180, 180), font=font_small)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# ORGANIC REACTION ANIMATION
# ============================================================

def create_organic_reaction_clip(duration: float = 5.0,
                                 title: str = "Organic Reaction") -> VideoClip:
    """
    Create animated organic reaction visualization.
    Shows a simple addition/substitution reaction.
    Uses CHEMISTRY visual grammar: CPK colors, molecular bonds.
    """
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(14)
    font_small = _load_font(12)
    
    # CHEMISTRY domain theme
    theme = _get_theme("chemistry")
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # CHEMISTRY themed background with hexagonal pattern
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "chemistry")
        
        # CHEMISTRY styled title
        _draw_domain_title(draw, title, theme, "chemistry", font_title)
        
        # ============================================
        # Show combustion of methane: CH4 + 2O2 → CO2 + 2H2O
        # ============================================
        
        center_y = HEIGHT // 2 + 10
        
        # Phase 1: Show reactants
        # Phase 2: Show arrow and transition
        # Phase 3: Show products
        
        phase = t / duration
        
        # Methane molecule (left side)
        ch4_x = 150
        ch4_y = center_y - 30
        
        # Draw CH4 using CPK colors from theme
        c_radius = 20
        h_radius = 12
        
        # CPK colors
        carbon_color = theme["carbon"]
        hydrogen_color = theme["hydrogen"]
        oxygen_color = theme["oxygen"]
        
        if phase < 0.7 or phase > 0.85:
            alpha = 1.0 if phase < 0.5 else max(0, 1 - (phase - 0.5) * 3) if phase < 0.7 else min(1, (phase - 0.85) * 5)
            
            if alpha > 0.1:
                # Central carbon - using CPK color
                c_color = tuple(int(c * alpha) for c in carbon_color)
                draw.ellipse([ch4_x - c_radius, ch4_y - c_radius, ch4_x + c_radius, ch4_y + c_radius],
                            fill=c_color, outline=theme["text"], width=1)
                if alpha > 0.5:
                    draw.text((ch4_x - 5, ch4_y - 7), "C", fill=theme["text"], font=font_info)
                
                # Hydrogen atoms - using CPK color
                h_positions = [
                    (ch4_x - 45, ch4_y - 25),
                    (ch4_x + 45, ch4_y - 25),
                    (ch4_x - 45, ch4_y + 25),
                    (ch4_x + 45, ch4_y + 25),
                ]
                h_color = tuple(int(c * alpha) for c in hydrogen_color)
                for hx, hy in h_positions:
                    # Bond using theme grid color
                    draw.line([(ch4_x, ch4_y), (hx, hy)], fill=theme["grid"], width=2)
                    draw.ellipse([hx - h_radius, hy - h_radius, hx + h_radius, hy + h_radius],
                                fill=h_color, outline=theme["text"], width=1)
                    if alpha > 0.5:
                        draw.text((hx - 4, hy - 5), "H", fill=(50, 50, 100), font=font_small)
                
                if alpha > 0.5:
                    draw.text((ch4_x - 20, ch4_y + 60), "CH₄", fill=theme["text"], font=font_label)
        
        # Plus sign - using accent color
        if phase < 0.6:
            draw.text((220, center_y - 15), "+", fill=theme["accent"], font=font_title)
        
        # Oxygen molecules (O2) - using CPK oxygen color
        o2_x = 300
        o2_y = center_y
        
        if phase < 0.6:
            o_radius = 18
            # Two oxygen atoms with double bond
            o1_x = o2_x - 25
            o2_x_pos = o2_x + 25
            
            draw.ellipse([o1_x - o_radius, o2_y - o_radius, o1_x + o_radius, o2_y + o_radius],
                        fill=oxygen_color, outline=theme["text"], width=1)
            draw.text((o1_x - 5, o2_y - 6), "O", fill=theme["text"], font=font_info)
            
            # Double bond using secondary color
            draw.line([(o1_x + o_radius, o2_y - 5), (o2_x_pos - o_radius, o2_y - 5)],
                     fill=theme["secondary"], width=3)
            draw.line([(o1_x + o_radius, o2_y + 5), (o2_x_pos - o_radius, o2_y + 5)],
                     fill=theme["secondary"], width=3)
            
            draw.ellipse([o2_x_pos - o_radius, o2_y - o_radius, o2_x_pos + o_radius, o2_y + o_radius],
                        fill=oxygen_color, outline=theme["text"], width=1)
            draw.text((o2_x_pos - 5, o2_y - 6), "O", fill=theme["text"], font=font_info)
            
            draw.text((o2_x - 35, center_y + 50), "2O₂", fill=theme["text"], font=font_label)
        
        # Reaction arrow (animated) - using highlight color
        if phase > 0.25 and phase < 0.85:
            arrow_x = 400
            arrow_progress = min(1.0, (phase - 0.25) * 3)
            arrow_length = int(100 * arrow_progress)
            
            # Arrow body
            draw.line([(arrow_x, center_y), (arrow_x + arrow_length, center_y)],
                     fill=theme["highlight"], width=4)
            
            # Arrow head
            if arrow_progress > 0.8:
                draw.polygon([(arrow_x + arrow_length + 15, center_y),
                             (arrow_x + arrow_length, center_y - 10),
                             (arrow_x + arrow_length, center_y + 10)],
                            fill=theme["highlight"])
            
            # Energy/heat symbol - using accent color
            if phase > 0.45:
                draw.text((arrow_x + 30, center_y - 35), "heat", fill=theme["accent"], font=font_info)
                # Wavy lines for heat
                for i in range(3):
                    wave_x = arrow_x + 25 + i * 25
                    for j in range(3):
                        wy = center_y - 55 - j * 8
                        draw.arc([wave_x, wy, wave_x + 15, wy + 10],
                                0, 180, fill=theme["highlight"], width=1)
        
        # Products (appear after reaction)
        if phase > 0.55:
            product_alpha = min(1.0, (phase - 0.55) * 3)
            
            # CO2 molecule
            co2_x = 600
            co2_y = center_y - 50
            
            o_radius = 16
            c_radius = 18
            
            # Left O - using CPK oxygen color
            o1_x = co2_x - 50
            draw.ellipse([o1_x - o_radius, co2_y - o_radius, o1_x + o_radius, co2_y + o_radius],
                        fill=oxygen_color, outline=theme["text"], width=1)
            draw.text((o1_x - 5, co2_y - 6), "O", fill=theme["text"], font=font_info)
            
            # Double bond using secondary color
            draw.line([(o1_x + o_radius, co2_y - 4), (co2_x - c_radius, co2_y - 4)],
                     fill=theme["secondary"], width=2)
            draw.line([(o1_x + o_radius, co2_y + 4), (co2_x - c_radius, co2_y + 4)],
                     fill=theme["secondary"], width=2)
            
            # Central C - using CPK carbon color
            draw.ellipse([co2_x - c_radius, co2_y - c_radius, co2_x + c_radius, co2_y + c_radius],
                        fill=carbon_color, outline=theme["text"], width=1)
            draw.text((co2_x - 5, co2_y - 7), "C", fill=theme["text"], font=font_info)
            
            # Double bond
            o2_x_pos = co2_x + 50
            draw.line([(co2_x + c_radius, co2_y - 4), (o2_x_pos - o_radius, co2_y - 4)],
                     fill=theme["secondary"], width=2)
            draw.line([(co2_x + c_radius, co2_y + 4), (o2_x_pos - o_radius, co2_y + 4)],
                     fill=theme["secondary"], width=2)
            
            # Right O - using CPK oxygen color
            draw.ellipse([o2_x_pos - o_radius, co2_y - o_radius, o2_x_pos + o_radius, co2_y + o_radius],
                        fill=oxygen_color, outline=theme["text"], width=1)
            draw.text((o2_x_pos - 5, co2_y - 6), "O", fill=theme["text"], font=font_info)
            
            draw.text((co2_x - 20, co2_y + 35), "CO₂", fill=theme["text"], font=font_label)
            
            # Plus sign - using accent color
            draw.text((co2_x + 80, center_y - 15), "+", fill=theme["accent"], font=font_label)
            
            # H2O molecule
            h2o_x = 750
            h2o_y = center_y + 30
            
            # Oxygen - using CPK oxygen color
            draw.ellipse([h2o_x - o_radius, h2o_y - o_radius, h2o_x + o_radius, h2o_y + o_radius],
                        fill=oxygen_color, outline=theme["text"], width=1)
            draw.text((h2o_x - 5, h2o_y - 6), "O", fill=theme["text"], font=font_info)
            
            # H atoms (bent shape) - using CPK hydrogen color
            h1_x, h1_y = h2o_x - 35, h2o_y - 30
            h2_pos_x, h2_pos_y = h2o_x + 35, h2o_y - 30
            
            h_radius = 10
            draw.line([(h2o_x, h2o_y), (h1_x, h1_y)], fill=theme["grid"], width=2)
            draw.ellipse([h1_x - h_radius, h1_y - h_radius, h1_x + h_radius, h1_y + h_radius],
                        fill=hydrogen_color, outline=theme["text"], width=1)
            draw.text((h1_x - 3, h1_y - 5), "H", fill=(50, 50, 100), font=font_small)
            
            draw.line([(h2o_x, h2o_y), (h2_pos_x, h2_pos_y)], fill=theme["grid"], width=2)
            draw.ellipse([h2_pos_x - h_radius, h2_pos_y - h_radius, h2_pos_x + h_radius, h2_pos_y + h_radius],
                        fill=hydrogen_color, outline=theme["text"], width=1)
            draw.text((h2_pos_x - 3, h2_pos_y - 5), "H", fill=(50, 50, 100), font=font_small)
            
            draw.text((h2o_x - 25, h2o_y + 35), "2H₂O", fill=theme["text"], font=font_label)
        
        # Equation at bottom - using theme highlight color
        if phase > 0.8:
            eq_y = HEIGHT - 60
            draw.text((WIDTH // 2 - 200, eq_y), "CH₄ + 2O₂ → CO₂ + 2H₂O + Energy",
                     fill=theme["highlight"], font=font_label)
            draw.text((WIDTH // 2 - 100, eq_y + 25), "(Combustion of Methane)",
                     fill=theme["secondary"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# PHYSICAL CHEMISTRY (GAS LAWS) ANIMATION
# ============================================================

def create_gas_law_clip(duration: float = 5.0,
                        title: str = "Gas Laws") -> VideoClip:
    """
    Create animated gas law visualization (Boyle's/Charles's Law).
    Shows a piston compressing gas particles, demonstrating PV=nRT.
    Uses CHEMISTRY/PHYSICS visual grammar.
    """
    theme = _get_theme("chemistry")
    font_title = _load_font(28)
    font_label = _load_font(18)
    font_info = _load_font(16)
    
    # Particle system
    import random
    random.seed(42)
    
    class GasParticle:
        def __init__(self, x_range, y_range):
            self.x = random.uniform(*x_range)
            self.y = random.uniform(*y_range)
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-3, 3)
            self.radius = 4
            
        def update(self, x_min, x_max, y_min, y_max, speed_mult=1.0):
            self.x += self.vx * speed_mult
            self.y += self.vy * speed_mult
            
            # Bounce off walls
            if self.x < x_min + self.radius:
                self.x = x_min + self.radius
                self.vx *= -1
            elif self.x > x_max - self.radius:
                self.x = x_max - self.radius
                self.vx *= -1
                
            if self.y < y_min + self.radius:
                self.y = y_min + self.radius
                self.vy *= -1
            elif self.y > y_max - self.radius:
                self.y = y_max - self.radius
                self.vy *= -1

    # Initialize particles
    container_w = 300
    container_h_max = 300
    cx = WIDTH // 2
    cy = HEIGHT // 2 + 20
    
    particles = [GasParticle((cx - container_w//2 + 10, cx + container_w//2 - 10),
                             (cy - container_h_max//2 + 10, cy + container_h_max//2 - 10)) 
                 for _ in range(40)]
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "chemistry")
        _draw_domain_title(draw, title, theme, "chemistry", font_title)
        
        # Animation: Piston moves down (Compression)
        # Volume decreases, Pressure increases (particles move faster)
        compression = 0.5 + 0.3 * math.sin(t * 1.5) # Oscillates between 0.2 and 0.8
        current_h = container_h_max * compression
        
        # Container boundaries
        left = cx - container_w // 2
        right = cx + container_w // 2
        bottom = cy + container_h_max // 2
        top = bottom - current_h
        
        # Draw container
        draw.line([(left, bottom), (left, top - 50)], fill=theme["text"], width=3)
        draw.line([(right, bottom), (right, top - 50)], fill=theme["text"], width=3)
        draw.line([(left, bottom), (right, bottom)], fill=theme["text"], width=3)
        
        # Draw Piston
        piston_y = top
        draw.rectangle([left + 2, piston_y - 20, right - 2, piston_y], fill=theme["secondary"])
        draw.line([(cx, piston_y - 20), (cx, piston_y - 100)], fill=theme["text"], width=5)
        draw.rectangle([cx - 40, piston_y - 110, cx + 40, piston_y - 100], fill=theme["text"])
        
        # Update and draw particles
        # As volume decreases (compression < 1), speed increases
        speed_factor = 1.0 + (1.0 - compression) * 2.0
        
        for p in particles:
            p.update(left, right, top, bottom, speed_factor)
            draw.ellipse([p.x - p.radius, p.y - p.radius, p.x + p.radius, p.y + p.radius],
                        fill=theme["primary"])
        
        # Info / Equations
        info_x = WIDTH - 250
        draw.text((info_x, 150), "Ideal Gas Law", fill=theme["highlight"], font=font_label)
        draw.text((info_x, 180), "PV = nRT", fill=theme["text"], font=font_title)
        
        # Dynamic values
        vol_text = f"Volume: {compression*100:.0f}%"
        press_text = f"Pressure: {1/compression:.1f}x"
        draw.text((info_x, 240), vol_text, fill=theme["accent"], font=font_info)
        draw.text((info_x, 270), press_text, fill=theme["secondary"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# INORGANIC CHEMISTRY (CRYSTAL LATTICE) ANIMATION
# ============================================================

def create_crystal_lattice_clip(duration: float = 5.0,
                                title: str = "Crystal Lattice") -> VideoClip:
    """
    Create animated crystal lattice visualization.
    Shows a rotating 3D cubic unit cell.
    """
    theme = _get_theme("chemistry")
    font_title = _load_font(28)
    
    # Define a simple cube unit cell (8 corners)
    points = []
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-1, 1]:
                points.append((x, y, z))
                
    # Connections (edges of the cube)
    edges = [
        (0,1), (1,3), (3,2), (2,0), # Front face
        (4,5), (5,7), (7,6), (6,4), # Back face
        (0,4), (1,5), (2,6), (3,7)  # Connecting edges
    ]
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "chemistry")
        _draw_domain_title(draw, title, theme, "chemistry", font_title)
        
        # Rotation angles
        angle_x = t * 0.5
        angle_y = t * 0.8
        
        # Project 3D points to 2D
        scale = 100
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        projected = []
        for x, y, z in points:
            # Rotate Y
            rx = x * math.cos(angle_y) - z * math.sin(angle_y)
            rz = x * math.sin(angle_y) + z * math.cos(angle_y)
            # Rotate X
            ry = y * math.cos(angle_x) - rz * math.sin(angle_x)
            
            # Simple perspective projection
            proj_x = center_x + rx * scale
            proj_y = center_y + ry * scale
            projected.append((proj_x, proj_y))
            
        # Draw edges
        for i, j in edges:
            p1 = projected[i]
            p2 = projected[j]
            draw.line([p1, p2], fill=theme["grid"], width=2)
            
        # Draw atoms (sorted by Z-depth roughly approximated by index for simplicity, 
        # or just draw all since it's a wireframe style)
        for px, py in projected:
            r = 15
            # Draw atom with gradient/shading look
            draw.ellipse([px - r, py - r, px + r, py + r], fill=theme["secondary"], outline=theme["text"])
            # Highlight
            draw.ellipse([px - r + 5, py - r + 5, px - r + 12, py - r + 12], fill=(255, 255, 255, 100))
            
        draw.text((50, HEIGHT - 50), "Simple Cubic Unit Cell", fill=theme["text"], font=_load_font(18))
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================================
# MAGNETIC FIELD ANIMATION
# Visual: Field lines emanating from bar magnet, compass needle alignment
# Domain: PHYSICS - Uses navy gradients, measurement markers, vector elements
# ============================================================================

def create_magnetic_field_clip(duration: float = 5.0,
                               title: str = "Magnetic Field Lines") -> VideoClip:
    """
    Create animated magnetic field lines visualization.
    Shows field lines from N to S pole with compass needle animation.
    Uses PHYSICS visual grammar: dark navy, measurement markers, vector styling.
    """
    theme = _get_theme("physics")
    
    # Load fonts
    font_label = _load_font(16)
    font_info = _load_font(14)
    font_small = _load_font(12)
    
    def make_frame(t):
        img = Image.new('RGB', (WIDTH, HEIGHT), color=theme["bg_top"])
        draw = ImageDraw.Draw(img)
        
        # Draw physics-themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # Title with physics styling
        _draw_domain_title(draw, title, theme, "physics", font_label)
        
        # Bar magnet in center
        magnet_w, magnet_h = 180, 60
        magnet_x = WIDTH // 2 - magnet_w // 2
        magnet_y = HEIGHT // 2 - magnet_h // 2
        
        # North pole (red)
        n_color = (200, 60, 60)
        draw.rectangle([magnet_x, magnet_y, magnet_x + magnet_w // 2, magnet_y + magnet_h],
                      fill=n_color, outline=theme["text"], width=2)
        draw.text((magnet_x + magnet_w // 4 - 8, magnet_y + magnet_h // 2 - 10),
                 "N", fill=(255, 255, 255), font=font_label)
        
        # South pole (blue)
        s_color = (60, 60, 200)
        draw.rectangle([magnet_x + magnet_w // 2, magnet_y, 
                       magnet_x + magnet_w, magnet_y + magnet_h],
                      fill=s_color, outline=theme["text"], width=2)
        draw.text((magnet_x + 3 * magnet_w // 4 - 8, magnet_y + magnet_h // 2 - 10),
                 "S", fill=(255, 255, 255), font=font_label)
        
        # Animated field lines
        cx, cy = WIDTH // 2, HEIGHT // 2
        phase = t * 0.5  # Slow animation
        
        # Draw curved field lines from N to S (outside magnet)
        num_lines = 8
        for i in range(num_lines):
            angle_offset = (i - num_lines // 2) * 15 + 90  # Spread from -60 to +60 degrees
            
            # Animation: lines "flow" from N to S
            flow_phase = (t * 2 + i * 0.3) % 1.0
            
            # Start at N pole edge
            start_angle = math.radians(angle_offset)
            
            # Draw curved path using Bezier-like points
            points = []
            for j in range(20):
                progress = j / 19.0
                
                # Parametric curve from N to S pole (outside)
                # Start from left of magnet (N), arc outside, end at right (S)
                arc_height = 80 + abs(angle_offset - 90) * 2  # Higher arc for outer lines
                
                # X goes from N pole to S pole
                px = magnet_x - 20 + (magnet_w + 40) * progress
                
                # Y arcs up (for top lines) or down (for bottom lines)
                if angle_offset > 90:
                    # Top lines
                    py = cy - arc_height * math.sin(math.pi * progress)
                else:
                    # Bottom lines
                    py = cy + arc_height * math.sin(math.pi * progress)
                
                points.append((px, py))
            
            # Draw field line with animated glow
            glow_intensity = int(100 + 80 * math.sin(phase * 4 + i))
            line_color = (glow_intensity, glow_intensity + 50, 255)
            
            if len(points) > 1:
                draw.line(points, fill=line_color, width=2)
                
                # Draw arrow at midpoint showing direction
                mid_idx = len(points) // 2
                if mid_idx < len(points) - 1:
                    mx, my = points[mid_idx]
                    mx2, my2 = points[mid_idx + 1]
                    _draw_arrow_head(draw, mx - 10, my, mx, my, theme["primary"], 8)
        
        # Draw field lines inside magnet (straight, N to S)
        for i in range(3):
            y_off = (i - 1) * 15
            ly = cy + y_off
            draw.line([(magnet_x + magnet_w - 10, ly), (magnet_x + 10, ly)],
                     fill=theme["primary"], width=2)
            # Arrow pointing from S to N inside
            _draw_arrow_head(draw, magnet_x + 30, ly, magnet_x + 10, ly, theme["primary"], 6)
        
        # Animated compass needles around magnet
        compass_positions = [
            (magnet_x - 80, cy - 80),
            (magnet_x - 80, cy + 80),
            (magnet_x + magnet_w + 80, cy - 80),
            (magnet_x + magnet_w + 80, cy + 80),
        ]
        
        for px, py in compass_positions:
            # Calculate direction to center
            dx, dy = cx - px, cy - py
            base_angle = math.atan2(dy, dx)
            
            # Add wobble animation
            wobble = 0.1 * math.sin(t * 3 + px * 0.01)
            angle = base_angle + wobble
            
            # Draw compass circle
            r = 20
            draw.ellipse([px - r, py - r, px + r, py + r],
                        outline=theme["secondary"], width=2)
            
            # Draw needle
            needle_len = 15
            nx1 = px + needle_len * math.cos(angle)
            ny1 = py + needle_len * math.sin(angle)
            nx2 = px - needle_len * math.cos(angle)
            ny2 = py - needle_len * math.sin(angle)
            
            # Red end points to N
            draw.line([(px, py), (nx1, ny1)], fill=(200, 60, 60), width=3)
            draw.line([(px, py), (nx2, ny2)], fill=(60, 60, 200), width=3)
        
        # Info text
        if t > duration * 0.3:
            info_y = HEIGHT - 80
            draw.text((60, info_y), "• Field lines: N → S (outside)", 
                     fill=theme["text"], font=font_info)
            draw.text((60, info_y + 25), "• Field lines: S → N (inside)", 
                     fill=theme["text"], font=font_info)
            draw.text((WIDTH - 300, info_y), "• Lines never cross",
                     fill=theme["highlight"], font=font_info)
            draw.text((WIDTH - 300, info_y + 25), "• Closer lines = stronger field",
                     fill=theme["highlight"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================================
# ELECTROMAGNETIC INDUCTION ANIMATION
# Visual: Coil with moving magnet, induced current, Faraday's law
# Domain: PHYSICS - Uses measurement markers, vector elements
# ============================================================================

def create_electromagnetic_clip(duration: float = 5.0,
                                 title: str = "Electromagnetic Induction") -> VideoClip:
    """
    Create animated electromagnetic induction visualization.
    Shows magnet moving through coil, inducing current (Faraday's Law).
    Uses PHYSICS visual grammar.
    """
    theme = _get_theme("physics")
    
    # Load fonts
    font_label = _load_font(16)
    font_info = _load_font(14)
    
    def make_frame(t):
        img = Image.new('RGB', (WIDTH, HEIGHT), color=theme["bg_top"])
        draw = ImageDraw.Draw(img)
        
        # Draw physics-themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # Title with physics styling
        _draw_domain_title(draw, title, theme, "physics", font_label)
        
        # Coil in center (solenoid representation)
        coil_x = WIDTH // 2 - 60
        coil_y = HEIGHT // 2 - 40
        coil_w, coil_h = 120, 80
        
        # Draw coil loops
        num_loops = 8
        for i in range(num_loops):
            lx = coil_x + i * (coil_w // num_loops)
            # Ellipse for each loop
            draw.ellipse([lx - 5, coil_y, lx + 20, coil_y + coil_h],
                        outline=theme["accent"], width=2)
        
        # Coil wire connections
        draw.line([(coil_x - 30, coil_y + coil_h // 2), (coil_x, coil_y + coil_h // 2)],
                 fill=theme["accent"], width=3)
        draw.line([(coil_x + coil_w, coil_y + coil_h // 2), 
                  (coil_x + coil_w + 30, coil_y + coil_h // 2)],
                 fill=theme["accent"], width=3)
        
        # Animated bar magnet moving through coil
        cycle_duration = duration / 2
        cycle_phase = (t % cycle_duration) / cycle_duration
        
        # Magnet oscillates left-right through coil
        magnet_w, magnet_h = 100, 35
        magnet_center_x = WIDTH // 2
        magnet_amplitude = 120
        
        # Sinusoidal motion
        magnet_offset = magnet_amplitude * math.sin(cycle_phase * 2 * math.pi)
        magnet_x = magnet_center_x + magnet_offset - magnet_w // 2
        magnet_y = coil_y + coil_h // 2 - magnet_h // 2
        
        # Draw magnet
        # North pole
        draw.rectangle([magnet_x, magnet_y, magnet_x + magnet_w // 2, magnet_y + magnet_h],
                      fill=(200, 60, 60), outline=(255, 255, 255), width=1)
        draw.text((magnet_x + magnet_w // 4 - 5, magnet_y + magnet_h // 2 - 8),
                 "N", fill=(255, 255, 255), font=font_info)
        
        # South pole
        draw.rectangle([magnet_x + magnet_w // 2, magnet_y, 
                       magnet_x + magnet_w, magnet_y + magnet_h],
                      fill=(60, 60, 200), outline=(255, 255, 255), width=1)
        draw.text((magnet_x + 3 * magnet_w // 4 - 5, magnet_y + magnet_h // 2 - 8),
                 "S", fill=(255, 255, 255), font=font_info)
        
        # Velocity arrow on magnet
        velocity = magnet_amplitude * 2 * math.pi / cycle_duration * math.cos(cycle_phase * 2 * math.pi)
        if abs(velocity) > 10:
            arrow_y = magnet_y - 20
            arrow_x = magnet_x + magnet_w // 2
            arrow_dir = 1 if velocity > 0 else -1
            arrow_len = min(40, abs(velocity) * 0.3)
            
            draw.line([(arrow_x, arrow_y), (arrow_x + arrow_dir * arrow_len, arrow_y)],
                     fill=theme["secondary"], width=2)
            _draw_arrow_head(draw, arrow_x + arrow_dir * arrow_len - arrow_dir * 5, arrow_y,
                           arrow_x + arrow_dir * arrow_len, arrow_y, theme["secondary"], 8)
            draw.text((arrow_x - 5, arrow_y - 18), "v", fill=theme["secondary"], font=font_info)
        
        # Induced current visualization
        # Current magnitude proportional to rate of flux change (velocity)
        current_magnitude = abs(velocity) / (magnet_amplitude * 2 * math.pi / cycle_duration)
        
        if current_magnitude > 0.1:
            # Draw current flow in wires
            current_color = (
                int(100 + 155 * current_magnitude),
                int(200 * current_magnitude),
                int(100 + 100 * current_magnitude)
            )
            
            # Galvanometer/ammeter
            meter_x, meter_y = coil_x - 80, coil_y + coil_h // 2 - 25
            draw.ellipse([meter_x, meter_y, meter_x + 50, meter_y + 50],
                        outline=theme["text"], width=2)
            draw.text((meter_x + 18, meter_y + 15), "G", fill=theme["text"], font=font_info)
            
            # Needle deflection based on current direction
            needle_angle = math.pi / 2 - velocity / abs(velocity + 0.001) * current_magnitude * 0.8
            needle_cx, needle_cy = meter_x + 25, meter_y + 25
            needle_len = 18
            needle_ex = needle_cx + needle_len * math.cos(needle_angle)
            needle_ey = needle_cy - needle_len * math.sin(needle_angle)
            draw.line([(needle_cx, needle_cy), (needle_ex, needle_ey)],
                     fill=current_color, width=2)
            
            # Current direction indicators on wires
            wire_y = coil_y + coil_h // 2
            if velocity > 0:
                draw.text((coil_x - 60, wire_y + 10), "→", fill=current_color, font=font_label)
                draw.text((coil_x + coil_w + 35, wire_y + 10), "→", fill=current_color, font=font_label)
            else:
                draw.text((coil_x - 60, wire_y + 10), "←", fill=current_color, font=font_label)
                draw.text((coil_x + coil_w + 35, wire_y + 10), "←", fill=current_color, font=font_label)
        
        # Faraday's law equation
        if t > duration * 0.2:
            eq_y = HEIGHT - 80
            draw.text((WIDTH // 2 - 150, eq_y), "ε = -dΦ/dt", 
                     fill=theme["highlight"], font=font_label)
            draw.text((WIDTH // 2 - 150, eq_y + 25), "(Faraday's Law of Induction)",
                     fill=theme["secondary"], font=font_info)
        
        # Labels
        draw.text((coil_x + 20, coil_y - 30), "Coil", fill=theme["text"], font=font_info)
        draw.text((magnet_x + 20, magnet_y + magnet_h + 10), "Magnet", fill=theme["text"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================================
# GRAVITY / GRAVITATIONAL FIELD ANIMATION
# Visual: Objects falling, gravitational field lines, orbital motion
# Domain: PHYSICS - Uses vector elements, measurement markers
# ============================================================================

def create_gravity_clip(duration: float = 5.0,
                        title: str = "Gravitational Force") -> VideoClip:
    """
    Create animated gravity/gravitational field visualization.
    Shows free fall, gravitational field, and orbital concepts.
    Uses PHYSICS visual grammar.
    """
    theme = _get_theme("physics")
    
    # Pre-generate falling objects
    class FallingObject:
        def __init__(self, x, start_y, start_time, size, color):
            self.x = x
            self.start_y = start_y
            self.start_time = start_time
            self.size = size
            self.color = color
            self.g = 150  # pixels/s^2 (scaled for visualization)
        
        def get_position(self, t):
            if t < self.start_time:
                return self.x, self.start_y
            dt = t - self.start_time
            y = self.start_y + 0.5 * self.g * dt * dt
            return self.x, min(y, HEIGHT - 80)  # Ground at HEIGHT - 80
    
    objects = [
        FallingObject(150, 150, 0.0, 15, theme["primary"]),
        FallingObject(250, 130, 0.5, 20, theme["accent"]),
        FallingObject(350, 160, 1.0, 12, theme["highlight"]),
    ]
    
    # Load fonts
    font_label = _load_font(16)
    font_info = _load_font(14)
    font_small = _load_font(12)
    
    def make_frame(t):
        img = Image.new('RGB', (WIDTH, HEIGHT), color=theme["bg_top"])
        draw = ImageDraw.Draw(img)
        
        # Draw physics-themed background
        _draw_domain_background(draw, (WIDTH, HEIGHT), theme, "physics")
        
        # Title with physics styling
        _draw_domain_title(draw, title, theme, "physics", font_label)
        
        # Ground line
        ground_y = HEIGHT - 80
        draw.line([(50, ground_y), (450, ground_y)], fill=theme["secondary"], width=3)
        draw.text((50, ground_y + 10), "Ground", fill=theme["secondary"], font=font_info)
        
        # Draw falling objects with velocity vectors
        for obj in objects:
            x, y = obj.get_position(t)
            
            # Draw object (circle)
            draw.ellipse([x - obj.size, y - obj.size, x + obj.size, y + obj.size],
                        fill=obj.color, outline=theme["text"], width=1)
            
            # Velocity vector (v = gt)
            if t > obj.start_time and y < ground_y - 5:
                dt = t - obj.start_time
                v = obj.g * dt
                v_scaled = min(v * 0.3, 60)  # Scale for display
                
                # Draw velocity arrow pointing down
                arrow_end_y = y + v_scaled
                draw.line([(x + obj.size + 5, y), (x + obj.size + 5, arrow_end_y)],
                         fill=theme["highlight"], width=2)
                _draw_arrow_head(draw, x + obj.size + 5, arrow_end_y - 5,
                               x + obj.size + 5, arrow_end_y, theme["highlight"], 6)
                draw.text((x + obj.size + 10, y + v_scaled // 2 - 8), "v",
                         fill=theme["highlight"], font=font_small)
            
            # Weight vector (constant)
            if y < ground_y - 5:
                w_len = 30
                draw.line([(x, y + obj.size), (x, y + obj.size + w_len)],
                         fill=theme["primary"], width=2)
                _draw_arrow_head(draw, x, y + obj.size + w_len - 5,
                               x, y + obj.size + w_len, theme["primary"], 6)
                draw.text((x - 20, y + obj.size + w_len // 2), "W=mg",
                         fill=theme["primary"], font=font_small)
        
        # Right side: Gravitational field visualization
        planet_x, planet_y = WIDTH - 200, HEIGHT // 2
        planet_r = 50
        
        # Draw planet
        draw.ellipse([planet_x - planet_r, planet_y - planet_r,
                     planet_x + planet_r, planet_y + planet_r],
                    fill=(80, 120, 180), outline=theme["text"], width=2)
        draw.text((planet_x - 12, planet_y - 8), "M", fill=(255, 255, 255), font=font_info)
        
        # Gravitational field lines (pointing inward)
        num_field_lines = 12
        for i in range(num_field_lines):
            angle = i * 2 * math.pi / num_field_lines + t * 0.2
            
            # Field line from outside pointing to center
            outer_r = planet_r + 100
            inner_r = planet_r + 10
            
            ox = planet_x + outer_r * math.cos(angle)
            oy = planet_y + outer_r * math.sin(angle)
            ix = planet_x + inner_r * math.cos(angle)
            iy = planet_y + inner_r * math.sin(angle)
            
            # Animated segments along field line
            num_segments = 5
            for j in range(num_segments):
                seg_phase = ((t * 2 + j * 0.2) % 1.0)
                seg_r = outer_r - (outer_r - inner_r) * seg_phase
                
                sx = planet_x + seg_r * math.cos(angle)
                sy = planet_y + seg_r * math.sin(angle)
                
                seg_size = 3
                alpha = int(200 * (1 - seg_phase))
                seg_color = (alpha, alpha, int(255 * (1 - seg_phase * 0.5)))
                
                draw.ellipse([sx - seg_size, sy - seg_size, sx + seg_size, sy + seg_size],
                            fill=seg_color)
        
        # Small orbiting object
        orbit_r = planet_r + 70
        orbit_angle = t * 1.5
        orb_x = planet_x + orbit_r * math.cos(orbit_angle)
        orb_y = planet_y + orbit_r * math.sin(orbit_angle)
        
        draw.ellipse([orb_x - 8, orb_y - 8, orb_x + 8, orb_y + 8],
                    fill=theme["accent"], outline=theme["text"], width=1)
        
        # Draw orbit path (dashed)
        for i in range(24):
            a1 = i * math.pi / 12
            a2 = (i + 0.5) * math.pi / 12
            x1 = planet_x + orbit_r * math.cos(a1)
            y1 = planet_y + orbit_r * math.sin(a1)
            x2 = planet_x + orbit_r * math.cos(a2)
            y2 = planet_y + orbit_r * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=theme["grid"], width=1)
        
        # Gravitational force on orbiting object
        grav_len = 25
        grav_ex = orb_x - grav_len * math.cos(orbit_angle)
        grav_ey = orb_y - grav_len * math.sin(orbit_angle)
        draw.line([(orb_x, orb_y), (grav_ex, grav_ey)], fill=theme["highlight"], width=2)
        _draw_arrow_head(draw, orb_x - (grav_len - 5) * math.cos(orbit_angle),
                        orb_y - (grav_len - 5) * math.sin(orbit_angle),
                        grav_ex, grav_ey, theme["highlight"], 6)
        
        # Equations
        if t > duration * 0.3:
            eq_y = HEIGHT - 70
            draw.text((500, eq_y), "F = Gm₁m₂/r²", fill=theme["highlight"], font=font_info)
            draw.text((500, eq_y + 20), "g = 9.8 m/s²", fill=theme["secondary"], font=font_info)
            
            draw.text((60, eq_y + 40), "v = gt, s = ½gt²", fill=theme["text"], font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)
