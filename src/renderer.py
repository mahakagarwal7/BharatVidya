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

        width, height = 1000, 600
        margin_left = 120
        margin_right = 120
        max_text_width = width - margin_left - margin_right

        total_duration = sum(s.get("duration", 2) for s in steps)

        # Build timeline
        timeline = []
        current = 0
        for step in steps:
            d = step.get("duration", 2)
            timeline.append((current, current + d, step))
            current += d

        # ==========================================================
        # TEXT WRAPPING
        # ==========================================================

        def draw_wrapped_text(frame, text, x, y, scale=0.8):

            words = text.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word

                (w, _), _ = cv2.getTextSize(
                    test_line,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    2
                )

                if w <= max_text_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            line_height = 32

            for i, line in enumerate(lines):
                cv2.putText(
                    frame,
                    line,
                    (x, y + i * line_height),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

            return y + len(lines) * line_height

        # ==========================================================
        # PRIMITIVES
        # ==========================================================

        def draw_rectangle(frame, elem):
            x, y = elem["x"], elem["y"]
            w, h = elem["width"], elem["height"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 255), 3)

        def draw_circle(frame, elem):
            cv2.circle(frame, (elem["x"], elem["y"]),
                       elem["radius"], (0, 255, 150), 3)

        def draw_arrow(frame, elem):
            cv2.arrowedLine(frame,
                            tuple(elem["start"]),
                            tuple(elem["end"]),
                            (0, 255, 255), 2)

        def draw_grid(frame, elem):
            rows = elem["rows"]
            cols = elem["cols"]
            x0, y0 = elem["x"], elem["y"]
            cell = 60
            values = elem.get("values", [])

            for i in range(rows):
                for j in range(cols):
                    x = x0 + j * cell
                    y = y0 + i * cell
                    cv2.rectangle(frame, (x, y),
                                  (x + cell, y + cell),
                                  (255, 255, 255), 2)

                    if values:
                        cv2.putText(
                            frame,
                            str(values[i][j]),
                            (x + 18, y + 38),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 255, 255),
                            2
                        )

        # ==========================================================
        # QUADRATIC GRAPH
        # ==========================================================

        def draw_quadratic_graph(frame, elem, t):

            a = elem["a"]
            b = elem["b"]
            c = elem["c"]

            width = frame.shape[1]
            height = frame.shape[0]

            x_scale = 80
            y_scale = 25

            progress = min(1, t / 4)
            max_x = int(width * progress)

            # Axes
            cv2.line(frame, (0, height//2),
                     (width, height//2), (100, 100, 100), 1)
            cv2.line(frame, (width//2, 0),
                     (width//2, height), (100, 100, 100), 1)

            for px in range(max_x):
                x = (px - width/2) / x_scale
                y = a*x*x + b*x + c
                py = int(height/2 - y*y_scale)

                if 0 <= py < height:
                    frame[py:py+2, px] = (255, 200, 50)

            # Vertex
            if t > 3:
                vx = int(width/2 + elem["vertex"][0]*x_scale)
                vy = int(height/2 - elem["vertex"][1]*y_scale)
                cv2.circle(frame, (vx, vy), 6, (0,255,255), -1)

            # Roots
            if t > 3 and elem["roots"]:
                for r in elem["roots"]:
                    rx = int(width/2 + r*x_scale)
                    cv2.circle(frame, (rx, height//2), 6, (0,255,0), -1)

        # ==========================================================
        # FRAME GENERATOR
        # ==========================================================

        def make_frame(t):

            frame = np.zeros((height, width, 3), dtype=np.uint8)

            # Gradient background
            for y in range(height):
                ratio = y / height
                frame[y, :] = (
                    int(20 + 40 * ratio),
                    int(60 + 80 * ratio),
                    int(120 + 100 * ratio)
                )

            visible = []
            scene_index = 0
            scene_start = 0
            scene_end = 0

            for idx, (start, end, step) in enumerate(timeline):
                if start <= t < end:
                    visible = step.get("elements", [])
                    scene_index = idx
                    scene_start = start
                    scene_end = end
                    break

            overlay = frame.copy()

            # ==================================================
            # SCENE 1 (Visual)
            # ==================================================

            if scene_index == 0:

                for elem in elements:
                    if elem["id"] not in visible:
                        continue

                    if elem["type"] == "quadratic_graph":
                        draw_quadratic_graph(overlay, elem, t)

                    elif elem["type"] == "circle" and elem["id"] == "flow_center":
                        # Rotating flow animation
                        center_x, center_y = 500, 300
                        radius = 130
                        for i in range(4):
                            angle = t * 1.5 + i * math.pi / 2
                            x = int(center_x + radius * math.cos(angle))
                            y = int(center_y + radius * math.sin(angle))
                            cv2.circle(overlay, (x, y),
                                       30, (0, 255, 255), 3)

                    elif elem["type"] == "rectangle":
                        draw_rectangle(overlay, elem)

                    elif elem["type"] == "grid":
                        draw_grid(overlay, elem)

                    elif elem["type"] == "arrow":
                        draw_arrow(overlay, elem)

                    elif elem["type"] == "text":
                        draw_wrapped_text(
                            overlay,
                            elem["description"],
                            margin_left,
                            elem["y"]
                        )

            # ==================================================
            # SCENE 2 (Explanation with Progressive Reveal)
            # ==================================================

            if scene_index == 1:

                y_cursor = 150

                # Title
                for elem in elements:
                    if elem["id"] == "title":
                        y_cursor = draw_wrapped_text(
                            overlay,
                            elem["description"],
                            margin_left,
                            y_cursor,
                            scale=1.0
                        )
                        y_cursor += 20

                bullet_delay = 2

                for elem in elements:
                    if elem["id"].startswith("text_"):
                        index = int(elem["id"].split("_")[1])
                        if (t - scene_start) > index * bullet_delay:
                            y_cursor = draw_wrapped_text(
                                overlay,
                                "• " + elem["description"],
                                margin_left,
                                y_cursor
                            )
                            y_cursor += 15

            # ==================================================
            # FADE TRANSITION
            # ==================================================

            fade_duration = 0.7
            alpha = 1.0

            if t - scene_start < fade_duration:
                alpha = (t - scene_start) / fade_duration
            elif scene_end - t < fade_duration:
                alpha = (scene_end - t) / fade_duration

            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ==========================================================
        # VIDEO EXPORT
        # ==========================================================

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