#!/usr/bin/env python3
from pathlib import Path
import os
import json
import time
import argparse
import re
from typing import Any, Dict, Tuple
from dotenv import load_dotenv, find_dotenv

from google import genai
from google.genai import types

env = find_dotenv()
if env:
    load_dotenv(env)
else:
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"Key loaded: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:] if GEMINI_API_KEY else 'NONE'}")

client = genai.Client(api_key=GEMINI_API_KEY)

RESP_FILE = Path("outputs/enhancements.jsonl")
PLANS_DIR = Path("outputs/plans")
RESP_FILE.parent.mkdir(parents=True, exist_ok=True)
PLANS_DIR.mkdir(parents=True, exist_ok=True)

BASE_INSTRUCTION = """
You are an expert animation planner that outputs ONLY valid JSON.
Create a scene-by-scene animation plan for Manim CE (Community Edition).

STRICT REQUIREMENTS:
1. Output MUST be valid JSON only - no markdown, no explanations
2. Top-level fields: 'title' (string), 'description' (string), 'scenes' (list)
3. Each scene must have:
   - id (string), title (string)
   - objects: list with 'id', 'type' (Dot|Circle|Square|Text|Axes|Arrow|ParametricCurve), 'params' (dict)
   - actions: list with 'type', 'target', 'params'
   - hint: string indicating animation type (e.g., "projectile", "circular_motion", "morphing")
4. For physics scenes (hint contains 'projectile' or 'trajectory'):
   - Include 'params.physics' dict with:
     * v0 (float): initial velocity in m/s
     * angle_degrees (float): launch angle
     * g (float): gravity (default 9.81)

Return only valid JSON. If impossible, return {"error": "cannot_generate"}.
"""

def _extract_json(text: str) -> Tuple[Dict, str]:
    if not text or not isinstance(text, str):
        return {}, "empty_input"
    
    text = text.strip()
    cleaned = re.sub(r'^\s*```(?:json)?\s*', '', text, flags=re.MULTILINE)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned, flags=re.MULTILINE)
    
    try:
        return json.loads(cleaned), "markdown_stripped"
    except json.JSONDecodeError:
        pass
    
    obj_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', text, re.DOTALL)
    if obj_match:
        try:
            return json.loads(obj_match.group(1)), "regex_object"
        except json.JSONDecodeError:
            pass
    
    return {}, "all_methods_failed"

def enhance_to_json(user_text: str, model: str = "gemini-2.0-flash", save: bool = True) -> Dict[str, Any]:
    full_prompt = BASE_INSTRUCTION.strip() + "\n\nUser request:\n" + user_text.strip()
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
                response_mime_type='application/json'
            )
        )
        
        text = response.text if hasattr(response, 'text') else str(response)
        parsed, method = _extract_json(text)
        
        if not parsed:
            return {"error": "json_extraction_failed", "raw": text[:500]}
        
        if save:
            PLANS_DIR.mkdir(parents=True, exist_ok=True)
            fname = f"{int(time.time())}_plan.json"
            with (PLANS_DIR / fname).open("w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
        
        return parsed
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="+")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    
    q = " ".join(args.query)
    print(f"Generating plan for: {q}")
    
    result = enhance_to_json(q, save=args.save)
    print(json.dumps(result, ensure_ascii=False, indent=2))