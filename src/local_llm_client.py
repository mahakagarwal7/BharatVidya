# src/local_llm_client.py

"""
Ollama-based content extraction for educational video generation.
Always uses Ollama to analyze topics and extract structured educational content.
"""

import json
import subprocess

MODEL_NAME = "phi3:mini"


def _call_ollama(prompt: str) -> str:
    """Call Ollama CLI and return raw text output."""
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
        print(f"⚠️ Ollama call failed: {e}")
        return ""


def _parse_json_from_text(text: str) -> dict:
    """Extract JSON object from Ollama's text output."""
    if not text:
        return {}
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            return {}
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {}


def extract_content(concept: str) -> dict:
    """
    Extract structured educational content from Ollama.
    
    Always calls Ollama to get rich, topic-aware content.
    Falls back to a basic structure only if Ollama is completely unavailable.
    
    Returns:
        {
            "title": "Clear descriptive title",
            "summary": "One paragraph overview",
            "category": "physics|math|algorithm|biology|chemistry|history|philosophy|general",
            "sections": [
                {
                    "heading": "Section heading",
                    "body": "Detailed explanation paragraph",
                    "key_points": ["Point 1", "Point 2"]
                }
            ],
            "key_facts": ["Important equation or fact"],
            "visual_style": "simulation|diagram|text_focused|mixed"
        }
    """
    clean_concept = concept.strip()
    if len(clean_concept.split()) < 2:
        clean_concept = f"Explain the concept of {clean_concept}"

    prompt = f"""You are an expert educational content creator.

Analyze and explain the following concept in a way suitable for an educational video.

Concept: {clean_concept}

Return ONLY valid JSON in this exact format:

{{
  "title": "A clear, concise title for the video",
  "summary": "A one-paragraph overview of the concept (2-3 sentences)",
  "category": "one of: physics, math, algorithm, biology, chemistry, history, philosophy, social, literature, general",
  "sections": [
    {{
      "heading": "Section 1 title",
      "body": "Detailed explanation of this aspect (2-3 sentences)",
      "key_points": ["Key point 1", "Key point 2"]
    }},
    {{
      "heading": "Section 2 title",
      "body": "Detailed explanation of this aspect (2-3 sentences)",
      "key_points": ["Key point 1", "Key point 2"]
    }},
    {{
      "heading": "Section 3 title",
      "body": "Detailed explanation of this aspect (2-3 sentences)",
      "key_points": ["Key point 1", "Key point 2"]
    }}
  ],
  "key_facts": ["Important equation, formula, or memorable fact"],
  "visual_style": "one of: simulation, diagram, text_focused, mixed"
}}

Rules:
- Provide exactly 3 sections
- Each section should teach one clear aspect
- Key points should be short and memorable
- The body text should be educational and engaging
- Focus on WHAT it is, HOW it works, and WHY it matters
- Return ONLY the JSON, no other text
"""

    print(f"🧠 Extracting content from Ollama for: {clean_concept}")
    raw_output = _call_ollama(prompt)
    data = _parse_json_from_text(raw_output)

    if data and "title" in data and "sections" in data:

        valid_sections = []
        for section in data.get("sections", []):
            if isinstance(section, dict) and "heading" in section:
                section.setdefault("body", section.get("heading", ""))
                section.setdefault("key_points", [])
                if isinstance(section["key_points"], str):
                    section["key_points"] = [section["key_points"]]
                valid_sections.append(section)
        
        if len(valid_sections) >= 2:
            data["sections"] = valid_sections[:3]  # Cap at 3 for 40-50s video
            data.setdefault("summary", f"An educational overview of {clean_concept}")
            data.setdefault("category", "general")
            data.setdefault("key_facts", [])
            data.setdefault("visual_style", "mixed")
            print(f"   ✅ Extracted {len(valid_sections)} sections from Ollama")
            return data


    print("   ⚠️ First attempt failed, trying simpler prompt...")
    
    simple_prompt = f"""Explain "{clean_concept}" as an educational topic.

Return ONLY valid JSON:

{{
  "title": "Title",
  "summary": "Overview in 2 sentences",
  "category": "general",
  "sections": [
    {{"heading": "What it is", "body": "Explanation", "key_points": ["point1"]}},
    {{"heading": "How it works", "body": "Explanation", "key_points": ["point1"]}},
    {{"heading": "Why it matters", "body": "Explanation", "key_points": ["point1"]}}
  ],
  "key_facts": ["One key fact"],
  "visual_style": "mixed"
}}
"""
    
    raw_output = _call_ollama(simple_prompt)
    data = _parse_json_from_text(raw_output)
    
    if data and "title" in data and "sections" in data:
        data.setdefault("summary", f"An educational overview of {clean_concept}")
        data.setdefault("category", "general")
        data.setdefault("key_facts", [])
        data.setdefault("visual_style", "mixed")
        print(f"   ✅ Extracted content from Ollama (simple prompt)")
        return data

    print("   ❌ Ollama unavailable, using minimal fallback")
    return {
        "title": clean_concept,
        "summary": f"An educational overview of {clean_concept}.",
        "category": "general",
        "sections": [
            {
                "heading": f"Understanding {clean_concept}",
                "body": f"This section introduces the core concept of {clean_concept} and its fundamental principles.",
                "key_points": [f"Core definition of {clean_concept}"]
            },
            {
                "heading": f"How {clean_concept} Works",
                "body": f"A step-by-step breakdown of how {clean_concept} operates and its key mechanisms.",
                "key_points": [f"Key mechanism of {clean_concept}"]
            },
            {
                "heading": f"Applications of {clean_concept}",
                "body": f"Real-world applications and practical examples of {clean_concept} in action.",
                "key_points": [f"Practical use of {clean_concept}"]
            }
        ],
        "key_facts": [f"{clean_concept} is a fundamental concept"],
        "visual_style": "text_focused"
    }