# src/animator.py

"""
High-level orchestrator:
- Generates multiple plans (multi-topic support)
- Renders each scene separately
- Stitches them into one final video
- Saves unique final output (no overwrite)
"""

from typing import Tuple, List, Dict, Any
import os
import time
import hashlib
from moviepy.editor import VideoFileClip, concatenate_videoclips

from .planner import SimplePlanner
from .generator import SimpleGenerator
from .renderer import MoviePyRenderer


class EducationalAnimator:

    def __init__(self):
        self.planner = SimplePlanner()
        self.generator = SimpleGenerator()
        self.renderer = MoviePyRenderer()
        os.makedirs("outputs", exist_ok=True)

    def generate(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:

        # --------------------------------------------------
        # 1️⃣ Generate Plans (Multi-topic)
        # --------------------------------------------------
        plans = self.planner.generate_plans(text)

        rendered_videos = []

        # --------------------------------------------------
        # 2️⃣ Render Each Scene Separately
        # --------------------------------------------------
        for idx, plan in enumerate(plans):

            plan = self.generator.normalize_plan(plan)

            scene_filename = os.path.join(
                "outputs",
                f"scene_{idx}_{abs(hash(text)) % 100000}.mp4"
            )

            video_path = self.renderer.render(
                plan,
                output_filename=scene_filename
            )

            rendered_videos.append(video_path)

        # --------------------------------------------------
        # 3️⃣ Stitch Scenes Together
        # --------------------------------------------------
        clips = [VideoFileClip(v) for v in rendered_videos]

        final_clip = concatenate_videoclips(clips)

        # --------------------------------------------------
        # 4️⃣ Unique Final Output Name (No Overwrite)
        # --------------------------------------------------
        hash_id = abs(hash(text)) % 100000
        timestamp = int(time.time())

        final_path = os.path.join(
            "outputs",
            f"final_{hash_id}_{timestamp}.mp4"
        )

        final_clip.write_videofile(
            final_path,
            fps=24,
            codec="libx264",
            audio=False
        )

        # Close clips to release memory
        for clip in clips:
            clip.close()

        final_clip.close()

        return final_path, plans