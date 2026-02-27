# src/renderer.py

from moviepy.editor import VideoClip
import numpy as np
import cv2
import os
import math


class MoviePyRenderer:

    def render(self, plan: dict, output_filename: str) -> str:

        elements = plan.get("visual_elements", [])
        steps = plan.get("animation_sequence", [])

        # Get theme information for styled background
        theme = plan.get("theme", "generic")
        theme_colors = plan.get("theme_colors", ((24, 62, 116), (50, 108, 164)))
        topic_analysis = plan.get("topic_analysis", {})
        topic_type = topic_analysis.get("topic_type", "context")

        width, height = 1000, 600
        margin_left = 120
        margin_right = 120
        max_text_width = width - margin_left - margin_right
        image_cache = {}

        total_duration = sum(s.get("duration", 2) for s in steps)

        # -------------------------------
        # Build timeline
        # -------------------------------

        timeline = []
        current = 0
        for step in steps:
            d = step.get("duration", 2)
            timeline.append((current, current + d, step))
            current += d

        # ==========================================================
        # TEXT WRAPPING
        # ==========================================================

        def draw_wrapped_text(frame, text, x, y, scale=0.8, box=False, box_width=None, max_lines=None, box_height=None, color=None):

            words = str(text).split()
            lines = []
            current_line = ""
            effective_max_width = int(box_width) if box_width else max_text_width
            effective_max_width = max(120, effective_max_width)
            text_pad_x = 14

            # Use custom color or default white
            if color and isinstance(color, (list, tuple)) and len(color) >= 3:
                text_color = (int(color[2]), int(color[1]), int(color[0]))  # RGB to BGR
            else:
                text_color = (255, 255, 255)

            if box and box_width:
                effective_max_width = max(120, effective_max_width - (text_pad_x * 2))

            for word in words:
                test_line = current_line + " " + word if current_line else word

                (w, _), _ = cv2.getTextSize(
                    test_line,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    2
                )

                if w <= effective_max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            if max_lines is not None:
                try:
                    max_lines = int(max_lines)
                except:
                    max_lines = None

            if max_lines is not None and max_lines > 0 and len(lines) > max_lines:
                lines = lines[:max_lines]
                if lines:
                    last = lines[-1].rstrip()
                    if not last.endswith("..."):
                        lines[-1] = (last[:-3] + "...") if len(last) > 3 else (last + "...")

            line_height = max(24, int(26 + scale * 10))

            if box_height is not None:
                try:
                    box_height = int(box_height)
                except:
                    box_height = None

            if box_height is not None and box_height > 0:
                usable_h = max(1, box_height - 32)
                max_fit = max(1, usable_h // line_height)
                if len(lines) > max_fit:
                    lines = lines[:max_fit]
                    last = lines[-1].rstrip()
                    if not last.endswith("..."):
                        lines[-1] = (last[:-3] + "...") if len(last) > 3 else (last + "...")

            if box and lines:
                max_line_w = 0
                for line in lines:
                    (line_w, _), _ = cv2.getTextSize(
                        line,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        scale,
                        2
                    )
                    max_line_w = max(max_line_w, line_w)

                pad_x = text_pad_x
                pad_y_top = 18
                pad_y_bottom = 14
                x0 = int(x - pad_x)
                y0 = int(y - pad_y_top)
                x1 = int(x + max_line_w + pad_x)
                y1 = int(y + len(lines) * line_height + pad_y_bottom)

                if box_width:
                    x0 = int(x)
                    x1 = int(x + int(box_width))

                if box_height is not None and box_height > 0:
                    y0 = int(y)
                    y1 = int(y + box_height)

                x0 = max(0, x0)
                y0 = max(0, y0)
                x1 = min(width - 1, x1)
                y1 = min(height - 1, y1)

                cv2.rectangle(frame, (x0, y0), (x1, y1), (14, 20, 34), -1)
                cv2.rectangle(frame, (x0, y0), (x1, y1), (216, 230, 246), 1)

                if box_width:
                    x = x0 + text_pad_x

                if box_height is not None and box_height > 0:
                    y = y0 + 18

            for i, line in enumerate(lines):
                cv2.putText(
                    frame,
                    line,
                    (int(x), int(y + i * line_height)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    text_color,
                    2,
                    cv2.LINE_AA
                )

            return y + len(lines) * line_height

        # ==========================================================
        # SAFE PRIMITIVES
        # ==========================================================

        def draw_rectangle(frame, elem):
            try:
                x = int(elem.get("x", 300))
                y = int(elem.get("y", 250))
                w = int(elem.get("width", 200))
                h = int(elem.get("height", 120))
            except:
                x, y, w, h = 300, 250, 200, 120

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (160, 182, 205),
                2
            )

        def draw_circle(frame, elem):
            try:
                x = int(elem.get("x", 500))
                y = int(elem.get("y", 300))
                r = int(elem.get("radius", 40))
            except:
                x, y, r = 500, 300, 40

            # Support custom color from element
            color = elem.get("color", (152, 201, 184))
            if isinstance(color, (list, tuple)) and len(color) >= 3:
                color = (int(color[2]), int(color[1]), int(color[0]))  # RGB to BGR
            else:
                color = (152, 201, 184)

            # Use fill or outline based on element config
            fill = elem.get("fill", True)
            thickness = -1 if fill else 2

            cv2.circle(
                frame,
                (x, y),
                r,
                color,
                thickness
            )

        def draw_arrow(frame, elem):
            start = elem.get("start", [300, 300])
            end = elem.get("end", [600, 300])

            try:
                sx, sy = int(start[0]), int(start[1])
                ex, ey = int(end[0]), int(end[1])
            except:
                sx, sy = 300, 300
                ex, ey = 600, 300

            cv2.arrowedLine(
                frame,
                (sx, sy),
                (ex, ey),
                (174, 202, 218),
                2
            )

        def draw_grid(frame, elem):

            values = elem.get("values", [])

            # ----------------------------
            # Sanitize rows
            # ----------------------------
            rows = elem.get("rows")

            if isinstance(rows, list):
                rows = rows[0] if rows else 0

            try:
                rows = int(rows)
            except:
                rows = len(values)

            # ----------------------------
            # Sanitize cols
            # ----------------------------
            cols = elem.get("cols")

            if isinstance(cols, list):
                cols = cols[0] if cols else 0

            try:
                cols = int(cols)
            except:
                if values and isinstance(values[0], list):
                    cols = len(values[0])
                else:
                    cols = 0

            # ----------------------------
            # Position defaults
            # ----------------------------
            try:
                x0 = int(elem.get("x", 200))
                y0 = int(elem.get("y", 200))
            except:
                x0, y0 = 200, 200

            cell = 60

            for i in range(rows):
                for j in range(cols):

                    x = x0 + j * cell
                    y = y0 + i * cell

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + cell, y + cell),
                        (255, 255, 255),
                        2
                    )

                    if (
                        values
                        and i < len(values)
                        and isinstance(values[i], list)
                        and j < len(values[i])
                    ):
                        cv2.putText(
                            frame,
                            str(values[i][j]),
                            (x + 18, y + 38),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 255, 255),
                            2
                        )

        def draw_image(frame, elem):
            source = (
                elem.get("path")
                or elem.get("src")
                or elem.get("url")
                or ""
            )

            try:
                x = int(elem.get("x", 200))
                y = int(elem.get("y", 180))
            except:
                x, y = 200, 180

            w = elem.get("width")
            h = elem.get("height")

            image = None
            if source and os.path.exists(source):
                if source not in image_cache:
                    image_cache[source] = cv2.imread(source, cv2.IMREAD_COLOR)
                image = image_cache.get(source)

            if image is None:
                default_w = int(w) if w else 320
                default_h = int(h) if h else 180
                default_w = max(40, default_w)
                default_h = max(30, default_h)
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + default_w, y + default_h),
                    (180, 180, 180),
                    2
                )
                cv2.putText(
                    frame,
                    "Image",
                    (x + 10, y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (220, 220, 220),
                    2,
                    cv2.LINE_AA
                )
                return

            src_h, src_w = image.shape[:2]
            target_w = int(w) if w else src_w
            target_h = int(h) if h else src_h
            target_w = max(1, target_w)
            target_h = max(1, target_h)

            resized = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_AREA)

            x0 = max(0, x)
            y0 = max(0, y)
            x1 = min(width, x + target_w)
            y1 = min(height, y + target_h)

            if x0 >= x1 or y0 >= y1:
                return

            src_x0 = x0 - x
            src_y0 = y0 - y
            src_x1 = src_x0 + (x1 - x0)
            src_y1 = src_y0 + (y1 - y0)

            frame[y0:y1, x0:x1] = resized[src_y0:src_y1, src_x0:src_x1]

        def draw_sine_wave(frame, elem):
            try:
                x = int(elem.get("x", 140))
                y = int(elem.get("y", 320))
                w = int(elem.get("width", 720))
                h = int(elem.get("height", 220))
                amplitude = float(elem.get("amplitude", 70))
                cycles = float(elem.get("cycles", 2.0))
            except:
                x, y, w, h = 140, 320, 720, 220
                amplitude = 70.0
                cycles = 2.0

            x_axis_y = y
            cv2.line(frame, (x, x_axis_y), (x + w, x_axis_y), (180, 180, 180), 1)
            cv2.line(frame, (x, y - h // 2), (x, y + h // 2), (180, 180, 180), 1)

            points = []
            for px in range(w + 1):
                t_norm = px / max(w, 1)
                angle = 2 * math.pi * cycles * t_norm
                py = int(x_axis_y - amplitude * math.sin(angle))
                points.append((x + px, py))

            if len(points) > 1:
                cv2.polylines(frame, [np.array(points, dtype=np.int32)], False, (0, 255, 255), 2)

        def draw_projectile(frame, elem, t, scene_start, scene_end):
            try:
                x0 = int(elem.get("x", 160))
                y0 = int(elem.get("y", 460))
                v0 = float(elem.get("v0", 12.0))
                angle_deg = float(elem.get("angle_degrees", 45.0))
                g = float(elem.get("g", 9.81))
                x_scale = float(elem.get("x_scale", 18.0))
                y_scale = float(elem.get("y_scale", 12.0))
            except:
                x0, y0, v0, angle_deg, g = 160, 460, 12.0, 45.0, 9.81
                x_scale, y_scale = 18.0, 12.0

            theta = math.radians(angle_deg)
            vx = v0 * math.cos(theta)
            vy = v0 * math.sin(theta)
            flight_t = (2 * vy / g) if g > 0 else 2.0
            flight_t = max(0.5, flight_t)

            curve_points = []
            samples = 120
            for i in range(samples + 1):
                tp = flight_t * (i / samples)
                world_x = vx * tp
                world_y = vy * tp - 0.5 * g * tp * tp
                sx = int(x0 + world_x * x_scale)
                sy = int(y0 - world_y * y_scale)
                curve_points.append((sx, sy))

            if len(curve_points) > 1:
                cv2.polylines(frame, [np.array(curve_points, dtype=np.int32)], False, (0, 220, 255), 2)

            scene_duration = max(1e-6, scene_end - scene_start)
            local_progress = min(1.0, max(0.0, (t - scene_start) / scene_duration))
            ball_t = flight_t * local_progress
            ball_x = int(x0 + (vx * ball_t) * x_scale)
            ball_y = int(y0 - (vy * ball_t - 0.5 * g * ball_t * ball_t) * y_scale)
            cv2.circle(frame, (ball_x, ball_y), 8, (0, 255, 255), -1)

        def draw_quadratic_graph(frame, elem):
            try:
                a = float(elem.get("a", 1.0))
                b = float(elem.get("b", 0.0))
                c = float(elem.get("c", 0.0))
                center_x = int(elem.get("x", 500))
                center_y = int(elem.get("y", 320))
                x_scale = float(elem.get("x_scale", 70.0))
                y_scale = float(elem.get("y_scale", 45.0))
            except:
                a, b, c = 1.0, 0.0, 0.0
                center_x, center_y = 500, 320
                x_scale, y_scale = 70.0, 45.0

            graph_w = int(elem.get("width", 700))
            graph_h = int(elem.get("height", 340))
            left = center_x - graph_w // 2
            right = center_x + graph_w // 2
            top = center_y - graph_h // 2
            bottom = center_y + graph_h // 2

            cv2.rectangle(frame, (left, top), (right, bottom), (80, 80, 80), 1)
            cv2.line(frame, (left, center_y), (right, center_y), (170, 170, 170), 1)
            cv2.line(frame, (center_x, top), (center_x, bottom), (170, 170, 170), 1)

            points = []
            x_min = -graph_w / (2 * x_scale)
            x_max = graph_w / (2 * x_scale)
            samples = 220
            for i in range(samples + 1):
                x_val = x_min + (x_max - x_min) * (i / samples)
                y_val = a * x_val * x_val + b * x_val + c
                sx = int(center_x + x_val * x_scale)
                sy = int(center_y - y_val * y_scale)
                points.append((sx, sy))

            if len(points) > 1:
                cv2.polylines(frame, [np.array(points, dtype=np.int32)], False, (255, 200, 0), 2)

            vertex = elem.get("vertex")
            if isinstance(vertex, list) and len(vertex) >= 2:
                try:
                    vx, vy = float(vertex[0]), float(vertex[1])
                    svx = int(center_x + vx * x_scale)
                    svy = int(center_y - vy * y_scale)
                    cv2.circle(frame, (svx, svy), 5, (0, 255, 0), -1)
                except:
                    pass

            roots = elem.get("roots", [])
            if isinstance(roots, list):
                for root in roots[:2]:
                    try:
                        rx = float(root)
                        srx = int(center_x + rx * x_scale)
                        sry = center_y
                        cv2.circle(frame, (srx, sry), 4, (0, 180, 255), -1)
                    except:
                        continue

        # ==========================================================
        # THEME-AWARE BACKGROUND COLORS
        # ==========================================================

        # Define background gradients based on theme
        theme_backgrounds = {
            "matrix_multiplication": ((15, 28, 45), (28, 52, 78)),
            "photosynthesis": ((12, 32, 18), (24, 58, 34)),
            "eigen": ((18, 26, 48), (32, 48, 82)),
            "projectile": ((14, 28, 48), (28, 52, 82)),
            "quadratic": ((32, 18, 48), (58, 34, 82)),
            "sine": ((12, 32, 58), (24, 58, 98)),
            "binary_search": ((38, 22, 14), (68, 42, 28)),
            "bubble_sort": ((36, 26, 10), (68, 50, 22)),
            "determinant": ((18, 30, 45), (34, 56, 78)),
            "linear_equation": ((16, 38, 32), (32, 68, 56)),
            "probability": ((42, 24, 34), (78, 48, 62)),
            "generic": ((14, 32, 58), (28, 56, 92)),
        }

        # Context-heavy topics use lighter backgrounds
        context_backgrounds = {
            "history": ((28, 22, 18), (52, 42, 34)),
            "philosophy": ((24, 22, 32), (48, 44, 62)),
            "literature": ((32, 26, 22), (62, 52, 44)),
            "social": ((22, 28, 38), (44, 54, 72)),
            "abstract": ((24, 28, 38), (48, 54, 72)),
            "general": ((22, 32, 48), (44, 62, 88)),
        }

        # Get background colors
        if topic_type == "context":
            topic_category = topic_analysis.get("category", "general")
            bg_start, bg_end = context_backgrounds.get(topic_category, context_backgrounds["general"])
        else:
            bg_start, bg_end = theme_backgrounds.get(theme, theme_backgrounds["generic"])

        # ==========================================================
        # FRAME GENERATOR
        # ==========================================================

        def make_frame(t):

            frame = np.zeros((height, width, 3), dtype=np.uint8)

            # Theme-aware gradient background
            for y_pos in range(height):
                ratio = y_pos / height
                b = int(bg_start[0] + (bg_end[0] - bg_start[0]) * ratio)
                g = int(bg_start[1] + (bg_end[1] - bg_start[1]) * ratio)
                r = int(bg_start[2] + (bg_end[2] - bg_start[2]) * ratio)
                frame[y_pos, :] = (b, g, r)

            # Add subtle decorative elements based on theme
            if topic_type == "simulation":
                # Grid pattern for simulation topics
                grid_color = (bg_end[0] + 15, bg_end[1] + 15, bg_end[2] + 15)
                for gx in range(0, width, 50):
                    cv2.line(frame, (gx, 0), (gx, height), grid_color, 1)
                for gy in range(0, height, 50):
                    cv2.line(frame, (0, gy), (width, gy), grid_color, 1)
            else:
                # Subtle corner decorations for context topics
                corner_color = (bg_end[0] + 20, bg_end[1] + 20, bg_end[2] + 20)
                cv2.line(frame, (20, 20), (80, 20), corner_color, 2)
                cv2.line(frame, (20, 20), (20, 80), corner_color, 2)
                cv2.line(frame, (width - 20, 20), (width - 80, 20), corner_color, 2)
                cv2.line(frame, (width - 20, 20), (width - 20, 80), corner_color, 2)
                cv2.line(frame, (20, height - 20), (80, height - 20), corner_color, 2)
                cv2.line(frame, (20, height - 20), (20, height - 80), corner_color, 2)
                cv2.line(frame, (width - 20, height - 20), (width - 80, height - 20), corner_color, 2)
                cv2.line(frame, (width - 20, height - 20), (width - 20, height - 80), corner_color, 2)

            visible = []
            scene_start = 0
            scene_end = 0

            for start, end, step in timeline:
                if start <= t < end:
                    visible = step.get("elements", [])
                    scene_start = start
                    scene_end = end
                    break

            overlay = frame.copy()

            def render_priority(elem):
                etype = elem.get("type")
                if etype == "text":
                    return 100
                if etype == "arrow":
                    return 70
                return 10

            # -------------------------------
            # Render visible elements
            # -------------------------------

            visible_elements = [
                elem for elem in elements
                if elem.get("id") in visible
            ]
            visible_elements.sort(key=render_priority)

            for elem in visible_elements:

                etype = elem.get("type")

                if etype == "text":
                    text_scale = float(elem.get("font_scale", 0.8))
                    text_boxed = bool(elem.get("boxed", False))
                    text_box_width = elem.get("box_width")
                    text_max_lines = elem.get("max_lines")
                    text_box_height = elem.get("box_height")
                    text_color = elem.get("color")
                    draw_wrapped_text(
                        overlay,
                        elem.get("description", ""),
                        elem.get("x", margin_left),
                        elem.get("y", 150),
                        scale=text_scale,
                        box=text_boxed,
                        box_width=text_box_width,
                        max_lines=text_max_lines,
                        box_height=text_box_height,
                        color=text_color
                    )

                elif etype == "rectangle":
                    draw_rectangle(overlay, elem)

                elif etype == "circle":
                    draw_circle(overlay, elem)

                elif etype == "arrow":
                    draw_arrow(overlay, elem)

                elif etype == "grid":
                    draw_grid(overlay, elem)

                elif etype == "image":
                    draw_image(overlay, elem)

                elif etype == "sine_wave":
                    draw_sine_wave(overlay, elem)

                elif etype == "projectile":
                    draw_projectile(overlay, elem, t, scene_start, scene_end)

                elif etype == "quadratic_graph":
                    draw_quadratic_graph(overlay, elem)

            # -------------------------------
            # Fade transition
            # -------------------------------

            fade_duration = 0.7
            alpha = 1.0

            if t - scene_start < fade_duration:
                alpha = (t - scene_start) / fade_duration
            elif scene_end - t < fade_duration:
                alpha = (scene_end - t) / fade_duration

            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ==========================================================
        # Export Video
        # ==========================================================

        clip = VideoClip(make_frame, duration=total_duration)

        output_dir = os.path.dirname(output_filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        clip.write_videofile(
            output_filename,
            fps=24,
            codec="libx264",
            audio=False,
            preset="ultrafast"
        )

        return output_filename