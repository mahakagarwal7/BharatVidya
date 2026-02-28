# src/animator.py

"""
High-level orchestrator:
Uses planner (Ollama content extraction) + renderer (MoviePy) + narrator to produce final video.
Supports optional topic-based animations for enhanced visualizations.
"""

from typing import Tuple, Dict, Any, Optional
import os
import uuid
from .planner import ContentPlanner
from .renderer import MoviePyRenderer
from .narrator import Narrator, generate_narration_for_plan


class EducationalAnimator:

    def __init__(
        self, 
        enable_narration: bool = True,
        enable_animations: bool = True,
        voice: str = None,
        language: str = "en"
    ):
        """
        Initialize the educational video generator.
        
        Args:
            enable_narration: Whether to generate audio narration
            enable_animations: Whether to include topic-based animations
            voice: TTS voice to use (auto-selected from language if None)
            language: Language code ('en', 'hi', 'es', 'fr', 'de', 'zh', 'ja', 'ko')
        """
        self.planner = ContentPlanner()
        self.renderer = MoviePyRenderer()
        self.enable_narration = enable_narration
        self.enable_animations = enable_animations
        self.language = language
        self.voice = voice
        os.makedirs("outputs", exist_ok=True)
        os.makedirs("outputs/audio", exist_ok=True)

    def generate(
        self,
        text: str,
        with_narration: Optional[bool] = None,
        with_animations: Optional[bool] = None,
        language: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate educational video with optional audio narration.
        
        Pipeline: Ollama Content Extraction → Narration (optional) → MoviePy Rendering
        
        Args:
            text: The concept/topic to explain
            with_narration: Override default narration setting
            with_animations: Override default animation setting
            language: Override default language
        
        Returns:
            Tuple of (video_path, content_dict)
        """
        
        use_narration = with_narration if with_narration is not None else self.enable_narration
        use_animations = with_animations if with_animations is not None else self.enable_animations
        use_language = language if language is not None else self.language

        # Step 1: Extract content from Ollama
        print(f"📝 Planning content for: {text}")
        content = self.planner.plan(text)
        
        # Store original concept for animation detection (LLM title may differ)
        content["_original_concept"] = text
        
        # Step 2: Generate narration if enabled
        narration = None
        session_id = str(uuid.uuid4())[:8]
        
        if use_narration:
            try:
                lang_display = {
                    "en": "English", "hi": "Hindi", "te": "Telugu",
                    "gu": "Gujarati", "bn": "Bengali", "pa": "Punjabi",
                    "ta": "Tamil", "kn": "Kannada", "ml": "Malayalam",
                    "mr": "Marathi", "or": "Odia", "as": "Assamese",
                    "es": "Spanish", "fr": "French", "de": "German",
                    "zh": "Chinese", "ja": "Japanese", "ko": "Korean"
                }.get(use_language, use_language)
                print(f"🎙️ Generating audio narration ({lang_display})...")
                narration = generate_narration_for_plan(
                    content, session_id, 
                    voice=self.voice,
                    language=use_language
                )
                print(f"   Audio duration: {narration['total_duration']:.1f}s")
                print(f"   Steps: {len(narration['step_durations'])}")
            except Exception as e:
                print(f"⚠️ Narration failed: {e}")
                narration = None

        # Step 3: Render video using MoviePy
        out_name = os.path.join(
            "outputs",
            f"animation_{abs(hash(text)) % 100000}.mp4"
        )

        try:
            video_path = self.renderer.render(
                content,
                output_filename=out_name,
                narration=narration,
                enable_animations=use_animations
            )
        except Exception as e:
            print(f"❌ Renderer error: {e}")
            import traceback
            traceback.print_exc()
            video_path = None

        return video_path, content