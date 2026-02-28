"""
Narrator module - Generates audio narration for video steps using edge-tts.
Provides sync information (durations) for video rendering.
Uses ffmpeg directly for audio processing (no pydub/ffprobe dependency).
Supports multiple languages including Hindi translation.
"""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

import edge_tts

# Translation support
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

# Get ffmpeg from imageio_ffmpeg
try:
    from imageio_ffmpeg import get_ffmpeg_exe
    FFMPEG_PATH = get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = "ffmpeg"


# Available voices (Microsoft Edge TTS)
VOICES = {
    # English voices
    "male_us": "en-US-GuyNeural",
    "female_us": "en-US-JennyNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_india": "en-IN-PrabhatNeural",
    "female_india": "en-IN-NeerjaNeural",
    # Hindi voices
    "hindi_male": "hi-IN-MadhurNeural",
    "hindi_female": "hi-IN-SwaraNeural",
    # Telugu voices
    "telugu_male": "te-IN-MohanNeural",
    "telugu_female": "te-IN-ShrutiNeural",
    # Gujarati voices
    "gujarati_male": "gu-IN-NiranjanNeural",
    "gujarati_female": "gu-IN-DhwaniNeural",
    # Bengali voices
    "bengali_male": "bn-IN-BashkarNeural",
    "bengali_female": "bn-IN-TanishaaNeural",
    # Punjabi voices
    "punjabi_male": "pa-IN-OjasNeural",
    "punjabi_female": "pa-IN-VaaniNeural",
    # Tamil voices
    "tamil_male": "ta-IN-ValluvarNeural",
    "tamil_female": "ta-IN-PallaviNeural",
    # Kannada voices
    "kannada_male": "kn-IN-GaganNeural",
    "kannada_female": "kn-IN-SapnaNeural",
    # Malayalam voices
    "malayalam_male": "ml-IN-MidhunNeural",
    "malayalam_female": "ml-IN-SobhanaNeural",
    # Marathi voices
    "marathi_male": "mr-IN-ManoharNeural",
    "marathi_female": "mr-IN-AarohiNeural",
    # Odia voices
    "odia_male": "or-IN-PravathNeural",
    "odia_female": "or-IN-SubhasiniNeural",
    # Assamese voices
    "assamese_male": "as-IN-PriyomNeural",
    "assamese_female": "as-IN-YashicaNeural",
    # Other languages
    "spanish_male": "es-ES-AlvaroNeural",
    "spanish_female": "es-ES-ElviraNeural",
    "french_male": "fr-FR-HenriNeural",
    "french_female": "fr-FR-DeniseNeural",
    "german_male": "de-DE-ConradNeural",
    "german_female": "de-DE-KatjaNeural",
    "chinese_male": "zh-CN-YunxiNeural",
    "chinese_female": "zh-CN-XiaoxiaoNeural",
    "japanese_female": "ja-JP-NanamiNeural",
    "korean_female": "ko-KR-SunHiNeural",
}

# Language to default voice mapping
LANGUAGE_VOICES = {
    "en": "en-US-JennyNeural",
    # Indian languages
    "hi": "hi-IN-SwaraNeural",
    "te": "te-IN-ShrutiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "bn": "bn-IN-TanishaaNeural",
    "pa": "pa-IN-VaaniNeural",
    "ta": "ta-IN-PallaviNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "mr": "mr-IN-AarohiNeural",
    "or": "or-IN-SubhasiniNeural",
    "as": "as-IN-YashicaNeural",
    # Other languages
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
}

DEFAULT_VOICE = "en-US-JennyNeural"
MIN_STEP_DURATION = 3.0  # Minimum seconds per step
STEP_BUFFER = 0.5  # Buffer between steps


def translate_text(text: str, source_lang: str = "en", target_lang: str = "hi") -> str:
    """
    Translate text from source language to target language.
    Falls back to original text if translation fails.
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'en', 'hi')
        target_lang: Target language code (e.g., 'hi', 'en')
    
    Returns:
        Translated text or original if translation fails
    """
    if not TRANSLATION_AVAILABLE:
        print("Warning: deep-translator not installed. Run: pip install deep-translator")
        return text
    
    if source_lang == target_lang:
        return text
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Translation warning: {e}")
        return text


def translate_steps(steps: List[str], target_lang: str = "hi") -> List[str]:
    """Translate a list of step descriptions to target language."""
    if target_lang == "en":
        return steps
    
    translated = []
    for step in steps:
        # Ensure step is a string (handle dict/mixed types from LLM output)
        if isinstance(step, dict):
            step = step.get("text", step.get("fact", step.get("description", str(step))))
        step_str = str(step) if not isinstance(step, str) else step
        translated.append(translate_text(step_str, "en", target_lang))
    return translated


def get_voice_for_language(language: str) -> str:
    """Get the default voice for a language code."""
    return LANGUAGE_VOICES.get(language, DEFAULT_VOICE)


def get_audio_duration_ffmpeg(file_path: str) -> float:
    """Get audio duration using ffmpeg."""
    try:
        cmd = [
            FFMPEG_PATH,
            "-i", file_path,
            "-f", "null",
            "-"
        ]
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            timeout=30,  # Add timeout to prevent hanging
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Parse duration from stderr (ffmpeg outputs info to stderr)
        output = result.stderr
        for line in output.split('\n'):
            if 'Duration:' in line:
                # Format: Duration: 00:00:05.23, ...
                time_str = line.split('Duration:')[1].split(',')[0].strip()
                parts = time_str.split(':')
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        
        # Fallback: estimate based on file size (rough approximation for mp3)
        file_size = os.path.getsize(file_path)
        # Approximate: 128kbps mp3 = 16KB/sec
        return file_size / 16000
        
    except Exception as e:
        print(f"Warning: Could not get duration: {e}")
        return 3.0  # Default fallback


def concatenate_audio_ffmpeg(audio_files: List[Dict], output_path: str) -> str:
    """Concatenate audio files using ffmpeg with silence padding."""
    
    if not audio_files:
        return output_path
    
    temp_dir = Path(output_path).parent
    list_file = temp_dir / "concat_list.txt"
    
    # Build file list with silence padding
    with open(list_file, 'w') as f:
        for step_info in audio_files:
            audio_path = step_info.get("audio_path")
            if audio_path and os.path.exists(audio_path):
                # Write audio file
                f.write(f"file '{os.path.abspath(audio_path)}'\n")
                
                # Calculate silence duration
                raw_duration = step_info.get("raw_duration", 0)
                effective_duration = step_info.get("effective_duration", MIN_STEP_DURATION)
                silence_ms = int((effective_duration - raw_duration) * 1000)
                
                if silence_ms > 100:
                    # Create a silence file for this duration
                    sil_file = temp_dir / f"silence_{silence_ms}ms.wav"
                    if not sil_file.exists():
                        cmd = [
                            FFMPEG_PATH,
                            "-f", "lavfi",
                            "-i", "anullsrc=r=44100:cl=mono",
                            "-t", str(silence_ms / 1000),
                            "-y",
                            str(sil_file)
                        ]
                        subprocess.run(cmd, capture_output=True,
                                      creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    f.write(f"file '{os.path.abspath(sil_file)}'\n")
            else:
                # Just silence for this step
                silence_ms = int(step_info.get("effective_duration", MIN_STEP_DURATION) * 1000)
                sil_file = temp_dir / f"silence_{silence_ms}ms.wav"
                if not sil_file.exists():
                    cmd = [
                        FFMPEG_PATH,
                        "-f", "lavfi",
                        "-i", "anullsrc=r=44100:cl=mono",
                        "-t", str(silence_ms / 1000),
                        "-y",
                        str(sil_file)
                    ]
                    subprocess.run(cmd, capture_output=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                f.write(f"file '{os.path.abspath(sil_file)}'\n")
    
    # Concatenate using concat demuxer
    cmd = [
        FFMPEG_PATH,
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c:a", "libmp3lame",
        "-q:a", "2",
        "-y",
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True,
                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    
    # Cleanup temp file
    try:
        list_file.unlink()
    except:
        pass
    
    return output_path


class Narrator:
    def __init__(self, voice: str = DEFAULT_VOICE, output_dir: str = "outputs/audio"):
        self.voice = voice
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def _generate_audio_async(self, text: str, output_path: str) -> str:
        """Generate audio for a single text using edge-tts."""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        return output_path
    
    def generate_step_audio(self, text: str, step_index: int, session_id: str) -> Dict:
        """
        Generate audio for a single step.
        Returns dict with audio_path and duration.
        """
        output_path = self.output_dir / f"{session_id}_step_{step_index}.mp3"
        
        # Run async TTS
        asyncio.run(self._generate_audio_async(text, str(output_path)))
        
        # Get duration using ffmpeg
        duration_sec = get_audio_duration_ffmpeg(str(output_path))
        
        # Apply minimum duration
        effective_duration = max(duration_sec, MIN_STEP_DURATION) + STEP_BUFFER
        
        return {
            "audio_path": str(output_path),
            "raw_duration": duration_sec,
            "effective_duration": effective_duration,
            "step_index": step_index
        }
    
    def generate_narration(self, steps: List[str], session_id: str) -> Dict:
        """
        Generate narration for all steps.
        Returns dict with step_audios list, combined audio path, and total duration.
        """
        step_audios = []
        
        for i, step_text in enumerate(steps):
            if not step_text or not step_text.strip():
                # Skip empty steps, but add placeholder duration
                step_audios.append({
                    "audio_path": None,
                    "raw_duration": 0,
                    "effective_duration": MIN_STEP_DURATION,
                    "step_index": i
                })
                continue
                
            audio_info = self.generate_step_audio(step_text, i, session_id)
            step_audios.append(audio_info)
        
        # Combine all audio files using ffmpeg
        combined_path = str(self.output_dir / f"{session_id}_combined.mp3")
        concatenate_audio_ffmpeg(step_audios, combined_path)
        
        # Calculate total duration
        total_duration = sum(s["effective_duration"] for s in step_audios)
        
        return {
            "step_audios": step_audios,
            "combined_audio_path": combined_path,
            "total_duration": total_duration,
            "step_durations": [s["effective_duration"] for s in step_audios]
        }
    
    def generate_intro_audio(self, title: str, session_id: str) -> Dict:
        """Generate audio for video intro/title."""
        output_path = self.output_dir / f"{session_id}_intro.mp3"
        
        # Run async TTS
        asyncio.run(self._generate_audio_async(title, str(output_path)))
        
        # Get duration using ffmpeg
        duration_sec = get_audio_duration_ffmpeg(str(output_path))
        
        return {
            "audio_path": str(output_path),
            "duration": max(duration_sec, 2.0) + STEP_BUFFER
        }
    
    def generate_animation_audio(self, description: str, session_id: str) -> Dict:
        """Generate audio narration for animation segment."""
        output_path = self.output_dir / f"{session_id}_animation.mp3"
        
        # Run async TTS
        asyncio.run(self._generate_audio_async(description, str(output_path)))
        
        # Get duration using ffmpeg
        duration_sec = get_audio_duration_ffmpeg(str(output_path))
        
        return {
            "audio_path": str(output_path),
            "duration": max(duration_sec, 3.0) + STEP_BUFFER
        }
    
    def generate_facts_audio(self, facts: List[str], session_id: str) -> Dict:
        """Generate audio narration for key facts."""
        if not facts:
            return {"audio_path": None, "duration": 0}
        
        # Ensure all facts are strings (handle dict/mixed types from LLM output)
        fact_strings = []
        for fact in facts:
            if isinstance(fact, str):
                fact_strings.append(fact)
            elif isinstance(fact, dict):
                # Extract text from dict (common LLM output format)
                fact_strings.append(fact.get("text", fact.get("fact", str(fact))))
            else:
                fact_strings.append(str(fact))
        
        if not fact_strings:
            return {"audio_path": None, "duration": 0}
        
        # Combine facts into readable text
        facts_text = "Key facts to remember: " + ". ".join(fact_strings)
        output_path = self.output_dir / f"{session_id}_facts.mp3"
        
        # Run async TTS
        asyncio.run(self._generate_audio_async(facts_text, str(output_path)))
        
        # Get duration using ffmpeg
        duration_sec = get_audio_duration_ffmpeg(str(output_path))
        
        return {
            "audio_path": str(output_path),
            "duration": max(duration_sec, 3.0) + STEP_BUFFER
        }

    def cleanup(self, session_id: str):
        """Remove temporary audio files for a session."""
        for f in self.output_dir.glob(f"{session_id}_*.mp3"):
            try:
                f.unlink()
            except:
                pass
        # Also cleanup silence files
        for f in self.output_dir.glob("silence_*.wav"):
            try:
                f.unlink()
            except:
                pass


def generate_narration_for_plan(
    plan: Dict, 
    session_id: str, 
    voice: str = None,
    language: str = "en"
) -> Dict:
    """
    Generate narration from educational content extracted by Ollama.
    
    Supports both new content format (sections) and legacy visual plan format.
    
    Args:
        plan: Content dict with sections (or legacy visual_elements)
        session_id: Unique session ID for file naming
        voice: TTS voice to use (auto-selected from language if None)
        language: Target language code ('en', 'hi', 'es', etc.)
    
    Returns:
        Dict with narration info including step_durations and audio paths
    """
    # Select voice based on language if not specified
    if voice is None:
        voice = get_voice_for_language(language)
    
    narrator = Narrator(voice=voice)
    
    # Extract step descriptions from content
    steps = []
    
    # New format: sections with heading/body
    sections = plan.get("sections", [])
    if sections:
        for section in sections:
            if isinstance(section, dict):
                body = section.get("body", "")
                heading = section.get("heading", "")
                # Use body text for narration, fall back to heading
                narration_text = body if body else heading
                if narration_text and len(narration_text.strip()) > 5:
                    steps.append(narration_text.strip())
    
    # Legacy fallback: visual_elements format
    if not steps:
        visual_elements = plan.get("visual_elements", [])
        for elem in visual_elements:
            elem_id = elem.get("id", "")
            if elem_id.startswith("text_step_") and "_brief" not in elem_id:
                description = elem.get("description", "")
                if description:
                    steps.append(description)
    
    if not steps:
        # Final fallback: use summary
        summary = plan.get("summary", "")
        if summary:
            steps.append(summary)
    
    # Translate steps if needed
    if language != "en" and TRANSLATION_AVAILABLE:
        print(f"🌐 Translating to {language}...")
        steps = translate_steps(steps, language)
    
    # Generate intro from title
    title = plan.get("title", "")
    intro_info = None
    if title:
        # Translate title if needed
        if language != "en" and TRANSLATION_AVAILABLE:
            title = translate_text(title, "en", language)
        intro_info = narrator.generate_intro_audio(title, session_id)
    
    # Generate animation narration if topic has animation
    animation_info = None
    try:
        from .topic_router import has_animation, get_animation_info
        if has_animation(title):
            anim_info = get_animation_info(title)
            if anim_info and anim_info.get("description"):
                anim_desc = anim_info["description"]
                if language != "en" and TRANSLATION_AVAILABLE:
                    anim_desc = translate_text(anim_desc, "en", language)
                animation_info = narrator.generate_animation_audio(anim_desc, session_id)
    except Exception as e:
        print(f"Animation narration skipped: {e}")
    
    # Generate facts narration
    facts_info = None
    key_facts = plan.get("key_facts", [])
    if key_facts:
        facts_to_narrate = key_facts
        if language != "en" and TRANSLATION_AVAILABLE:
            facts_to_narrate = translate_steps(key_facts, language)
        facts_info = narrator.generate_facts_audio(facts_to_narrate, session_id)
    
    # Generate step narration
    narration_result = narrator.generate_narration(steps, session_id)
    narration_result["intro"] = intro_info
    narration_result["animation"] = animation_info
    narration_result["facts"] = facts_info
    narration_result["language"] = language
    
    # ============================================
    # Combine all audio in video playback order:
    # intro → animation → sections → facts
    # ============================================
    all_audio_segments = []
    
    # 1. Intro audio
    if intro_info and intro_info.get("audio_path"):
        all_audio_segments.append({
            "audio_path": intro_info["audio_path"],
            "raw_duration": intro_info.get("duration", 3.0),
            "effective_duration": intro_info.get("duration", 3.0)
        })
    
    # 2. Animation audio
    if animation_info and animation_info.get("audio_path"):
        all_audio_segments.append({
            "audio_path": animation_info["audio_path"],
            "raw_duration": animation_info.get("duration", 5.0),
            "effective_duration": animation_info.get("duration", 5.0)
        })
    
    # 3. Section audio
    for step_audio in narration_result.get("step_audios", []):
        all_audio_segments.append(step_audio)
    
    # 4. Facts audio
    if facts_info and facts_info.get("audio_path"):
        all_audio_segments.append({
            "audio_path": facts_info["audio_path"],
            "raw_duration": facts_info.get("duration", 3.0),
            "effective_duration": facts_info.get("duration", 3.0)
        })
    
    # Create combined audio with all segments
    combined_path = str(narrator.output_dir / f"{session_id}_full_combined.mp3")
    concatenate_audio_ffmpeg(all_audio_segments, combined_path)
    
    # Update total duration to include all segments
    total_duration = sum(s.get("effective_duration", 0) for s in all_audio_segments)
    
    narration_result["combined_audio_path"] = combined_path
    narration_result["total_duration"] = total_duration
    narration_result["all_segments"] = all_audio_segments
    
    return narration_result


# For testing
if __name__ == "__main__":
    test_steps = [
        "Initialize the simulation environment with gravity set to negative 9.8 meters per second squared.",
        "Release a virtual projectile at an angle of 45 degrees.",
        "Animate the motion frame by frame showing the parabolic trajectory.",
        "Overlay the trajectory path to visualize the complete motion."
    ]
    
    narrator = Narrator()
    result = narrator.generate_narration(test_steps, "test_session")
    
    print("Narration generated:")
    print(f"  Combined audio: {result['combined_audio_path']}")
    print(f"  Total duration: {result['total_duration']:.2f}s")
    print(f"  Step durations: {result['step_durations']}")
