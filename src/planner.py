# src/planner.py

import os
import json
import hashlib
from typing import Dict, Any, List

from .topic_router import detect_topics
from .domain_engines.bubble_sort import generate_bubble_sort_plan
from .domain_engines.binary_search import generate_binary_search_plan
from .domain_engines.quadratic import generate_quadratic_plan
from .domain_engines.sine_wave import generate_sine_wave_plan
from .domain_engines.projectile import generate_projectile_plan
from .local_llm_client import safe_generate_plan


def save_plan(plan: Dict[str, Any], prefix="plan"):
    os.makedirs("outputs/plans", exist_ok=True)
    h = hashlib.md5(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:8]
    path = os.path.join("outputs", "plans", f"{prefix}_{h}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    return path


class SimplePlanner:

    def generate_plans(self, concept: str) -> List[Dict[str, Any]]:

        topics = detect_topics(concept)
        plans = []

        for topic in topics:

            if topic == "bubble_sort":
                plan = generate_bubble_sort_plan(concept)

            elif topic == "binary_search":
                plan = generate_binary_search_plan(concept)

            elif topic == "quadratic":
                plan = generate_quadratic_plan(concept)

            elif topic == "sine":
                plan = generate_sine_wave_plan(concept)

            elif topic == "projectile":
                plan = generate_projectile_plan(concept)

            else:
                plan = safe_generate_plan(concept)

            plan["_saved_plan_file"] = save_plan(plan)
            plans.append(plan)

        return plans