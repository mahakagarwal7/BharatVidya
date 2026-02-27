# src/planner.py

import os
import json
import hashlib
from typing import Dict, Any

from .local_llm_client import generate_reasoning_plan
from .visual_builder import build_visual_plan


def save_plan(plan: Dict[str, Any], prefix="plan"):
    os.makedirs("outputs/plans", exist_ok=True)
    h = hashlib.md5(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:8]
    path = os.path.join("outputs", "plans", f"{prefix}_{h}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    return path


class SimplePlanner:

    def plan_universal_scene(self, concept: str) -> Dict[str, Any]:

        clean_concept = concept.strip()

        if len(clean_concept.split()) < 2:
            clean_concept = f"Explain the concept of {clean_concept}"

        reasoning = generate_reasoning_plan(clean_concept)

        if not reasoning:
            reasoning = {
                "title": clean_concept,
                "category": "abstract",
                "steps": [
                    f"Introduction to {clean_concept}",
                    f"Key aspects of {clean_concept}",
                    f"Applications of {clean_concept}"
                ]
            }

        plan = build_visual_plan(clean_concept, reasoning)

        plan_file = save_plan(plan)
        plan["_saved_plan_file"] = plan_file

        return plan