# src/local_llm_client.py

import json
import subprocess

MODEL_NAME = "phi3:mini"


def _call_ollama(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180
        )
        return result.stdout.decode("utf-8").strip()
    except Exception as e:
        print("Ollama call failed:", e)
        return ""


# --------------------------------------------------
# REASONING + CATEGORY GENERATOR
# --------------------------------------------------

def generate_reasoning_plan(concept: str):

    prompt = f"""
You are an educational AI.

Explain the concept clearly and classify it.

Concept: {concept}

Classify the concept into ONE of:
- process
- structure
- hierarchy
- system
- abstract

Then provide structured explanation steps.

Return ONLY valid JSON.

Format:

{{
  "title": "Short clear title",
  "category": "one of the five",
  "steps": [
    "Step 1 explanation",
    "Step 2 explanation",
    "Step 3 explanation"
  ]
}}
"""

    raw_output = _call_ollama(prompt)

    if not raw_output:
        return None

    try:
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1

        if start == -1 or end == -1:
            return None

        data = json.loads(raw_output[start:end])

        if "title" not in data or "steps" not in data:
            return None

        if not isinstance(data["steps"], list):
            return None

        if "category" not in data:
            data["category"] = "abstract"

        # Guarantee minimum 3 steps
        if len(data["steps"]) < 3:
            data["steps"] = [
                f"Introduction to {concept}",
                f"Key aspects of {concept}",
                f"Applications of {concept}"
            ]

        return data

    except:
        return None