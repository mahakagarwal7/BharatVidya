# src/local_llm_client.py

import json
import subprocess

MODEL_NAME = "phi3:mini"

ALLOWED_TYPES = [
    "structure",
    "sequence",
    "flow",
    "transformation",
    "hierarchy",
    "system",
    "abstract"
]


def _call_ollama(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        return result.stdout.decode("utf-8").strip()
    except Exception as e:
        print("Ollama call failed:", e)
        return ""


def safe_generate_generic_plan(concept: str):

    prompt = f"""
You are an educational content planner.

Return ONLY valid JSON.
No markdown.
No comments.

Classify the concept into ONE of these concept types:
structure
sequence
flow
transformation
hierarchy
system
abstract

Then generate:

{{
  "title": "short title",
  "concept_type": "one of the allowed types",
  "points": [
    "point 1",
    "point 2",
    "point 3"
  ]
}}

Keep 3–5 short bullet points.

Concept: {concept}
"""

    raw_output = _call_ollama(prompt)

    if not raw_output:
        return None

    try:
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        json_str = raw_output[start:end]
        data = json.loads(json_str)

        if "title" not in data or "points" not in data:
            return None

        if data.get("concept_type") not in ALLOWED_TYPES:
            data["concept_type"] = "abstract"

        return data

    except Exception as e:
        print("JSON parsing failed:", e)
        return None