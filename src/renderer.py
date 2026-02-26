# src/renderer.py

from moviepy.editor import VideoClip
import numpy as np
import os
import math
import cv2


class MoviePyRenderer:

    def render(self, plan: dict, output_filename: str) -> str:

        steps = plan.get("animation_sequence", [])
        elements = plan.get("visual_elements", [])

        width, height = 900, 550

        def draw_text(frame, text, x, y, scale=0.8, color=(255, 255, 255), thickness=2):
            cv2.putText(
                frame,
                str(text),
                (int(x), int(y)),
                cv2.FONT_HERSHEY_SIMPLEX,
                scale,
                color,
                thickness,
                cv2.LINE_AA
            )

        types = [e.get("type") for e in elements]

        # ==========================================================
        # QUADRATIC (Animated Equation + Graph)
        # ==========================================================
        if "parabola" in types:

            parabola = next(e for e in elements if e["type"] == "parabola")

            a = parabola.get("a", 1)
            b = parabola.get("b", 0)
            c = parabola.get("c", 0)

            equation_text = f"{a}x² + {b}x + {c} = 0"

            total_duration = 8
            discriminant = b*b - 4*a*c

            vertex_x = -b / (2*a) if a != 0 else 0
            vertex_y = a*vertex_x**2 + b*vertex_x + c

            roots = []
            if discriminant >= 0 and a != 0:
                r1 = (-b + math.sqrt(discriminant)) / (2*a)
                r2 = (-b - math.sqrt(discriminant)) / (2*a)
                roots = [r1, r2]

            def make_frame(t):

                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:] = (15, 18, 28)

                # Fade-in equation
                alpha = min(1, t / 2)
                eq_color = (
                    int(255 * alpha),
                    int(255 * alpha),
                    int(255 * alpha),
                )

                draw_text(frame, equation_text, width//2 - 220, 60, scale=1.0, color=eq_color, thickness=3)

                # Axes
                cv2.line(frame, (0, height//2), (width, height//2), (80, 80, 80), 1)
                cv2.line(frame, (width//2, 0), (width//2, height), (80, 80, 80), 1)

                x_scale = 80
                y_scale = 25

                progress = min(1, t / 4)
                max_x = int(width * progress)

                for px in range(max_x):
                    x = (px - width/2) / x_scale
                    y = a*x*x + b*x + c
                    py = int(height/2 - y*y_scale)
                    if 0 <= py < height:
                        frame[py:py+2, px] = (255, 150, 50)

                if t > 4:
                    vx = int(width/2 + vertex_x * x_scale)
                    vy = int(height/2 - vertex_y * y_scale)
                    if 0 <= vy < height and 0 <= vx < width:
                        cv2.circle(frame, (vx, vy), 6, (0, 255, 255), -1)
                        draw_text(frame, "Vertex", vx + 10, vy - 10, scale=0.6)

                if t > 5 and roots:
                    for r in roots:
                        rx = int(width/2 + r * x_scale)
                        ry = height//2
                        if 0 <= rx < width:
                            cv2.circle(frame, (rx, ry), 6, (0, 255, 0), -1)
                            draw_text(frame, round(r,2), rx - 15, ry + 25, scale=0.6)

                if t > 5 and discriminant < 0:
                    draw_text(frame, "No Real Roots", width//2 - 120, height - 40, scale=0.8)

                draw_text(frame, f"Discriminant = {round(discriminant,2)}", 20, height - 30, scale=0.6)

                return frame

        # ==========================================================
        # GENERIC LLM SLIDE MODE
        # ==========================================================
        elif "text" in types:

            total_duration = sum(s.get("duration", 2) for s in steps)
            total_duration = max(total_duration, 6)

            timeline = []
            current = 0
            for step in steps:
                d = step.get("duration", 2)
                timeline.append((current, current + d, step))
                current += d

            def make_frame(t):

                frame = np.zeros((height, width, 3), dtype=np.uint8)

                # Animated soft background
                for y in range(height):
                    shade = int(40 + 20 * math.sin(t + y/120))
                    shade = max(0, min(255, shade))
                    frame[y, :] = (shade, shade+10, shade+20)

                # Determine revealed elements
                revealed = []
                for start, end, step in timeline:
                    if t >= end:
                        for elem_id in step.get("elements", []):
                            if elem_id not in revealed:
                                revealed.append(elem_id)

                # Title
                title_elem = next((e for e in elements if e["id"] == "title"), None)
                if title_elem:
                    draw_text(frame, title_elem["description"], 80, 80, scale=1.2)

                # Bullet points
                y_offset = 150
                bullet_index = 0

                for elem_id in revealed:
                    if elem_id == "title":
                        continue

                    elem = next((e for e in elements if e["id"] == elem_id), None)
                    if elem:
                        text = f"- {elem['description']}"
                        draw_text(frame, text, 100, y_offset + bullet_index*50, scale=0.9)
                        bullet_index += 1

                return frame

        # ==========================================================
        # SAFE FALLBACK
        # ==========================================================
        else:

            total_duration = 5

            def make_frame(t):
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:] = (30, 30, 45)

                draw_text(frame, plan.get("title", "Educational Animation"), 20, 40, scale=1.0)

                radius = int(50 + 20 * math.sin(t*3))
                cx, cy = width//2, height//2

                for y in range(height):
                    for x in range(width):
                        if (x-cx)**2 + (y-cy)**2 <= radius**2:
                            frame[y, x] = (150, 200, 255)

                return frame

        clip = VideoClip(make_frame, duration=total_duration)

        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        clip.write_videofile(
            output_filename,
            fps=24,
            codec="libx264",
            audio=False,
            preset="ultrafast"
        )

        return output_filename