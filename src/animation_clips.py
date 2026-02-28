# src/animation_clips.py

"""
Topic-based animation clip generators.
Creates MoviePy VideoClip objects with frame-by-frame animations for educational topics.
This is an ADDITIVE module - does not modify existing rendering pipeline.
"""

import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip
from typing import Optional, Tuple, List

# Video dimensions
WIDTH = 960
HEIGHT = 540


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


# ============================================================
# PROJECTILE MOTION ANIMATION
# ============================================================

def create_projectile_clip(duration: float = 5.0, 
                           velocity: float = 50.0, 
                           angle: float = 45.0,
                           title: str = "Projectile Motion") -> VideoClip:
    """
    Create animated projectile motion clip.
    Shows parabolic trajectory with velocity vectors.
    """
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
        
        # Gradient background
        _draw_gradient_bg(draw, (WIDTH, HEIGHT), (18, 32, 58), (35, 62, 102))
        
        # Title
        draw.text((WIDTH // 2 - 100, 30), title, fill=(220, 240, 255), font=font_title)
        
        # Ground line
        draw.line([(margin - 20, ground_y), (WIDTH - margin + 20, ground_y)], 
                  fill=(100, 150, 200), width=2)
        
        # Draw trajectory path (full parabola)
        path_points = []
        for i in range(100):
            ti = i * t_flight / 100
            px = origin_x + vx * ti * scale
            py = ground_y - (vy * ti - 0.5 * g * ti * ti) * scale
            path_points.append((px, py))
        
        if len(path_points) >= 2:
            draw.line(path_points, fill=(80, 200, 255, 128), width=1)
        
        # Current position based on animation time
        progress = min(t / duration, 1.0)
        current_t = progress * t_flight
        
        ball_x = origin_x + vx * current_t * scale
        ball_y = ground_y - (vy * current_t - 0.5 * g * current_t * current_t) * scale
        
        # Trail (previous positions)
        for i in range(20):
            past_t = current_t - (i + 1) * 0.05
            if past_t > 0:
                px = origin_x + vx * past_t * scale
                py = ground_y - (vy * past_t - 0.5 * g * past_t * past_t) * scale
                alpha = int(255 * (1 - i / 20))
                radius = max(2, 8 - i // 3)
                draw.ellipse([px - radius, py - radius, px + radius, py + radius],
                            fill=(80, 200, 255))
        
        # Ball
        radius = 12
        draw.ellipse([ball_x - radius, ball_y - radius, ball_x + radius, ball_y + radius],
                    fill=(255, 200, 100), outline=(255, 255, 255))
        
        # Velocity vector
        current_vy = vy - g * current_t
        arrow_scale = 1.5
        arrow_end_x = ball_x + vx * arrow_scale
        arrow_end_y = ball_y - current_vy * arrow_scale
        draw.line([(ball_x, ball_y), (arrow_end_x, arrow_end_y)], fill=(100, 255, 200), width=2)
        
        # Info box
        info_y = HEIGHT - 70
        draw.text((margin, info_y), f"v₀ = {velocity} m/s  θ = {angle}°", 
                  fill=(200, 220, 255), font=font_info)
        draw.text((margin, info_y + 25), f"Range: {max_range:.1f}m  Max Height: {max_height:.1f}m",
                  fill=(180, 200, 240), font=font_label)
        
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
    """
    font_title = _load_font(28)
    font_label = _load_font(16)
    font_info = _load_font(18)
    
    center_y = HEIGHT // 2
    wave_amplitude = 120  # pixels
    
    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        _draw_gradient_bg(draw, (WIDTH, HEIGHT), (12, 38, 68), (28, 68, 118))
        
        # Title
        draw.text((WIDTH // 2 - 80, 30), title, fill=(220, 245, 255), font=font_title)
        
        # Axis lines
        draw.line([(50, center_y), (WIDTH - 50, center_y)], fill=(100, 150, 200), width=1)
        draw.line([(100, center_y - 150), (100, center_y + 150)], fill=(100, 150, 200), width=1)
        
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
# BUBBLE SORT ANIMATION
# ============================================================

def create_bubble_sort_clip(duration: float = 8.0,
                            array: Optional[List[int]] = None,
                            title: str = "Bubble Sort") -> VideoClip:
    """
    Create animated bubble sort visualization.
    Shows step-by-step sorting with comparisons highlighted.
    """
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
        
        # Gradient background
        _draw_gradient_bg(draw, (WIDTH, HEIGHT), (42, 25, 15), (78, 52, 32))
        
        # Title
        draw.text((WIDTH // 2 - 80, 30), title, fill=(255, 240, 220), font=font_title)
        
        # Current state based on time
        progress = min(t / duration, 0.99)
        state_idx = int(progress * total_steps)
        current_state = states[min(state_idx, len(states) - 1)]
        
        # Get comparison info
        compare_i, compare_j, swapped = -1, -1, False
        if state_idx > 0 and state_idx <= len(comparisons):
            compare_i, compare_j, swapped = comparisons[state_idx - 1]
        
        # Draw bars
        ground_y = HEIGHT - 120
        max_bar_height = 280
        
        for i, val in enumerate(current_state):
            bar_height = int((val / max_val) * max_bar_height)
            x = start_x + i * (bar_width + bar_gap)
            y = ground_y - bar_height
            
            # Color based on comparison state
            if i == compare_i or i == compare_j:
                if swapped:
                    color = (255, 100, 100)  # Red for swap
                else:
                    color = (100, 255, 150)  # Green for no swap
            else:
                color = (255, 190, 100)  # Normal orange
            
            draw.rectangle([x, y, x + bar_width, ground_y], fill=color, outline=(255, 255, 255))
            
            # Value label
            text_x = x + bar_width // 2 - 10
            draw.text((text_x, y - 25), str(val), fill=(255, 255, 255), font=font_value)
        
        # Info box
        info_y = HEIGHT - 60
        step_text = f"Step {state_idx}/{total_steps - 1}"
        if state_idx == total_steps - 1:
            step_text = "Sorted!"
        draw.text((WIDTH // 2 - 50, info_y), step_text, fill=(255, 240, 220), font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# BINARY SEARCH ANIMATION
# ============================================================

def create_binary_search_clip(duration: float = 8.0,
                              array: Optional[List[int]] = None,
                              target: int = 7,
                              title: str = "Binary Search") -> VideoClip:
    """
    Create animated binary search visualization.
    Shows narrowing search range with low/mid/high pointers.
    """
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
        
        # Gradient background
        _draw_gradient_bg(draw, (WIDTH, HEIGHT), (15, 28, 52), (32, 58, 98))
        
        # Title
        draw.text((WIDTH // 2 - 80, 30), title, fill=(220, 235, 255), font=font_title)
        draw.text((WIDTH // 2 - 60, 65), f"Finding: {target}", fill=(180, 200, 255), font=font_info)
        
        # Current state
        progress = min(t / duration, 0.99)
        state_idx = int(progress * total_steps)
        low, high, mid, found = states[min(state_idx, len(states) - 1)]
        
        # Draw array boxes
        for i, val in enumerate(arr):
            x = start_x + i * (box_size + box_gap)
            y = center_y
            
            # Color based on state
            if found and i == mid:
                color = (100, 255, 150)  # Green - found
            elif i < low or i > high:
                color = (60, 60, 80)  # Dimmed - eliminated
            elif i == mid:
                color = (255, 200, 100)  # Orange - current mid
            elif i == low or i == high:
                color = (100, 180, 255)  # Blue - boundaries
            else:
                color = (80, 100, 140)  # Normal
            
            draw.rectangle([x, y, x + box_size, y + box_size], fill=color, outline=(255, 255, 255))
            
            # Value
            text_x = x + box_size // 2 - 8
            draw.text((text_x, y + box_size // 2 - 10), str(val), fill=(255, 255, 255), font=font_value)
            
            # Index
            draw.text((text_x, y + box_size + 5), str(i), fill=(150, 170, 200), font=font_label)
        
        # Pointer labels
        pointer_y = center_y - 30
        if low <= n - 1:
            lx = start_x + low * (box_size + box_gap) + box_size // 2 - 10
            draw.text((lx, pointer_y), "low", fill=(100, 180, 255), font=font_label)
        
        if high >= 0 and high <= n - 1:
            hx = start_x + high * (box_size + box_gap) + box_size // 2 - 10
            draw.text((hx, pointer_y - 15), "high", fill=(100, 180, 255), font=font_label)
        
        if 0 <= mid < n:
            mx = start_x + mid * (box_size + box_gap) + box_size // 2 - 10
            draw.text((mx, center_y + box_size + 25), "mid", fill=(255, 200, 100), font=font_label)
        
        # Status
        info_y = HEIGHT - 80
        if found:
            status = f"Found {target} at index {mid}!"
            color = (100, 255, 150)
        else:
            status = f"Step {state_idx + 1}: Checking index {mid}"
            color = (200, 220, 255)
        draw.text((WIDTH // 2 - 100, info_y), status, fill=color, font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# QUADRATIC GRAPH ANIMATION
# ============================================================

def create_quadratic_clip(duration: float = 5.0,
                          a: float = 1.0,
                          b: float = -3.0,
                          c: float = 2.0,
                          title: str = "Quadratic Function") -> VideoClip:
    """
    Create animated quadratic function graph.
    Shows parabola being drawn with vertex and roots marked.
    """
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
        
        # Gradient background
        _draw_gradient_bg(draw, (WIDTH, HEIGHT), (38, 20, 58), (68, 42, 98))
        
        # Title and equation
        draw.text((WIDTH // 2 - 100, 25), title, fill=(240, 225, 255), font=font_title)
        
        eq_text = f"y = {a}x² + {b}x + {c}" if b >= 0 else f"y = {a}x² {b}x + {c}"
        draw.text((WIDTH // 2 - 80, 55), eq_text, fill=(255, 200, 150), font=font_eq)
        
        # Axes
        draw.line([(50, graph_center_y), (WIDTH - 50, graph_center_y)], fill=(150, 130, 180), width=1)
        draw.line([(graph_center_x, 100), (graph_center_x, HEIGHT - 80)], fill=(150, 130, 180), width=1)
        
        # Axis labels
        draw.text((WIDTH - 45, graph_center_y - 20), "x", fill=(180, 160, 200), font=font_label)
        draw.text((graph_center_x + 10, 105), "y", fill=(180, 160, 200), font=font_label)
        
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
            draw.line(points, fill=(255, 180, 120), width=3)
        
        # Mark vertex (after curve is drawn)
        if progress > 0.7:
            vx_px = graph_center_x + vertex_x * scale
            vy_px = graph_center_y - vertex_y * scale
            if 50 < vx_px < WIDTH - 50 and 90 < vy_px < HEIGHT - 70:
                draw.ellipse([vx_px - 6, vy_px - 6, vx_px + 6, vy_px + 6],
                            fill=(100, 255, 200), outline=(255, 255, 255))
                draw.text((vx_px + 10, vy_px - 5), f"({vertex_x:.1f}, {vertex_y:.1f})",
                          fill=(150, 255, 220), font=font_label)
        
        # Mark roots (after vertex)
        if progress > 0.85 and roots:
            for root in roots:
                rx_px = graph_center_x + root * scale
                if 50 < rx_px < WIDTH - 50:
                    draw.ellipse([rx_px - 5, graph_center_y - 5, rx_px + 5, graph_center_y + 5],
                                fill=(255, 150, 150))
                    draw.text((rx_px - 10, graph_center_y + 10), f"{root:.1f}",
                              fill=(255, 180, 180), font=font_label)
        
        # Info box
        info_y = HEIGHT - 60
        info_text = f"Vertex: ({vertex_x:.2f}, {vertex_y:.2f})"
        if roots:
            info_text += f"  Roots: {roots[0]:.2f}, {roots[1]:.2f}"
        draw.text((100, info_y), info_text, fill=(220, 200, 240), font=font_info)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)


# ============================================================
# PENDULUM ANIMATION
# ============================================================

def create_pendulum_clip(duration: float = 5.0,
                         length: float = 1.0,
                         max_angle: float = 30.0,
                         title: str = "Simple Pendulum") -> VideoClip:
    """
    Create animated pendulum motion.
    Shows oscillation with angle and period information.
    """
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
        
        # Gradient background
        _draw_gradient_bg(draw, (WIDTH, HEIGHT), (18, 32, 58), (35, 62, 102))
        
        # Title
        draw.text((WIDTH // 2 - 100, 25), title, fill=(220, 240, 255), font=font_title)
        
        # Current angle (simple harmonic motion)
        angle = max_angle_rad * math.cos(omega * t)
        
        # Calculate bob position
        bob_x = pivot_x + rope_length * math.sin(angle)
        bob_y = pivot_y + rope_length * math.cos(angle)
        
        # Draw pivot
        draw.ellipse([pivot_x - 8, pivot_y - 8, pivot_x + 8, pivot_y + 8],
                    fill=(150, 150, 160), outline=(200, 200, 210))
        
        # Draw rope
        draw.line([(pivot_x, pivot_y), (bob_x, bob_y)], fill=(180, 180, 190), width=3)
        
        # Draw bob
        bob_radius = 25
        draw.ellipse([bob_x - bob_radius, bob_y - bob_radius, 
                     bob_x + bob_radius, bob_y + bob_radius],
                    fill=(255, 200, 100), outline=(255, 255, 255))
        
        # Draw arc showing swing range
        arc_radius = 80
        left_angle = 90 - max_angle
        right_angle = 90 + max_angle
        draw.arc([pivot_x - arc_radius, pivot_y - arc_radius,
                 pivot_x + arc_radius, pivot_y + arc_radius],
                left_angle, right_angle, fill=(100, 180, 255), width=2)
        
        # Angle indicator line (vertical reference)
        draw.line([(pivot_x, pivot_y), (pivot_x, pivot_y + 100)],
                  fill=(100, 150, 200), width=1)
        
        # Current angle text
        angle_deg = math.degrees(angle)
        draw.text((pivot_x + 50, pivot_y + 40), f"θ = {angle_deg:.1f}°",
                  fill=(150, 200, 255), font=font_label)
        
        # Info box
        info_y = HEIGHT - 80
        draw.text((100, info_y), f"Length: {length} m  Period: {period:.2f} s",
                  fill=(200, 220, 255), font=font_info)
        draw.text((100, info_y + 25), f"Max angle: ±{max_angle}°",
                  fill=(180, 200, 240), font=font_label)
        
        return np.array(img)
    
    return VideoClip(make_frame, duration=duration)
