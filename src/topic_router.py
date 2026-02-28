# src/topic_router.py

"""
Topic detection and animation routing.
Detects topic type from concept text and optionally provides animation clips.
"""

import re
from typing import Optional, Tuple, Any


__all__ = [
    "detect_topic",
    "has_animation",
    "get_animation_clip",
    "get_animation_info",
]


def detect_topic(concept: str) -> str:
    """
    Detect the topic category from concept text.
    Returns topic identifier string.
    
    IMPORTANT: Only returns animated topics when the concept is 
    specifically about that topic, NOT when it's a related but different concept.
    """
    text = concept.lower()
    
    # ============================================
    # Exclusion patterns - topics that should NOT match animations
    # even if they contain animation keywords
    # ============================================
    
    # Data structure topics (not algorithm animations)
    data_structure_patterns = [
        r"linked\s*list",
        r"tree\s+(insertion|deletion|traversal|node)",
        r"binary\s+search\s+tree",  # BST is different from binary search algorithm
        r"bst\b",
        r"heap\b",
        r"stack\b",
        r"queue\b",
        r"graph\b",
        r"hash\s*(table|map)",
        r"array\s+(insertion|deletion)",
    ]
    
    for pattern in data_structure_patterns:
        if re.search(pattern, text):
            return "generic"  # These get card-based presentation, not algorithm animation
    
    # ============================================
    # Specific topic detection (strict matching)
    # ============================================
    
    # Bubble Sort - only if specifically about bubble sort algorithm
    if "bubble sort" in text and "tree" not in text:
        return "bubble_sort"

    # Binary Search - algorithm only, NOT binary search tree
    # Must have "binary search" but NOT "tree" or "bst"
    if "binary search" in text:
        if "tree" not in text and "bst" not in text and "node" not in text:
            return "binary_search"

    # Quadratic / Parabola / Second Degree
    quadratic_patterns = [
        r"\bquadratic\s+(equation|function|formula)",
        r"\bparabola\b",
        r"second\s+degree\s+(equation|polynomial)",
        r"\bax\^?2\s*[+-]",
        r"\bdiscriminant\b",
        r"roots?\s+of\s+(a\s+)?quadratic",
    ]

    for pattern in quadratic_patterns:
        if re.search(pattern, text):
            return "quadratic"

    # Sine Wave - physics/math sine waves
    sine_patterns = [
        r"\bsine\s+wave\b",
        r"\bsin\s*\(\s*x\s*\)",
        r"sinusoidal",
        r"trigonometric\s+wave",
    ]
    for pattern in sine_patterns:
        if re.search(pattern, text):
            return "sine_wave"

    # Projectile Motion - physics topic
    projectile_patterns = [
        r"\bprojectile\s+motion\b",
        r"\bprojectile\b.*\b(trajectory|angle|velocity)\b",
        r"\blaunch\s+angle\b",
        r"\bparabolic\s+trajectory\b",
    ]
    for pattern in projectile_patterns:
        if re.search(pattern, text):
            return "projectile_motion"

    # Pendulum - physics topic
    pendulum_patterns = [
        r"\bpendulum\b",
        r"\bsimple\s+harmonic\s+motion\b",
        r"\bshm\b",
    ]
    for pattern in pendulum_patterns:
        if re.search(pattern, text):
            return "pendulum"

    return "generic"


def has_animation(concept: str) -> bool:
    """
    Check if an animation is available for the given concept.
    Returns True if animated visualization can be generated.
    """
    topic = detect_topic(concept)
    animated_topics = [
        "bubble_sort", "binary_search", "quadratic", 
        "sine_wave", "projectile_motion", "pendulum"
    ]
    return topic in animated_topics


def get_animation_clip(concept: str, duration: float = 5.0, **kwargs) -> Optional[Any]:
    """
    Get an animated VideoClip for the concept if available.
    This is an ADDITIVE feature - does not modify existing rendering.
    
    Args:
        concept: Topic/concept text
        duration: Animation duration in seconds
        **kwargs: Additional animation parameters
    
    Returns:
        MoviePy VideoClip or None if no animation available
    """
    topic = detect_topic(concept)
    
    try:
        from .animation_clips import (
            create_projectile_clip,
            create_sine_wave_clip,
            create_bubble_sort_clip,
            create_binary_search_clip,
            create_quadratic_clip,
            create_pendulum_clip
        )
        
        if topic == "projectile_motion":
            return create_projectile_clip(
                duration=duration,
                velocity=kwargs.get("velocity", 50),
                angle=kwargs.get("angle", 45),
                title=kwargs.get("title", "Projectile Motion")
            )
        
        elif topic == "sine_wave":
            return create_sine_wave_clip(
                duration=duration,
                amplitude=kwargs.get("amplitude", 1.0),
                frequency=kwargs.get("frequency", 1.0),
                title=kwargs.get("title", "Sine Wave")
            )
        
        elif topic == "bubble_sort":
            return create_bubble_sort_clip(
                duration=duration,
                array=kwargs.get("array"),
                title=kwargs.get("title", "Bubble Sort")
            )
        
        elif topic == "binary_search":
            return create_binary_search_clip(
                duration=duration,
                array=kwargs.get("array"),
                target=kwargs.get("target", 7),
                title=kwargs.get("title", "Binary Search")
            )
        
        elif topic == "quadratic":
            return create_quadratic_clip(
                duration=duration,
                a=kwargs.get("a", 1.0),
                b=kwargs.get("b", -3.0),
                c=kwargs.get("c", 2.0),
                title=kwargs.get("title", "Quadratic Function")
            )
        
        elif topic == "pendulum":
            return create_pendulum_clip(
                duration=duration,
                length=kwargs.get("length", 1.0),
                max_angle=kwargs.get("max_angle", 30.0),
                title=kwargs.get("title", "Simple Pendulum")
            )
        
    except ImportError as e:
        print(f"   ⚠️ Animation import failed: {e}")
        return None
    
    return None


def get_animation_info(concept: str) -> dict:
    """
    Get animation availability info for a concept.
    
    Returns:
        Dict with keys: has_animation, topic, description
    """
    topic = detect_topic(concept)
    
    descriptions = {
        "bubble_sort": "Watch the bubble sort algorithm in action, comparing and swapping elements step by step.",
        "binary_search": "See how binary search efficiently finds a target by halving the search space.",
        "quadratic": "Observe the parabolic curve of a quadratic function with its vertex and roots.",
        "sine_wave": "Watch the sine wave propagate, showing the periodic nature of trigonometric functions.",
        "projectile_motion": "See a projectile follow its parabolic trajectory under gravity.",
        "pendulum": "Observe simple harmonic motion as the pendulum swings back and forth.",
        "generic": "Educational content presentation"
    }
    
    is_animated = topic in ["bubble_sort", "binary_search", "quadratic", 
                            "sine_wave", "projectile_motion", "pendulum"]
    
    return {
        "has_animation": is_animated,
        "topic": topic,
        "description": descriptions.get(topic, "Educational demonstration")
    }