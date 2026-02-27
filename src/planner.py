# src/planner.py

"""
Hybrid Planner (Upgraded Architecture)

Flow:
1. Detect known domain topics (deterministic engines)
2. If not domain → LLM generates explanation only
3. Visual Pattern Engine generates primitives
4. Renderer draws primitives
"""

import os
import json
import hashlib
from typing import Dict, Any

# Domain routing
from .topic_router import detect_topic

# Deterministic engines (optional — still supported)
from .domain_engines.bubble_sort import generate_bubble_sort_plan
from .domain_engines.quadratic import generate_quadratic_plan
from .domain_engines.sine_wave import generate_sine_wave_plan
from .domain_engines.projectile_motion import generate_projectile_plan
from .domain_engines.binary_search import generate_binary_search_plan

# LLM explanation generator
from .local_llm_client import safe_generate_generic_plan

# Visual Pattern Engine
from .visual_pattern_engine import generate_visual_plan


# --------------------------------------------------
# Plan Saving Utility
# --------------------------------------------------

def save_plan(plan: Dict[str, Any], prefix="plan"):
    os.makedirs("outputs/plans", exist_ok=True)

    h = hashlib.md5(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:8]
    path = os.path.join("outputs", "plans", f"{prefix}_{h}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)

    return path


# --------------------------------------------------
# Planner Class
# --------------------------------------------------

class SimplePlanner:

    def __init__(self):
        os.makedirs("outputs/plans", exist_ok=True)

    # --------------------------------------------------
    # Main Entry
    # --------------------------------------------------

    def plan_universal_scene(self, concept: str) -> Dict[str, Any]:

        topic = detect_topic(concept)

        # ==========================================================
        # Deterministic Domain Engines (Optional but Powerful)
        # ==========================================================

        if topic == "bubble_sort":
            plan = generate_bubble_sort_plan(concept)

        elif topic == "quadratic":
            plan = generate_quadratic_plan(concept)

        elif topic == "sine_wave":
            plan = generate_sine_wave_plan(concept)

        elif topic == "projectile_motion":
            plan = generate_projectile_plan(concept)

        elif topic == "binary_search":
            plan = generate_binary_search_plan(concept)

        # ==========================================================
        # Generic Hybrid Mode (LLM + Visual Pattern Engine)
        # ==========================================================

        else:
            explanation = safe_generate_generic_plan(concept)

            if explanation:
                plan = generate_visual_plan(concept, explanation)
            else:
                plan = self._minimal_fallback(concept)

        # Save plan
        plan_file = save_plan(plan)
        plan["_saved_plan_file"] = plan_file

        return plan

    # --------------------------------------------------
    # Safe Minimal Fallback
    # --------------------------------------------------

    def _minimal_fallback(self, concept: str) -> Dict[str, Any]:

        elements = [
            {
                "id": "title",
                "type": "text",
                "description": concept,
                "x": 80,
                "y": 100
            }
        ]

        sequence = [
            {
                "elements": ["title"],
                "duration": 5
            }
        ]

        return {
            "title": f"Understanding {concept}",
            "visual_elements": elements,
            "animation_sequence": sequence,
            "_source": "fallback"
        }