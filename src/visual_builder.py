# src/visual_builder.py

import math
import os
import re
import hashlib
from PIL import Image, ImageDraw, ImageFont


def _safe_slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", str(text).strip().lower()).strip("_")
    return cleaned[:40] or "concept"


def _detect_theme(*parts: str) -> str:
    text = " ".join(str(p or "") for p in parts).lower()

    if any(k in text for k in ["matrix multiplication", "multiply matrices", "matrix product"]):
        return "matrix_multiplication"

    if any(k in text for k in ["photosynthesis", "chlorophyll", "plant", "leaf", "sunlight"]):
        return "photosynthesis"
    if any(k in text for k in ["eigen", "eigenvalue", "eigenvector", "matrix", "vector space"]):
        return "eigen"
    if any(k in text for k in ["projectile", "trajectory", "launch angle", "gravity"]):
        return "projectile"
    if any(k in text for k in ["quadratic", "parabola", "x^2", "x²", "discriminant"]):
        return "quadratic"
    if any(k in text for k in ["sine", "sin(", "periodic", "wave"]):
        return "sine"
    if any(k in text for k in ["binary search", "midpoint", "sorted array"]):
        return "binary_search"
    if any(k in text for k in ["bubble sort", "swap", "sorting"]):
        return "bubble_sort"
    if any(k in text for k in ["determinant", "det(", "det a", "matrix inverse"]):
        return "determinant"
    if any(k in text for k in ["linear equation", "solve for x", "y = mx", "slope", "intercept"]):
        return "linear_equation"
    if any(k in text for k in ["probability", "dice", "coin", "chance", "odds", "random"]):
        return "probability"

    return "generic"


def _theme_colors(theme: str):
    palettes = {
        "matrix_multiplication": ((25, 62, 88), (46, 104, 136)),
        "photosynthesis": ((19, 75, 38), (42, 129, 71)),
        "eigen": ((34, 50, 92), (64, 90, 153)),
        "projectile": ((27, 55, 89), (48, 91, 145)),
        "quadratic": ((69, 37, 96), (108, 66, 144)),
        "sine": ((22, 63, 111), (45, 106, 171)),
        "binary_search": ((79, 43, 29), (132, 79, 53)),
        "bubble_sort": ((72, 50, 16), (132, 96, 35)),
        "determinant": ((32, 54, 78), (58, 92, 132)),
        "linear_equation": ((28, 68, 56), (52, 118, 94)),
        "probability": ((82, 48, 68), (138, 84, 118)),
        "generic": ((24, 62, 116), (50, 108, 164)),
    }
    return palettes.get(theme, palettes["generic"])


def _load_font(size: int):
    candidates = [
        "arial.ttf",
        "segoeui.ttf",
        "calibri.ttf",
        "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_theme_art(draw: ImageDraw.ImageDraw, theme: str, width: int, height: int):
    art_top = 68
    art_bottom = height - 88
    art_left = 34
    art_right = width - 34

    draw.rounded_rectangle((art_left, art_top, art_right, art_bottom), radius=18, outline=(225, 240, 255), width=2)

    if theme in {"projectile", "quadratic", "sine", "eigen", "generic"}:
        cx = art_left + 50
        cy = art_bottom - 30
        draw.line((cx, cy, art_right - 20, cy), fill=(210, 222, 238), width=2)
        draw.line((cx, cy, cx, art_top + 16), fill=(210, 222, 238), width=2)

    if theme == "projectile":
        pts = []
        for i in range(0, 260):
            x = i / 28.0
            y = 0.8 * x - 0.06 * x * x
            sx = int(art_left + 62 + i * 1.8)
            sy = int(art_bottom - 30 - y * 55)
            pts.append((sx, sy))
        draw.line(pts, fill=(255, 220, 80), width=4)
        bx, by = pts[min(len(pts) - 1, int(len(pts) * 0.55))]
        draw.ellipse((bx - 7, by - 7, bx + 7, by + 7), fill=(255, 245, 160))

    elif theme == "quadratic":
        pts = []
        for i in range(-170, 171):
            x = i / 40.0
            y = 0.4 * (x - 1.2) * (x - 1.2) - 1.6
            sx = int((art_left + art_right) / 2 + i * 1.35)
            sy = int((art_top + art_bottom) / 2 - y * 44)
            pts.append((sx, sy))
        draw.line(pts, fill=(255, 206, 120), width=4)

    elif theme == "sine":
        pts = []
        span = art_right - art_left - 90
        for i in range(span):
            angle = (i / max(1, span)) * 6.5 * math.pi
            sx = art_left + 60 + i
            sy = int((art_top + art_bottom) / 2 - math.sin(angle) * 54)
            pts.append((sx, sy))
        draw.line(pts, fill=(120, 245, 255), width=4)

    elif theme == "binary_search":
        values = [2, 5, 9, 14, 21, 30, 44]
        bw = 62
        gap = 10
        start_x = art_left + 42
        y0 = (art_top + art_bottom) // 2 - 24
        for i, value in enumerate(values):
            x0 = start_x + i * (bw + gap)
            x1 = x0 + bw
            color = (255, 198, 118) if i == 3 else (186, 206, 232)
            draw.rounded_rectangle((x0, y0, x1, y0 + 48), radius=8, fill=color)
            draw.text((x0 + 24, y0 + 17), str(value), fill=(24, 24, 24))
        draw.text((start_x + 3 * (bw + gap) + 6, y0 + 58), "mid", fill=(255, 235, 180))

    elif theme == "bubble_sort":
        bars = [50, 22, 74, 35, 60]
        start_x = art_left + 72
        base_y = art_bottom - 20
        for i, h in enumerate(bars):
            x0 = start_x + i * 86
            x1 = x0 + 48
            color = (255, 195, 113) if i in (1, 2) else (196, 214, 236)
            draw.rectangle((x0, base_y - h * 2, x1, base_y), fill=color)
        draw.text((start_x + 92, base_y - 172), "swap", fill=(255, 230, 170))

    elif theme == "photosynthesis":
        sun_x, sun_y = art_right - 82, art_top + 46
        draw.ellipse((sun_x - 26, sun_y - 26, sun_x + 26, sun_y + 26), fill=(255, 226, 99))
        for i in range(10):
            angle = i * (2 * math.pi / 10)
            x0 = int(sun_x + math.cos(angle) * 34)
            y0 = int(sun_y + math.sin(angle) * 34)
            x1 = int(sun_x + math.cos(angle) * 49)
            y1 = int(sun_y + math.sin(angle) * 49)
            draw.line((x0, y0, x1, y1), fill=(255, 232, 130), width=2)
        stem_x = art_left + 250
        draw.line((stem_x, art_bottom - 18, stem_x, art_top + 86), fill=(129, 214, 141), width=6)
        draw.ellipse((stem_x - 104, art_top + 90, stem_x + 16, art_top + 170), fill=(90, 176, 102), outline=(196, 245, 201), width=2)
        draw.ellipse((stem_x - 14, art_top + 110, stem_x + 106, art_top + 190), fill=(96, 188, 109), outline=(196, 245, 201), width=2)
        draw.polygon([(art_left + 80, art_top + 46), (art_left + 162, art_top + 46), (art_left + 150, art_top + 88)], fill=(156, 228, 255))
        draw.text((art_left + 70, art_top + 20), "CO2", fill=(220, 242, 255))
        draw.text((art_left + 166, art_top + 150), "O2", fill=(220, 242, 255))

    elif theme == "matrix_multiplication":
        mx_x = art_left + 40
        mx_y = art_top + 70
        cell = 42
        for r in range(2):
            for c in range(2):
                x0 = mx_x + c * cell
                y0 = mx_y + r * cell
                draw.rectangle((x0, y0, x0 + cell, y0 + cell), outline=(202, 222, 245), width=2)
                draw.text((x0 + 14, y0 + 11), str((r + 1) + c), fill=(226, 237, 255))

        draw.text((mx_x + 102, mx_y + 34), "×", fill=(255, 224, 140))

        mx2_x = mx_x + 130
        for r in range(2):
            for c in range(2):
                x0 = mx2_x + c * cell
                y0 = mx_y + r * cell
                draw.rectangle((x0, y0, x0 + cell, y0 + cell), outline=(202, 222, 245), width=2)
                draw.text((x0 + 14, y0 + 11), str((r + 2) * (c + 1)), fill=(226, 237, 255))

        draw.text((mx2_x + 102, mx_y + 34), "=", fill=(255, 224, 140))

        out_x = mx2_x + 130
        for r in range(2):
            for c in range(2):
                x0 = out_x + c * cell
                y0 = mx_y + r * cell
                draw.rectangle((x0, y0, x0 + cell, y0 + cell), outline=(158, 230, 202), width=2)
                draw.text((x0 + 14, y0 + 11), str((r + 2) * (c + 3)), fill=(212, 255, 232))

    elif theme == "eigen":
        matrix_x = art_left + 80
        matrix_y = art_top + 54
        cell = 44
        for r in range(3):
            for c in range(3):
                x0 = matrix_x + c * cell
                y0 = matrix_y + r * cell
                draw.rectangle((x0, y0, x0 + cell, y0 + cell), outline=(202, 222, 245), width=2)
                draw.text((x0 + 15, y0 + 13), str((r + 1) * (c + 2)), fill=(226, 237, 255))
        origin = (art_left + 335, art_bottom - 44)
        draw.line((origin[0], origin[1], origin[0] + 120, origin[1] - 86), fill=(255, 214, 117), width=4)
        draw.line((origin[0], origin[1], origin[0] + 68, origin[1] - 120), fill=(129, 228, 186), width=4)
        draw.text((origin[0] + 126, origin[1] - 92), "v", fill=(255, 214, 117))
        draw.text((origin[0] + 74, origin[1] - 126), "Av", fill=(129, 228, 186))

    elif theme == "determinant":
        # 2x2 matrix with cross-product lines
        mx_x = art_left + 120
        mx_y = art_top + 70
        cell = 58
        vals = [["a", "b"], ["c", "d"]]
        for r in range(2):
            for c in range(2):
                x0 = mx_x + c * cell
                y0 = mx_y + r * cell
                draw.rectangle((x0, y0, x0 + cell, y0 + cell), outline=(202, 222, 245), width=2)
                draw.text((x0 + 23, y0 + 18), vals[r][c], fill=(226, 237, 255))
        # diagonal lines showing ad - bc
        draw.line((mx_x + 29, mx_y + 29, mx_x + cell + 29, mx_y + cell + 29), fill=(140, 255, 180), width=3)
        draw.line((mx_x + cell + 29, mx_y + 29, mx_x + 29, mx_y + cell + 29), fill=(255, 140, 140), width=3)
        # formula
        draw.text((mx_x + 155, mx_y + 42), "= ad − bc", fill=(255, 235, 180))

    elif theme == "linear_equation":
        # Coordinate system with line y = mx + b
        cx = art_left + 110
        cy = (art_top + art_bottom) // 2
        axis_len = 180
        # axes
        draw.line((cx - axis_len, cy, cx + axis_len, cy), fill=(210, 222, 238), width=2)
        draw.line((cx, cy + axis_len // 2, cx, cy - axis_len // 2), fill=(210, 222, 238), width=2)
        # line y = 0.6x + 20
        pts = []
        for i in range(-140, 141):
            sx = cx + i
            sy = int(cy - (0.6 * i + 20))
            pts.append((sx, sy))
        draw.line(pts, fill=(120, 255, 180), width=4)
        # labels
        draw.text((cx + 160, cy + 8), "x", fill=(220, 240, 255))
        draw.text((cx + 6, cy - axis_len // 2 - 16), "y", fill=(220, 240, 255))
        draw.text((art_left + 360, art_top + 85), "y = mx + b", fill=(255, 235, 180))

    elif theme == "probability":
        # Dice and probability bar chart
        dice_x = art_left + 80
        dice_y = art_top + 80
        dice_size = 70
        draw.rounded_rectangle((dice_x, dice_y, dice_x + dice_size, dice_y + dice_size), radius=10, fill=(255, 255, 255), outline=(180, 200, 230), width=3)
        # dice dots (showing 5)
        dot_r = 7
        offsets = [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)]
        for ox, oy in offsets:
            cx = int(dice_x + ox * dice_size)
            cy = int(dice_y + oy * dice_size)
            draw.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r), fill=(40, 40, 60))
        # bar chart for probability distribution
        bar_x = art_left + 230
        bar_bot = art_bottom - 30
        bar_heights = [20, 55, 90, 110, 85, 50]
        bar_w = 40
        for i, h in enumerate(bar_heights):
            x0 = bar_x + i * (bar_w + 8)
            draw.rectangle((x0, bar_bot - h, x0 + bar_w, bar_bot), fill=(168, 218, 255))
        draw.text((bar_x + 70, bar_bot + 8), "outcomes", fill=(220, 240, 255))

    else:
        bulb_x = (art_left + art_right) // 2
        bulb_y = (art_top + art_bottom) // 2 - 20
        draw.ellipse((bulb_x - 58, bulb_y - 58, bulb_x + 58, bulb_y + 58), fill=(255, 220, 122), outline=(255, 236, 176), width=2)
        draw.rectangle((bulb_x - 18, bulb_y + 52, bulb_x + 18, bulb_y + 86), fill=(210, 180, 130))
        draw.text((bulb_x - 34, bulb_y + 96), "IDEA", fill=(238, 244, 255))


def _create_visual_card(base_dir: str, concept: str, heading: str, body: str, idx: int) -> str:
    os.makedirs(base_dir, exist_ok=True)

    concept_slug = _safe_slug(concept)
    digest = hashlib.md5(f"{concept}-{heading}-{idx}".encode("utf-8")).hexdigest()[:8]
    filename = f"{concept_slug}_{idx}_{digest}.png"
    out_path = os.path.join(base_dir, filename)

    if os.path.exists(out_path):
        return out_path

    width, height = 640, 360
    theme = _detect_theme(concept, heading, body)
    top_color, bottom_color = _theme_colors(theme)

    image = Image.new("RGB", (width, height), top_color)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)

    title_font = _load_font(30)
    body_font = _load_font(20)

    _draw_theme_art(draw, theme, width, height)

    draw.rounded_rectangle((26, 16, width - 26, 66), radius=12, fill=(12, 22, 40))
    draw.text((42, 29), heading[:54], fill=(240, 248, 255), font=title_font)

    body_text = str(body).strip() or heading
    wrapped = []
    words = body_text.split()
    line = ""
    max_chars = 50
    for word in words:
        probe = f"{line} {word}".strip()
        if len(probe) <= max_chars:
            line = probe
        else:
            if line:
                wrapped.append(line)
            line = word
    if line:
        wrapped.append(line)

    draw.rounded_rectangle((24, height - 86, width - 24, height - 20), radius=12, fill=(10, 18, 34))

    y_cursor = height - 74
    for ln in wrapped[:2]:
        draw.text((44, y_cursor), ln, fill=(230, 236, 246), font=body_font)
        y_cursor += 24

    image.save(out_path)
    return out_path


def _short_caption(text: str, max_words: int = 7) -> str:
    words = str(text).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "..."


def _detail_caption(text: str, max_words: int = 22) -> str:
    words = str(text).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "..."


def _normalize_step_text(step) -> str:
    """Extract clean text description from a step, which may be a string or complex dict."""
    
    if isinstance(step, str):
        # If it looks like a dict string, try to parse it
        if step.strip().startswith('{') and ':' in step:
            try:
                import ast
                parsed = ast.literal_eval(step)
                return _normalize_step_text(parsed)
            except:
                pass
        return step

    if isinstance(step, dict):
        # Priority keys that contain the actual step text
        text_keys = ["step", "text", "description", "title", "content", "value", 
                     "actionableFrameVisualization", "explanation", "step_text",
                     "visualization", "frame", "action", "actionableFrame"]
        
        for key in text_keys:
            value = step.get(key)
            if isinstance(value, str) and len(value.strip()) > 5:
                # Clean up the text - remove step numbers at start if present
                text = value.strip()
                # Remove leading step numbers like "1. " or "Step 1: "
                import re
                text = re.sub(r'^(\d+\.\s*|Step\s*\d+[:\s]*)', '', text, flags=re.IGNORECASE)
                if text:
                    return text
            elif isinstance(value, dict):
                nested = _normalize_step_text(value)
                if len(nested.strip()) > 10:
                    return nested

        # If no text keys found, try to find any long string value
        for key, value in step.items():
            if isinstance(value, str) and len(value.strip()) > 20:
                # Skip keys that look like metadata
                if key.lower() not in ('id', 'type', 'category', 'index', 'number'):
                    return value.strip()

        # Last resort: stringify but make it clean
        return ""

    if isinstance(step, (list, tuple)) and step:
        for item in step:
            normalized = _normalize_step_text(item)
            if len(normalized.strip()) > 10:
                return normalized

    return ""


def _is_subjective_concept(concept: str, reasoning: dict) -> bool:
    style = str(reasoning.get("pedagogy_style", "")).lower().strip()
    if style in {"subjective", "objective"}:
        return style == "subjective"

    text = f"{concept} {reasoning.get('title', '')}".lower()
    subjective_keywords = [
        "history", "philosophy", "literature", "ethics", "politics", "civics",
        "society", "culture", "biography", "democracy", "constitution"
    ]
    objective_keywords = [
        "matrix", "multiplication", "equation", "algorithm", "physics", "math",
        "sine", "quadratic", "projectile", "binary search", "bubble sort"
    ]

    if any(k in text for k in objective_keywords):
        return False
    if any(k in text for k in subjective_keywords):
        return True
    return False


def _strip_history_from_steps(steps):
    history_words = [
        "history", "historical", "origin", "invented", "inventor", "developed by",
        "in year", "in the year", "timeline", "century", "background", "biography"
    ]
    out = []
    for step in steps:
        txt = _normalize_step_text(step)
        low = txt.lower()
        if any(w in low for w in history_words):
            continue
        out.append(txt)
    return out


def build_visual_plan(concept: str, reasoning: dict):

    visual_elements = []
    animation_sequence = []

    title = reasoning.get("title", concept)
    steps = reasoning.get("steps", [])
    category = reasoning.get("category", "abstract")
    images_dir = os.path.join("outputs", "generated_images")
    is_subjective = _is_subjective_concept(concept, reasoning)

    # Extract topic analysis for visual approach decisions
    topic_analysis = reasoning.get("topic_analysis", {})
    topic_type = topic_analysis.get("topic_type", "context")
    visual_approach = topic_analysis.get("visual_approach", {})
    animation_style = topic_analysis.get("animation_style", {})

    # Configure based on topic type
    is_simulation_heavy = topic_type == "simulation"
    text_density = visual_approach.get("text_density", "rich")
    caption_length = visual_approach.get("caption_length", "detailed")
    animation_focus = visual_approach.get("animation_focus", False)

    normalized_steps = [_normalize_step_text(s) for s in steps]
    if not is_subjective:
        normalized_steps = _strip_history_from_steps(normalized_steps)
    if len(normalized_steps) < 3:
        # Import topic-specific step generator
        from src.local_llm_client import _generate_topic_specific_steps
        normalized_steps = _generate_topic_specific_steps(concept)
    steps = normalized_steps

    frame_w, frame_h = 1000, 600
    image_w, image_h = 680, 340
    image_x = (frame_w - image_w) // 2
    image_y = 98
    caption_x = image_x
    caption_y = image_y + image_h + 20
    title_y = 16

    title_box_h = 64
    # Adjust text box heights based on topic type
    if is_simulation_heavy:
        brief_box_h = 54  # Less text for simulation
        detail_box_h = 90
        max_caption_words = 8
    else:
        brief_box_h = 74  # More text for context
        detail_box_h = 120
        max_caption_words = 14

    # --------------------------------
    # Title
    # --------------------------------

    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": title,
        "x": image_x,
        "y": title_y,
        "font_scale": 0.95,
        "boxed": True,
        "box_width": image_w,
        "box_height": title_box_h,
        "max_lines": 1
    })

    hero_image_path = _create_visual_card(
        images_dir,
        concept,
        f"{title}",
        f"Concept overview: {title}",
        0
    )

    visual_elements.append({
        "id": "hero_image",
        "type": "image",
        "path": hero_image_path,
        "x": image_x,
        "y": image_y,
        "width": image_w,
        "height": image_h,
        "description": title
    })

    visual_elements.append({
        "id": "hero_caption",
        "type": "text",
        "description": _short_caption(title, max_words=10),
        "x": caption_x,
        "y": caption_y,
        "font_scale": 0.8,
        "boxed": True,
        "box_width": image_w,
        "box_height": brief_box_h,
        "max_lines": 1
    })

    # ============================================
    # SIMULATION ELEMENTS (for simulation-heavy topics)
    # ============================================

    if is_simulation_heavy:
        sim_category = topic_analysis.get("category", "general")

        # Add simulation-specific visual elements based on category
        if sim_category == "physics":
            # Add trajectory/motion indicators
            visual_elements.append({
                "id": "sim_indicator",
                "type": "text",
                "description": "▶ SIMULATION",
                "x": image_x + image_w - 140,
                "y": title_y + 8,
                "font_scale": 0.6,
                "color": (100, 220, 180)
            })
        elif sim_category == "algorithm":
            visual_elements.append({
                "id": "sim_indicator",
                "type": "text",
                "description": "⚙ ALGORITHM",
                "x": image_x + image_w - 140,
                "y": title_y + 8,
                "font_scale": 0.6,
                "color": (180, 200, 255)
            })
        elif sim_category == "math_process":
            visual_elements.append({
                "id": "sim_indicator",
                "type": "text",
                "description": "∑ CALCULATION",
                "x": image_x + image_w - 150,
                "y": title_y + 8,
                "font_scale": 0.6,
                "color": (255, 220, 140)
            })
        elif sim_category in {"chemistry", "biology_process"}:
            visual_elements.append({
                "id": "sim_indicator",
                "type": "text",
                "description": "🔬 PROCESS",
                "x": image_x + image_w - 120,
                "y": title_y + 8,
                "font_scale": 0.6,
                "color": (140, 255, 180)
            })

        # Add step progress indicator for simulations
        for i in range(min(len(steps), 5)):
            visual_elements.append({
                "id": f"step_dot_{i}",
                "type": "circle",
                "x": image_x + 30 + i * 25,
                "y": image_y + image_h - 20,
                "radius": 8,
                "color": (80, 160, 220) if i == 0 else (60, 80, 100)
            })

    count = len(steps)

    # ============================================
    # CATEGORY-BASED LAYOUTS
    # ============================================

    # PROCESS → Horizontal Flow
    if category == "process":

        for i in range(count):
            step_text = steps[i] if i < len(steps) else f"Step {i+1}"
            node_image = _create_visual_card(
                images_dir,
                concept,
                f"Process Step {i+1}",
                step_text,
                i + 1
            )
            visual_elements.append({
                "id": f"node_{i}",
                "type": "image",
                "path": node_image,
                "x": 110 + i * 220,
                "y": 220,
                "width": 200,
                "height": 120
            })

        animation_sequence.append({
            "elements": ["title", "hero_image", "hero_caption"],
            "duration": 4
        })

    # HIERARCHY → Vertical Stack
    elif category == "hierarchy":

        for i in range(count):
            step_text = steps[i] if i < len(steps) else f"Level {i+1}"
            node_image = _create_visual_card(
                images_dir,
                concept,
                f"Hierarchy Level {i+1}",
                step_text,
                i + 1
            )
            visual_elements.append({
                "id": f"node_{i}",
                "type": "image",
                "path": node_image,
                "x": 350,
                "y": 120 + i * 135,
                "width": 300,
                "height": 110
            })

        animation_sequence.append({
            "elements": ["title", "hero_image", "hero_caption"],
            "duration": 4
        })

    # STRUCTURE → Grid Layout
    elif category == "structure":

        size = int(math.ceil(math.sqrt(count)))

        for i in range(count):
            row = i // size
            col = i % size

            step_text = steps[i] if i < len(steps) else f"Part {i+1}"
            node_image = _create_visual_card(
                images_dir,
                concept,
                f"Structure Part {i+1}",
                step_text,
                i + 1
            )

            visual_elements.append({
                "id": f"node_{i}",
                "type": "image",
                "path": node_image,
                "x": 180 + col * 260,
                "y": 140 + row * 170,
                "width": 220,
                "height": 140
            })

        animation_sequence.append({
            "elements": ["title", "hero_image", "hero_caption"],
            "duration": 4
        })

    # SYSTEM → Central Hub with Satellites
    elif category == "system":

        visual_elements.append({
            "id": "central",
            "type": "image",
            "path": hero_image_path,
            "x": 500,
            "y": 300,
            "width": 220,
            "height": 140
        })

        radius = 200

        for i in range(count):
            angle = (2 * math.pi / max(count, 1)) * i
            x = 500 + radius * math.cos(angle)
            y = 300 + radius * math.sin(angle)

            step_text = steps[i] if i < len(steps) else f"Node {i+1}"
            node_image = _create_visual_card(
                images_dir,
                concept,
                f"System Node {i+1}",
                step_text,
                i + 1
            )

            visual_elements.append({
                "id": f"node_{i}",
                "type": "image",
                "path": node_image,
                "x": int(x - 90),
                "y": int(y - 55),
                "width": 180,
                "height": 110
            })

        animation_sequence.append({
            "elements": ["title", "hero_image", "central", "hero_caption"],
            "duration": 4
        })

    # ABSTRACT → Minimal Focus Layout
    else:
        animation_sequence.append({
            "elements": ["title", "hero_image", "hero_caption"],
            "duration": 4
        })

    # --------------------------------
    # Step Explanation Scenes
    # --------------------------------

    for i, step in enumerate(steps):

        step_id = f"text_step_{i}"
        step_brief_id = f"text_step_brief_{i}"
        step_image_id = f"image_step_{i}"
        step_image_path = _create_visual_card(
            images_dir,
            concept,
            f"{title} · Step {i+1}",
            step,
            i + 20
        )

        visual_elements.append({
            "id": step_image_id,
            "type": "image",
            "path": step_image_path,
            "x": image_x,
            "y": image_y,
            "width": image_w,
            "height": image_h,
            "description": step
        })

        visual_elements.append({
            "id": step_id,
            "type": "text",
            "description": _detail_caption(step),
            "x": caption_x,
            "y": caption_y,
            "font_scale": 0.8,
            "boxed": True,
            "box_width": image_w,
            "box_height": detail_box_h,
            "max_lines": 3
        })

        visual_elements.append({
            "id": step_brief_id,
            "type": "text",
            "description": _short_caption(step, max_words=max_caption_words),
            "x": caption_x,
            "y": caption_y,
            "font_scale": 0.8,
            "boxed": True,
            "box_width": image_w,
            "box_height": brief_box_h,
            "max_lines": 1
        })

        # Animation sequencing based on topic type
        if is_simulation_heavy:
            # Simulation-heavy: image-first with step progression, faster pacing
            animation_sequence.append({
                "elements": ["title", step_image_id, step_brief_id],
                "duration": 2.5,
                "transition": "slide"
            })
            animation_sequence.append({
                "elements": ["title", step_image_id, step_id],
                "duration": 3.0,
                "transition": "fade"
            })
        elif is_subjective:
            # Context-heavy subjective: text-first then image, slower pacing
            animation_sequence.append({
                "elements": ["title", "hero_image", step_id],
                "duration": 3.5,
                "transition": "fade"
            })
            animation_sequence.append({
                "elements": ["title", step_image_id, step_brief_id],
                "duration": 3.0,
                "transition": "fade"
            })
        else:
            # Context-heavy objective: balanced approach
            animation_sequence.append({
                "elements": ["title", step_image_id, step_brief_id],
                "duration": 3.2,
                "transition": "fade"
            })
            animation_sequence.append({
                "elements": ["title", step_image_id, step_id],
                "duration": 2.8,
                "transition": "fade"
            })

    # Detect theme for background styling
    detected_theme = _detect_theme(concept, title)
    theme_colors = _theme_colors(detected_theme)

    # Add topic analysis metadata to plan
    return {
        "visual_elements": visual_elements,
        "animation_sequence": animation_sequence,
        "topic_analysis": topic_analysis,
        "theme": detected_theme,
        "theme_colors": theme_colors
    }