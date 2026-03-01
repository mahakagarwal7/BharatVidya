# web_app/video_service.py
"""Service layer wrapping EducationalAnimator for API use"""

import os
import sys
from typing import Tuple, Dict, Any, Optional, Callable

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.animator import EducationalAnimator


class VideoService:
    """
    Wraps EducationalAnimator with progress callbacks for API.
    """
    
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_video(
        self,
        concept: str,
        language: str = "en",
        enable_animations: bool = True,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Generate educational video with progress updates.
        
        Args:
            concept: Topic/concept to explain
            language: Language code
            enable_animations: Whether to include topic animations
            progress_callback: Function(step_name, percent) for progress updates
        
        Returns:
            Tuple of (video_path, plan_dict) or (None, None) on failure
        """
        
        def update(step: str, pct: int):
            if progress_callback:
                progress_callback(step, pct)
            print(f"  [{pct}%] {step}")
        
        try:
            update("Initializing animator...", 10)
            
            animator = EducationalAnimator(
                language=language,
                enable_animations=enable_animations
            )
            
            update("Planning content with Ollama...", 20)
            
            # Generate video
            # Note: The actual animator doesn't support progress callbacks internally,
            # so we estimate progress based on typical stages
            video_path, plan = animator.generate(
                concept,
                language=language,
                with_animations=enable_animations
            )
            
            if video_path:
                update("Video generation complete!", 100)
                return video_path, plan
            else:
                return None, None
                
        except Exception as e:
            print(f"VideoService error: {e}")
            import traceback
            traceback.print_exc()
            raise


# Singleton instance
video_service = VideoService()


def generate_video_with_progress(
    concept: str,
    language: str,
    enable_animations: bool,
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Convenience function for job manager.
    """
    return video_service.generate_video(
        concept=concept,
        language=language,
        enable_animations=enable_animations,
        progress_callback=progress_callback
    )
