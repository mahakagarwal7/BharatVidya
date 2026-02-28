# src/renderer.py

"""
MoviePy-native video renderer for educational content.
Uses ImageClip from card_generator + CompositeVideoClip for clean composition.
No raw TextClip overlays — all text is baked into PIL card images
to avoid white line artifacts from ImageMagick text rendering.
"""

from moviepy.editor import (
    VideoClip, ImageClip, ColorClip,
    CompositeVideoClip, AudioFileClip, concatenate_videoclips
)
import numpy as np
import os
from typing import Optional, Dict, List, Any

from .card_generator import create_section_card, create_title_card


# Video dimensions
WIDTH = 960
HEIGHT = 540
FPS = 24

# Timing — targets 40-50s total for 3 sections
TITLE_DURATION = 3.0
SECTION_DURATION = 3.5
TRANSITION_DURATION = 0.5
MIN_SECTION_DURATION = 2.5
FACTS_DURATION = 3.0


class MoviePyRenderer:
    """Renders educational content to video using card images + MoviePy composition."""

    def render(
        self,
        content: Dict[str, Any],
        output_filename: str,
        narration: Optional[Dict] = None
    ) -> str:
        """
        Render educational content to a video file.
        
        Args:
            content: Content dict from Ollama with title, summary, sections, etc.
            output_filename: Output video path
            narration: Optional narration data with step_durations and combined_audio_path
        
        Returns:
            Path to the rendered video file
        """
        title = content.get("title", "Educational Video")
        summary = content.get("summary", "")
        sections = content.get("sections", [])
        key_facts = content.get("key_facts", [])
        category = content.get("category", "general")
        
        print(f"🎬 Rendering video: {title}")
        print(f"   Sections: {len(sections)}")
        
        # ============================================
        # Calculate durations from narration
        # ============================================
        
        audio_path = None
        section_durations = []
        title_dur = TITLE_DURATION
        
        if narration:
            audio_path = narration.get("combined_audio_path")
            step_durations = narration.get("step_durations", [])
            intro_info = narration.get("intro")
            
            if intro_info and intro_info.get("duration"):
                title_dur = max(TITLE_DURATION, intro_info["duration"])
            
            for i in range(len(sections)):
                if i < len(step_durations):
                    section_durations.append(max(MIN_SECTION_DURATION, step_durations[i]))
                else:
                    section_durations.append(SECTION_DURATION)
        else:
            section_durations = [SECTION_DURATION] * len(sections)
        
        # ============================================
        # Build scene clips (all from card images — no TextClip overlays)
        # ============================================
        
        scene_clips = []
        
        # --- Scene 1: Title Card ---
        title_card_path = create_title_card(title, summary, category)
        title_scene = self._image_scene(title_card_path, title_dur)
        scene_clips.append(title_scene)
        
        # --- Scene 2+: Content Sections ---
        concept = content.get("title", "concept")
        for i, section in enumerate(sections):
            dur = section_durations[i] if i < len(section_durations) else SECTION_DURATION
            heading = section.get("heading", f"Section {i+1}")
            body = section.get("body", "")
            key_pts = section.get("key_points", [])
            
            card_path = create_section_card(concept, heading, body, i, key_pts)
            section_scene = self._image_scene(card_path, dur)
            scene_clips.append(section_scene)
        
        # --- Final Scene: Key Facts ---
        if key_facts:
            from .card_generator import create_facts_card
            facts_path = create_facts_card(title, key_facts, category)
            facts_scene = self._image_scene(facts_path, FACTS_DURATION)
            scene_clips.append(facts_scene)
        
        # ============================================
        # Concatenate with transitions
        # ============================================
        
        if not scene_clips:
            print("   ❌ No scenes to render")
            return None
        
        # Add crossfade transitions
        transition_clips = []
        for i, clip in enumerate(scene_clips):
            if i == 0:
                transition_clips.append(clip.crossfadeout(TRANSITION_DURATION))
            elif i == len(scene_clips) - 1:
                transition_clips.append(clip.crossfadein(TRANSITION_DURATION))
            else:
                transition_clips.append(
                    clip.crossfadein(TRANSITION_DURATION).crossfadeout(TRANSITION_DURATION)
                )
        
        try:
            final_clip = concatenate_videoclips(
                transition_clips,
                method="compose",
                padding=-TRANSITION_DURATION
            )
        except Exception as e:
            print(f"   ⚠️ Transition concat failed ({e}), using simple concat")
            final_clip = concatenate_videoclips(scene_clips, method="compose")
        
        total_duration = final_clip.duration
        print(f"   Total duration: {total_duration:.1f}s")
        
        # ============================================
        # Add audio
        # ============================================
        
        output_dir = os.path.dirname(output_filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        if audio_path and os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(audio_path)
                if audio_clip.duration > total_duration:
                    audio_clip = audio_clip.subclip(0, total_duration)
                final_clip = final_clip.set_audio(audio_clip)
                
                final_clip.write_videofile(
                    output_filename,
                    fps=FPS,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                audio_clip.close()
            except Exception as e:
                print(f"   ⚠️ Audio attach failed: {e}")
                final_clip.write_videofile(
                    output_filename, fps=FPS, codec="libx264",
                    audio=False, preset="ultrafast", logger=None
                )
        else:
            final_clip.write_videofile(
                output_filename, fps=FPS, codec="libx264",
                audio=False, preset="ultrafast", logger=None
            )
        
        # Cleanup
        for clip in scene_clips:
            try:
                clip.close()
            except:
                pass
        try:
            final_clip.close()
        except:
            pass
        
        print(f"   ✅ Video saved: {output_filename}")
        return output_filename

    def _image_scene(self, image_path: str, duration: float) -> VideoClip:
        """Create a scene from a card image — no text overlays."""
        try:
            clip = ImageClip(image_path).set_duration(duration).resize((WIDTH, HEIGHT))
        except Exception:
            clip = ColorClip(
                size=(WIDTH, HEIGHT), color=(15, 25, 45)
            ).set_duration(duration)
        return clip