# src/card_generator.py

"""
Visual card image generator for educational video sections.
Creates themed card images using PIL with topic-relevant icons and diagrams.
All text rendering happens here — no ImageMagick/TextClip needed.
"""

import os
import math
import hashlib
import re
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# Theme detection and colors
# ============================================================

def _safe_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower().strip())[:40]


def _detect_theme(*parts: str) -> str:
    """Detect visual theme from concept text."""
    combined = " ".join(str(p).lower() for p in parts)
    theme_map = {
        "matrix": "matrix", "determinant": "determinant", "eigen": "eigen",
        "projectile": "projectile", "trajectory": "projectile",
        "quadratic": "quadratic", "parabola": "quadratic",
        "sine": "sine", "wave": "sine", "oscillat": "sine",
        "binary search": "binary_search", "bubble sort": "bubble_sort",
        "sort": "bubble_sort", "photosynthesis": "photosynthesis",
        "probability": "probability", "dice": "probability",
        "linear equation": "linear_equation", "slope": "linear_equation",
        "gravity": "physics", "force": "physics", "newton": "physics",
        "cell": "biology", "dna": "biology", "protein": "biology",
        "atom": "chemistry", "molecule": "chemistry", "element": "chemistry",
        "gas": "chemistry", "pressure": "chemistry", "thermodynamics": "chemistry",
        "crystal": "chemistry", "lattice": "chemistry", "inorganic": "chemistry",
        "organic": "chemistry", "reaction": "chemistry", "bond": "chemistry",
        "periodic": "chemistry", "metal": "chemistry"
    }
    for keyword, theme in theme_map.items():
        if keyword in combined:
            return theme
    return "generic"


def _shift_color(color, shift):
    """Shift an RGB color tuple by a small amount for slide variation."""
    return tuple(max(0, min(255, c + shift)) for c in color)


def _theme_palette(theme: str, slide_index: int = 0):
    """
    Get full color palette for a theme.
    slide_index shifts colors so each slide looks distinct.
    Returns: (bg_top, bg_bottom, accent, heading_bg, text_color, point_color)
    """
    palettes = {
        "matrix":          ((15, 28, 52), (32, 58, 98),  (100, 180, 255), (10, 18, 38), (220, 235, 255), (140, 200, 255)),
        "determinant":     ((20, 32, 58), (38, 62, 102), (120, 190, 255), (12, 20, 42), (220, 235, 255), (150, 210, 255)),
        "eigen":           ((22, 28, 55), (40, 55, 95),  (180, 160, 255), (12, 18, 38), (225, 230, 255), (180, 170, 255)),
        "projectile":      ((18, 32, 58), (35, 62, 102), (80, 200, 255),  (10, 20, 40), (220, 240, 255), (100, 220, 200)),
        "quadratic":       ((38, 20, 58), (68, 42, 98),  (255, 180, 120), (22, 12, 38), (240, 225, 255), (255, 200, 150)),
        "sine":            ((12, 38, 68), (28, 68, 118), (80, 230, 255),  (8, 24, 48),  (220, 245, 255), (100, 240, 255)),
        "binary_search":   ((42, 25, 15), (78, 52, 32),  (255, 190, 100), (28, 16, 8),  (255, 240, 220), (255, 210, 130)),
        "bubble_sort":     ((38, 30, 12), (72, 58, 28),  (255, 200, 80),  (24, 18, 6),  (255, 240, 210), (255, 220, 100)),
        "photosynthesis":  ((12, 38, 22), (28, 68, 42),  (120, 230, 140), (6, 24, 14),  (220, 255, 230), (140, 240, 160)),
        "probability":     ((45, 28, 38), (82, 52, 68),  (255, 160, 200), (28, 16, 24), (255, 230, 240), (255, 180, 210)),
        "linear_equation": ((18, 42, 38), (35, 78, 68),  (120, 255, 200), (10, 26, 22), (220, 255, 240), (140, 255, 210)),
        "physics":         ((15, 30, 55), (30, 58, 95),  (100, 200, 255), (8, 18, 38),  (220, 240, 255), (120, 210, 255)),
        "biology":         ((15, 38, 25), (30, 68, 48),  (100, 220, 150), (8, 24, 15),  (220, 255, 235), (120, 230, 170)),
        "chemistry":       ((25, 20, 45), (48, 38, 82),  (180, 140, 255), (15, 12, 30), (235, 225, 255), (190, 160, 255)),
        "generic":         ((18, 32, 62), (35, 60, 105), (100, 180, 240), (10, 20, 42), (225, 238, 255), (130, 195, 250)),
    }
    base = palettes.get(theme, palettes["generic"])
    
    if slide_index == 0:
        return base
    
    # Shift colors based on slide index for variety
    # Each slide gets a different channel boosted
    shifts = [
        (0, 0, 0),      # slide 0: base
        (8, -4, 12),     # slide 1: slightly bluer/purple
        (-5, 10, 5),     # slide 2: slightly greener
        (12, 5, -6),     # slide 3: slightly warmer
        (-3, 8, 14),     # slide 4: slightly teal
    ]
    s = shifts[slide_index % len(shifts)]
    
    return (
        _shift_color(base[0], s[0]),  # bg_top
        _shift_color(base[1], s[1]),  # bg_bottom
        base[2],                       # accent stays same
        _shift_color(base[3], s[0] // 2),  # heading_bg
        base[4],                       # text_color stays
        base[5],                       # point_color stays
    )


def _load_font(size: int):
    """Load a font with fallbacks."""
    font_paths = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return ImageFont.load_default()


def _load_bold_font(size: int):
    """Load a bold font with fallbacks."""
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return _load_font(size)


# ============================================================
# Topic-relevant icon/diagram drawing
# ============================================================

def _draw_topic_illustration(draw, theme, x, y, w, h):
    """Draw a small topic-relevant illustration/icon on the card."""
    
    cx, cy = x + w // 2, y + h // 2
    
    if theme == "photosynthesis":
        # Sun + leaf
        sun_x, sun_y = x + w - 50, y + 30
        draw.ellipse((sun_x - 20, sun_y - 20, sun_x + 20, sun_y + 20), fill=(255, 220, 80))
        for i in range(8):
            angle = i * math.pi / 4
            x0 = int(sun_x + math.cos(angle) * 28)
            y0 = int(sun_y + math.sin(angle) * 28)
            x1 = int(sun_x + math.cos(angle) * 38)
            y1 = int(sun_y + math.sin(angle) * 38)
            draw.line([(x0, y0), (x1, y1)], fill=(255, 230, 100), width=2)
        # Leaf shape
        leaf_cx = x + 60
        leaf_cy = y + h - 50
        draw.ellipse((leaf_cx - 30, leaf_cy - 15, leaf_cx + 30, leaf_cy + 15), fill=(80, 180, 100))
        draw.line([(leaf_cx - 25, leaf_cy), (leaf_cx + 25, leaf_cy)], fill=(60, 140, 80), width=2)
    
    elif theme in ("matrix", "determinant", "eigen"):
        # Matrix grid
        cell = 22
        gx, gy = x + w - 90, y + 20
        for r in range(2):
            for c in range(2):
                rx, ry = gx + c * cell, gy + r * cell
                draw.rectangle((rx, ry, rx + cell, ry + cell), outline=(120, 170, 230), width=2)
                draw.text((rx + 7, ry + 4), str(r * 2 + c + 1), fill=(180, 210, 255), font=_load_font(14))
    
    elif theme == "projectile":
        # Parabola curve
        pts = []
        for i in range(50):
            t = i / 49
            px = int(x + 20 + t * (w - 40))
            py = int(y + h - 30 - 4 * (w - 40) * t * (1 - t) * 0.3)
            pts.append((px, py))
        if len(pts) > 1:
            draw.line(pts, fill=(80, 220, 255), width=3)
        # Ball at peak
        peak_idx = len(pts) // 2
        if peak_idx < len(pts):
            draw.ellipse((pts[peak_idx][0] - 6, pts[peak_idx][1] - 6,
                          pts[peak_idx][0] + 6, pts[peak_idx][1] + 6), fill=(255, 200, 80))
    
    elif theme == "quadratic":
        # Parabola
        pts = []
        for i in range(-30, 31):
            px = int(cx + i * 2)
            py = int(cy + i * i * 0.04 - 30)
            if y <= py <= y + h:
                pts.append((px, py))
        if len(pts) > 1:
            draw.line(pts, fill=(255, 200, 100), width=3)
    
    elif theme == "sine":
        # Sine wave
        pts = []
        for i in range(int(w - 40)):
            px = x + 20 + i
            py = int(cy + math.sin(i * 0.08) * 25)
            pts.append((px, py))
        if len(pts) > 1:
            draw.line(pts, fill=(100, 230, 255), width=3)
    
    elif theme == "binary_search":
        # Array cells
        bw, gap = 28, 4
        start_x = x + 10
        by = cy - 12
        vals = [3, 7, 11, 15, 22, 30]
        for i, v in enumerate(vals):
            bx = start_x + i * (bw + gap)
            color = (255, 200, 100) if i == 3 else (140, 170, 200)
            draw.rounded_rectangle((bx, by, bx + bw, by + 24), radius=4, fill=color)
            draw.text((bx + 6, by + 4), str(v), fill=(20, 20, 30), font=_load_font(12))
    
    elif theme == "bubble_sort":
        # Bar chart
        bars = [40, 18, 55, 28, 48]
        start_x = x + 20
        base = y + h - 15
        for i, bh in enumerate(bars):
            bx = start_x + i * 35
            color = (255, 190, 100) if i in (1, 2) else (140, 180, 220)
            draw.rectangle((bx, base - bh, bx + 25, base), fill=color)
    
    elif theme == "probability":
        # Dice
        dx, dy = x + w - 65, y + 15
        ds = 45
        draw.rounded_rectangle((dx, dy, dx + ds, dy + ds), radius=6, fill=(255, 255, 255), outline=(180, 160, 190), width=2)
        dot_r = 4
        offsets = [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)]
        for ox, oy in offsets:
            ddx = int(dx + ox * ds)
            ddy = int(dy + oy * ds)
            draw.ellipse((ddx - dot_r, ddy - dot_r, ddx + dot_r, ddy + dot_r), fill=(40, 30, 50))
    
    elif theme == "linear_equation":
        # Line graph
        pts = []
        for i in range(int(w - 40)):
            px = x + 20 + i
            py = int(cy + 20 - i * 0.3)
            pts.append((px, py))
        if len(pts) > 1:
            draw.line(pts, fill=(120, 255, 190), width=3)
        # Axes
        draw.line([(x + 20, y + 10), (x + 20, y + h - 10)], fill=(160, 200, 180), width=1)
        draw.line([(x + 10, y + h - 20), (x + w - 10, y + h - 20)], fill=(160, 200, 180), width=1)
    
    elif theme == "physics":
        # Arrow (force vector)
        draw.line([(x + 20, cy + 10), (x + w - 30, cy - 15)], fill=(100, 210, 255), width=3)
        # Arrowhead
        ax, ay = x + w - 30, cy - 15
        draw.polygon([(ax, ay), (ax - 12, ay - 5), (ax - 8, ay + 8)], fill=(100, 210, 255))
    
    elif theme == "biology":
        # Cell circle
        draw.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), outline=(100, 220, 160), width=2)
        draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(80, 180, 130))  # nucleus
    
    elif theme == "chemistry":
        # Atom rings
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(200, 160, 255))
        draw.ellipse((cx - 25, cy - 12, cx + 25, cy + 12), outline=(160, 130, 220), width=2)
        draw.ellipse((cx - 15, cy - 22, cx + 15, cy + 22), outline=(140, 120, 200), width=2)
    
        # Add flask icon for general chemistry
        flask_x = x + w - 40
        flask_y = y + h - 10
        # Flask body
        draw.polygon([
            (flask_x - 15, flask_y), (flask_x + 15, flask_y),
            (flask_x + 5, flask_y - 25), (flask_x + 5, flask_y - 40),
            (flask_x - 5, flask_y - 40), (flask_x - 5, flask_y - 25)
        ], fill=(180, 140, 255))
        # Liquid inside
        draw.polygon([(flask_x - 12, flask_y - 2), (flask_x + 12, flask_y - 2), (flask_x, flask_y - 20)], fill=(100, 255, 200))

    else:
        # Generic: lightbulb icon
        bx, by = x + w - 55, y + 15
        draw.ellipse((bx, by, bx + 36, by + 36), fill=(255, 220, 100), outline=(255, 240, 180), width=2)
        draw.rectangle((bx + 12, by + 34, bx + 24, by + 46), fill=(200, 170, 110))


# ============================================================
# Word wrapping utility
# ============================================================

def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    """Word-wrap text to fit within max_width pixels."""
    words = str(text).split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(test_line) * (font.size * 0.6 if hasattr(font, 'size') else 10)
        
        if tw <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


# ============================================================
# Card generators
# ============================================================

def create_section_card(
    concept: str,
    heading: str,
    body: str,
    index: int,
    key_points: list = None,
    output_dir: str = "outputs/generated_images"
) -> str:
    """
    Create a themed card image for a video section.
    Includes topic-relevant illustration, heading, body text, and key points.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    kp_hash = hashlib.md5(str(key_points).encode()).hexdigest()[:4] if key_points else "0000"
    slug = _safe_slug(concept)
    digest = hashlib.md5(f"{concept}-{heading}-{index}-{kp_hash}".encode("utf-8")).hexdigest()[:8]
    filename = f"{slug}_{index}_{digest}.png"
    out_path = os.path.join(output_dir, filename)
    
    if os.path.exists(out_path):
        return out_path
    
    width, height = 960, 540
    theme = _detect_theme(concept, heading, body)
    # Each slide gets shifted colors for visual variety
    bg_top, bg_bottom, accent, heading_bg, text_color, point_color = _theme_palette(theme, slide_index=index)
    
    # Create gradient background
    image = Image.new("RGB", (width, height), bg_top)
    draw = ImageDraw.Draw(image)
    
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * ratio),
            int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * ratio),
            int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)
    
    # Fonts
    heading_font = _load_bold_font(30)
    body_font = _load_font(20)
    points_font = _load_font(18)
    step_font = _load_bold_font(48)
    small_font = _load_font(14)
    
    # --- Layout: concept image on right, text on left ---
    pad = 36
    concept_img_w = 280  # larger illustration area for concept image
    concept_img_h = 180
    text_area_x = pad
    text_area_w = width - pad * 2
    
    # Step number (large, bottom-right, subtle)
    step_text = str(index + 1)
    draw.text((width - pad - 40, height - pad - 50), step_text, fill=(*heading_bg[:3],), font=step_font)
    
    # Heading bar
    heading_bar_y = pad - 4
    heading_bar_h = 50
    draw.rounded_rectangle(
        (pad - 4, heading_bar_y, width - pad + 4, heading_bar_y + heading_bar_h),
        radius=12, fill=heading_bg
    )
    # Accent line on left
    draw.rectangle((pad - 4, heading_bar_y, pad + 2, heading_bar_y + heading_bar_h), fill=accent)
    # Heading text
    draw.text((pad + 14, heading_bar_y + 10), heading[:65], fill=text_color, font=heading_font)
    
    # Concept image / illustration (right side, large)
    img_x = width - pad - concept_img_w
    img_y = heading_bar_y + heading_bar_h + 14
    # Draw a subtle panel behind the illustration
    panel_color = (heading_bg[0] + 5, heading_bg[1] + 5, heading_bg[2] + 5)
    draw.rounded_rectangle(
        (img_x - 8, img_y - 8, img_x + concept_img_w + 8, img_y + concept_img_h + 8),
        radius=12, fill=panel_color
    )
    _draw_topic_illustration(draw, theme, img_x, img_y, concept_img_w, concept_img_h)
    
    # Body text (left side, wraps to avoid concept image)
    body_y = heading_bar_y + heading_bar_h + 22
    body_max_w = text_area_w - concept_img_w - 30  # Leave space for concept image
    
    if body:
        body_lines = _wrap_text(body, body_font, body_max_w, draw)
        for i, ln in enumerate(body_lines[:6]):
            draw.text((text_area_x, body_y + i * 28), ln, fill=text_color, font=body_font)
        body_bottom = body_y + min(len(body_lines), 6) * 28 + 12
    else:
        body_bottom = body_y + 12
    
    # Key points (full width below body + concept image)
    kp_y = max(body_bottom, img_y + concept_img_h + 16)
    if key_points:
        # Subtle separator line
        sep_color = (accent[0] // 2, accent[1] // 2, accent[2] // 2)
        draw.line([(pad, kp_y), (width - pad, kp_y)], fill=sep_color, width=1)
        kp_y += 12
        
        for i, point in enumerate(key_points[:4]):
            bullet_text = f"  ●  {point}"
            lines = _wrap_text(bullet_text, points_font, text_area_w - 20, draw)
            for j, ln in enumerate(lines[:2]):
                draw.text((text_area_x + 8, kp_y), ln, fill=point_color, font=points_font)
                kp_y += 24
            kp_y += 4
    
    # Bottom bar with concept name
    draw.rectangle((0, height - 28, width, height), fill=heading_bg)
    draw.text((pad, height - 24), concept[:60], fill=(*accent,), font=small_font)
    draw.text((width - pad - 60, height - 24), f"Step {index + 1}", fill=point_color, font=small_font)
    
    image.save(out_path)
    return out_path


def create_title_card(
    title: str,
    summary: str,
    category: str = "general",
    output_dir: str = "outputs/generated_images"
) -> str:
    """Create a title/intro card for the video."""
    os.makedirs(output_dir, exist_ok=True)
    
    slug = _safe_slug(title)
    digest = hashlib.md5(f"title-{title}-{summary}".encode("utf-8")).hexdigest()[:8]
    filename = f"title_{slug}_{digest}.png"
    out_path = os.path.join(output_dir, filename)
    
    if os.path.exists(out_path):
        return out_path
    
    width, height = 960, 540
    theme = _detect_theme(title, category)
    bg_top, bg_bottom, accent, heading_bg, text_color, point_color = _theme_palette(theme)
    
    image = Image.new("RGB", (width, height), bg_top)
    draw = ImageDraw.Draw(image)
    
    # Gradient background
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * ratio),
            int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * ratio),
            int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)
    
    # Fonts
    title_font = _load_bold_font(40)
    summary_font = _load_font(22)
    category_font = _load_bold_font(14)
    
    pad = 48
    
    # Outer frame
    frame_color = (accent[0] // 3, accent[1] // 3, accent[2] // 3)
    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=20, outline=frame_color, width=2)
    
    # Category badge (top center)
    cat_text = category.upper()
    try:
        cat_bbox = draw.textbbox((0, 0), cat_text, font=category_font)
        cat_w = cat_bbox[2] - cat_bbox[0] + 24
    except:
        cat_w = len(cat_text) * 10 + 24
    
    cat_x = (width - cat_w) // 2
    draw.rounded_rectangle((cat_x, 40, cat_x + cat_w, 62), radius=8, fill=heading_bg)
    draw.text((cat_x + 12, 43), cat_text, fill=accent, font=category_font)
    
    # Topic illustration (centered, above title)
    illus_w, illus_h = 280, 110
    _draw_topic_illustration(draw, theme, (width - illus_w) // 2, 80, illus_w, illus_h)
    
    # Title text (centered)
    title_text = title[:55]
    title_lines = _wrap_text(title_text, title_font, width - pad * 2, draw)
    
    title_y = 210
    for i, ln in enumerate(title_lines[:2]):
        try:
            bbox = draw.textbbox((0, 0), ln, font=title_font)
            tw = bbox[2] - bbox[0]
        except:
            tw = len(ln) * 22
        tx = max(pad, (width - tw) // 2)
        # Text shadow
        draw.text((tx + 1, title_y + i * 48 + 1), ln, fill=(0, 0, 0), font=title_font)
        draw.text((tx, title_y + i * 48), ln, fill=(255, 255, 255), font=title_font)
    
    title_bottom = title_y + min(len(title_lines), 2) * 48 + 16
    
    # Accent divider
    div_y = title_bottom + 4
    div_w = min(350, width - pad * 4)
    draw.line([((width - div_w) // 2, div_y), ((width + div_w) // 2, div_y)], fill=accent, width=2)
    
    # Summary text (centered)
    if summary:
        summary_text = summary[:150]
        summary_lines = _wrap_text(summary_text, summary_font, width - pad * 2 - 40, draw)
        summary_y = div_y + 20
        for i, ln in enumerate(summary_lines[:3]):
            try:
                bbox = draw.textbbox((0, 0), ln, font=summary_font)
                sw = bbox[2] - bbox[0]
            except:
                sw = len(ln) * 12
            sx = max(pad, (width - sw) // 2)
            draw.text((sx, summary_y + i * 30), ln, fill=point_color, font=summary_font)
    
    # Bottom bar
    draw.rectangle((0, height - 28, width, height), fill=heading_bg)
    draw.text((pad, height - 24), "Educational Video", fill=frame_color, font=_load_font(13))
    
    image.save(out_path)
    return out_path


def create_facts_card(
    title: str,
    key_facts: list,
    category: str = "general",
    output_dir: str = "outputs/generated_images"
) -> str:
    """Create a key facts summary card for the video."""
    os.makedirs(output_dir, exist_ok=True)
    
    slug = _safe_slug(title)
    digest = hashlib.md5(f"facts-{title}-{str(key_facts)}".encode("utf-8")).hexdigest()[:8]
    filename = f"facts_{slug}_{digest}.png"
    out_path = os.path.join(output_dir, filename)
    
    if os.path.exists(out_path):
        return out_path
    
    width, height = 960, 540
    theme = _detect_theme(title, category)
    bg_top, bg_bottom, accent, heading_bg, text_color, point_color = _theme_palette(theme)
    
    image = Image.new("RGB", (width, height), bg_top)
    draw = ImageDraw.Draw(image)
    
    # Gradient background (darker for facts)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(bg_top[0] * 0.7 + (bg_bottom[0] * 0.7) * ratio),
            int(bg_top[1] * 0.7 + (bg_bottom[1] * 0.7) * ratio),
            int(bg_top[2] * 0.7 + (bg_bottom[2] * 0.7) * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)
    
    # Fonts
    header_font = _load_bold_font(34)
    fact_font = _load_font(22)
    title_font = _load_font(16)
    
    pad = 48
    
    # Header
    header_text = "Key Facts"
    try:
        bbox = draw.textbbox((0, 0), header_text, font=header_font)
        hw = bbox[2] - bbox[0]
    except:
        hw = len(header_text) * 20
    hx = (width - hw) // 2
    draw.text((hx, 40), header_text, fill=(255, 255, 255), font=header_font)
    
    # Accent bar under header
    draw.line([((width - 200) // 2, 82), ((width + 200) // 2, 82)], fill=accent, width=3)
    
    # Facts
    fact_y = 110
    for i, fact in enumerate(key_facts[:5]):
        star_color = (
            min(255, accent[0] + 40),
            min(255, accent[1] + 40),
            min(255, accent[2] + 40),
        )
        fact_text = f"★  {fact}"
        lines = _wrap_text(fact_text, fact_font, width - pad * 2 - 20, draw)
        for j, ln in enumerate(lines[:3]):
            color = star_color if j == 0 else point_color
            draw.text((pad + 10, fact_y), ln, fill=color, font=fact_font)
            fact_y += 30
        fact_y += 16  # Gap between facts
    
    # Topic illustration (bottom right)
    _draw_topic_illustration(draw, theme, width - 240, height - 130, 200, 90)
    
    # Bottom bar with title
    draw.rectangle((0, height - 28, width, height), fill=heading_bg)
    draw.text((pad, height - 24), title[:60], fill=accent, font=title_font)
    
    image.save(out_path)
    return out_path
