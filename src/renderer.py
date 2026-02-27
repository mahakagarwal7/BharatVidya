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

        def draw_wrapped_text(frame, text, x, y, scale=0.8):

            words = str(text).split()
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
                    (int(x), int(y + i * line_height)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    (255, 255, 255),
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
                (0, 200, 255),
                3
            )

        def draw_circle(frame, elem):
            try:
                x = int(elem.get("x", 500))
                y = int(elem.get("y", 300))
                r = int(elem.get("radius", 40))
            except:
                x, y, r = 500, 300, 40

            cv2.circle(
                frame,
                (x, y),
                r,
                (0, 255, 150),
                3
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
                (0, 255, 255),
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
            scene_start = 0
            scene_end = 0

            for start, end, step in timeline:
                if start <= t < end:
                    visible = step.get("elements", [])
                    scene_start = start
                    scene_end = end
                    break

            overlay = frame.copy()

            # -------------------------------
            # Render visible elements
            # -------------------------------

            for elem in elements:

                if elem.get("id") not in visible:
                    continue

                etype = elem.get("type")

                if etype == "text":
                    draw_wrapped_text(
                        overlay,
                        elem.get("description", ""),
                        elem.get("x", margin_left),
                        elem.get("y", 150)
                    )

                elif etype == "rectangle":
                    draw_rectangle(overlay, elem)

                elif etype == "circle":
                    draw_circle(overlay, elem)

                elif etype == "arrow":
                    draw_arrow(overlay, elem)

                elif etype == "grid":
                    draw_grid(overlay, elem)

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

        os.makedirs(os.path.dirname(output_filename), exist_ok=True)

        clip.write_videofile(
            output_filename,
            fps=24,
            codec="libx264",
            audio=False,
            preset="ultrafast"
        )

        return output_filename