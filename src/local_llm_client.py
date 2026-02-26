# src/local_llm_client.py

import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"


def call_llm(prompt: str) -> str:

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()
    return response.json()["response"]


def build_structured_prompt(user_prompt: str) -> str:
    return f"""
You are an educational content planner.

Return STRICTLY in this format:

TITLE: <short title>

POINTS:
- <point 1>
- <point 2>
- <point 3>
- <point 4>

Concept: {user_prompt}
"""


def parse_structured_output(text: str):

    title_match = re.search(r"TITLE:\s*(.*)", text)
    title = title_match.group(1).strip() if title_match else "Educational Topic"

    points = re.findall(r"-\s*(.*)", text)

    if not points:
        return None

    return {
        "title": title,
        "points": points[:5]
    }


def safe_generate_generic_plan(user_prompt: str):

    try:
        prompt = build_structured_prompt(user_prompt)
        raw = call_llm(prompt)

        parsed = parse_structured_output(raw)

        if not parsed:
            return None

        elements = [
            {"id": "title", "type": "text", "description": parsed["title"]}
        ]

        sequence = [
            {
                "step": 1,
                "action": "show",
                "elements": ["title"],
                "duration": 2
            }
        ]

        for i, point in enumerate(parsed["points"]):
            elem_id = f"point{i}"
            elements.append({
                "id": elem_id,
                "type": "text",
                "description": point
            })

            sequence.append({
                "step": i + 2,
                "action": "show",
                "elements": [elem_id],
                "duration": 2
            })

        return {
            "title": parsed["title"],
            "core_concept": user_prompt,
            "visual_elements": elements,
            "animation_sequence": sequence,
            "_source": "local_llm"
        }

    except Exception as e:
        print("LLM generic mode failed:", e)
        return None