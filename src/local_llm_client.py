# src/local_llm_client.py

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"


def extract_keywords(prompt: str):

    system_prompt = f"""
Extract 3 short educational keywords about:

"{prompt}"

Rules:
- Return ONLY 3 lines
- No numbering
- No explanation
- Each line maximum 4 words
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": system_prompt,
            "stream": False
        },
        timeout=60
    )

    result = response.json()["response"]

    lines = [
        line.strip()
        for line in result.split("\n")
        if line.strip()
    ]

    return lines[:3]


def safe_generate_plan(prompt: str):

    try:
        print("Using Local LLM for generic topic...")

        keywords = extract_keywords(prompt)

        visual_elements = [
            {"id": "title", "type": "text", "description": prompt}
        ]

        for i, kw in enumerate(keywords):
            visual_elements.append({
                "id": f"kw{i}",
                "type": "text",
                "description": kw
            })

        animation_sequence = []

        # Title
        animation_sequence.append({
            "step": 1,
            "title": "Introduction",
            "action": "show_text",
            "elements": ["title"],
            "duration": 2
        })

        # Keywords
        for i in range(len(keywords)):
            animation_sequence.append({
                "step": i + 2,
                "title": f"Key Idea {i+1}",
                "action": "show_text",
                "elements": [f"kw{i}"],
                "duration": 2
            })

        return {
            "title": f"Understanding {prompt}",
            "core_concept": prompt,
            "visual_elements": visual_elements,
            "animation_sequence": animation_sequence,
            "_source": "local_llm_slide_mode"
        }

    except Exception as e:
        print("LLM fallback failed:", e)

        return {
            "title": f"Understanding {prompt}",
            "core_concept": prompt,
            "visual_elements": [
                {"id": "main", "type": "text", "description": prompt}
            ],
            "animation_sequence": [
                {
                    "step": 1,
                    "title": "Introduction",
                    "action": "show_text",
                    "elements": ["main"],
                    "duration": 3
                }
            ],
            "_source": "minimal_fallback"
        }