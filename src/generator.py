# src/generator.py
"""
Generator: normalize and enrich the planner output.
Keeps the plan consistent, safe, and optimized for fast rendering.
"""

from typing import Dict, Any


MAX_DURATION = 3.0  # 🔥 clamp animation time for performance


class SimpleGenerator:
    def normalize_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:

        plan = dict(plan)  # shallow copy

        # Ensure required keys
        # frame detection.. statement here
        plan.setdefault("title", "Educational Animation")
        plan.setdefault("core_concept", "")
        plan.setdefault("visual_elements", [])
        plan.setdefault("animation_sequence", [])

        # Ensure at least one element exists (prevents crash)
        if not plan["visual_elements"]:
            plan["visual_elements"] = [{
                "id": "main",
                "type": "circle",
                "description": "Main concept"
            }]

        # Normalize element structure
        for i, e in enumerate(plan["visual_elements"]):
            e.setdefault("id", f"elem_{i}")
            e.setdefault("type", "circle")
            e.setdefault("description", e.get("description", e["id"]))

        # Normalize animation steps safely
        for i, s in enumerate(plan["animation_sequence"]):

            s.setdefault("step", i + 1)
            s.setdefault("title", f"Step {i+1}")
            s.setdefault("action", "show")

            # Safe element fallback
            if "elements" not in s or not s["elements"]:
                s["elements"] = [plan["visual_elements"][0]["id"]]

            # Clamp duration for faster rendering
            duration = s.get("duration", 2.5)
            s["duration"] = min(duration, MAX_DURATION)

        # Ensure at least one animation step exists
        if not plan["animation_sequence"]:
            plan["animation_sequence"] = [{
                "step": 1,
                "title": "Introduction",
                "action": "show",
                "elements": [plan["visual_elements"][0]["id"]],
                "duration": 2.0
            }]

        return plan