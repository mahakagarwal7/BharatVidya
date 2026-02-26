# src/planner.py

"""
Hybrid Planner (Hackathon Ready)

Flow:
1. Detect known domain topics
2. Use deterministic domain engines for deep visualization
3. If unknown → use Local LLM structured slide mode
4. If LLM fails → fallback minimal rule-based animation
"""

import os
import json
import hashlib
from typing import Dict, Any

# Domain routing
from .topic_router import detect_topic

# Deterministic engines
from .domain_engines.bubble_sort import generate_bubble_sort_plan
from .domain_engines.quadratic import generate_quadratic_plan
from .domain_engines.sine_wave import generate_sine_wave_plan
from .domain_engines.projectile_motion import generate_projectile_plan
from .domain_engines.binary_search import generate_binary_search_plan

# Local LLM generic explainer
from .local_llm_client import safe_generate_generic_plan


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
        # Deterministic Domain Engines
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
        # Generic LLM Mode
        # ==========================================================

        else:
            generic_plan = safe_generate_generic_plan(concept)

            if generic_plan:
                plan = generic_plan
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
                "description": concept
            }
        ]

        sequence = [
            {
                "step": 1,
                "action": "show",
                "elements": ["title"],
                "duration": 4
            }
        ]

        return {
            "title": f"Understanding {concept}",
            "core_concept": concept,
            "visual_elements": elements,
            "animation_sequence": sequence,
            "_source": "fallback"
        }