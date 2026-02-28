# src/domain_engines/__init__.py

"""
DEPRECATED: Domain-specific plan generators for educational topics.

NOTE: This module is LEGACY CODE and is no longer used by the main pipeline.
The current animation system uses:
  - src/topic_router.py for topic detection and animation routing
  - src/animation_clips.py for frame-by-frame animation generation

These domain engines generated the old visual_elements/animation_sequence format.
They are preserved for reference but may be removed in a future version.
"""

import warnings
warnings.warn(
    "domain_engines module is deprecated. Use topic_router and animation_clips instead.",
    DeprecationWarning,
    stacklevel=2
)

from .projectile_motion import generate_projectile_plan
from .sine_wave import generate_sine_wave_plan
from .bubble_sort import generate_bubble_sort_plan
from .binary_search import generate_binary_search_plan
from .quadratic import generate_quadratic_plan

__all__ = [
    "generate_projectile_plan",
    "generate_sine_wave_plan", 
    "generate_bubble_sort_plan",
    "generate_binary_search_plan",
    "generate_quadratic_plan"
]


def get_domain_plan(topic: str, concept: str):
    """
    Get a domain-specific plan based on topic type.
    
    Args:
        topic: Topic identifier (e.g., "projectile_motion", "sine_wave")
        concept: Full concept text
    
    Returns:
        Plan dict with visual_elements and animation_sequence, or None
    """
    generators = {
        "projectile_motion": generate_projectile_plan,
        "sine_wave": generate_sine_wave_plan,
        "bubble_sort": generate_bubble_sort_plan,
        "binary_search": generate_binary_search_plan,
        "quadratic": generate_quadratic_plan
    }
    
    generator = generators.get(topic)
    if generator:
        try:
            return generator(concept)
        except Exception as e:
            print(f"   ⚠️ Domain plan generation failed: {e}")
            return None
    
    return None