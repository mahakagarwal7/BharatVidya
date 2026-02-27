# src/animator.py

"""
High-level orchestrator:
Uses planner + renderer + narrator to produce final video with audio.
"""

from typing import Tuple, Dict, Any, Optional
import os
import uuid
from .planner import SimplePlanner
from .renderer import MoviePyRenderer
from .narrator import Narrator, generate_narration_for_plan


class EducationalAnimator:

    def __init__(self, enable_narration: bool = True, voice: str = "en-US-JennyNeural"):
        self.planner = SimplePlanner()
        self.renderer = MoviePyRenderer()
        self.enable_narration = enable_narration
        self.voice = voice
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("outputs/audio", exist_ok=True)

    def generate(
        self,
        text: str,
        with_narration: Optional[bool] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate educational video with optional audio narration.
        
        Args:
            text: The concept/topic to explain
            with_narration: Override default narration setting (None uses class default)
        
        Returns:
            Tuple of (video_path, plan_dict)
        """
        
        # Determine if we should generate narration
        use_narration = with_narration if with_narration is not None else self.enable_narration

        # Step 1: Generate visual plan
        plan = self.planner.plan_universal_scene(text)
        
        # Step 2: Generate narration if enabled
        narration = None
        session_id = str(uuid.uuid4())[:8]
        
        if use_narration:
            try:
                print("🎙️ Generating audio narration...")
                narration = generate_narration_for_plan(plan, session_id, self.voice)
                print(f"   Audio duration: {narration['total_duration']:.1f}s")
                print(f"   Steps: {len(narration['step_durations'])}")
            except Exception as e:
                print(f"⚠️ Narration failed: {e}")
                narration = None

        # Step 3: Render video (with audio if narration succeeded)
        out_name = os.path.join(
            "outputs",
            f"animation_{abs(hash(text)) % 100000}.mp4"
        )

        try:
            video_path = self.renderer.render(
                plan,
                output_filename=out_name,
                narration=narration
            )
            
            # Cleanup audio temp files if video succeeded
            if narration:
                narrator = Narrator()
                # Keep combined audio, cleanup individual step files
                # narrator.cleanup(session_id)  # Uncomment to auto-cleanup
                
        except Exception as e:
            print("Renderer error:", e)
            video_path = None

        return video_path, plan