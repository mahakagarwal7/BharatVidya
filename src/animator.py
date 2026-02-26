# src/animator.py

"""
High-level orchestrator:
Uses planner + renderer to produce final video.
Hackathon stable version.
"""

from typing import Tuple, Dict, Any
import os
from .planner import SimplePlanner
from .renderer import MoviePyRenderer


class EducationalAnimator:

    def __init__(self):
        self.planner = SimplePlanner()
        self.renderer = MoviePyRenderer()
        os.makedirs("outputs", exist_ok=True)

    def generate(self, text: str) -> Tuple[str, Dict[str, Any]]:

        # Step 1: Generate SINGLE plan
        plan = self.planner.plan_universal_scene(text)

        # Step 2: Render
        out_name = os.path.join(
            "outputs",
            f"animation_{abs(hash(text)) % 100000}.mp4"
        )

        try:
            video_path = self.renderer.render(
                plan,
                output_filename=out_name
            )
        except Exception as e:
            print("Renderer error:", e)
            video_path = None

        return video_path, plan