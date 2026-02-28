# src/planner.py

"""
Content planner - extracts educational content via Ollama.
"""

import os
import json
import hashlib
from typing import Dict, Any

from .local_llm_client import extract_content


def save_plan(plan: Dict[str, Any], prefix="plan"):
    os.makedirs("outputs/plans", exist_ok=True)
    h = hashlib.md5(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:8]
    path = os.path.join("outputs", "plans", f"{prefix}_{h}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    return path


class ContentPlanner:
    """Extracts structured educational content via Ollama."""

    def plan(self, concept: str) -> Dict[str, Any]:
        """
        Extract educational content for a concept.
        
        Returns content dict with title, summary, sections, key_facts, etc.
        """
        content = extract_content(concept)
        
        plan_file = save_plan(content)
        content["_saved_plan_file"] = plan_file
        
        return content