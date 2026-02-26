#!/usr/bin/env python3
"""
genai_enhancer.py — FIXED import error
"""
from pathlib import Path
import os
import json
import time
import argparse
import re
from typing import Any, Dict, Tuple
from dotenv import load_dotenv, find_dotenv

# LINE 17: CORRECT IMPORT for new SDK
from google import genai
from google.genai import types

# Load env
env = find_dotenv()
if env:
    load_dotenv(env)
else:
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

# Initialize client
client = genai.Client(api_key=GEMINI_API_KEY)

# Paths
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

def _save_record(query: str, rec: Dict[str, Any]):
    r = {"ts": int(time.time()), "query": query, "rec": rec}
    try:
        with RESP_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    except Exception:
        pass

def _extract_json(text: str) -> Tuple[Dict, str]:
    if not text or not isinstance(text, str):
        return {}, "empty_input"
    
    text = text.strip()
    
    # Remove markdown fences
    cleaned = re.sub(r'^\s*```(?:json)?\s*', '', text, flags=re.MULTILINE)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned, flags=re.MULTILINE)
    
    try:
        return json.loads(cleaned), "markdown_stripped"
    except json.JSONDecodeError:
        pass
    
    # Find JSON object
    obj_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', text, re.DOTALL)
    if obj_match:
        try:
            return json.loads(obj_match.group(1)), "regex_object"
        except json.JSONDecodeError:
            pass
    
    return {}, "all_methods_failed"

def enhance_to_json(
    user_text: str, 
    model: str = "gemini-2.0-flash",
    max_tokens: int = 2048,
    attempts: int = 3,
    save: bool = True,
    temperature: float = 0.1
) -> Dict[str, Any]:
    
    full_prompt = BASE_INSTRUCTION.strip() + "\n\nUser request:\n" + user_text.strip()
    record = {
        "model": model,
        "start_time": time.time(),
        "attempts": [],
        "final_status": "failed"
    }
    
    current_temp = temperature
    
    for attempt in range(attempts):
        attempt_record = {
            "attempt": attempt + 1,
            "temperature": current_temp,
            "timestamp": time.time()
        }
        
        try:
            # CORRECT API CALL for new SDK
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=current_temp,
                    max_output_tokens=max_tokens,
                    response_mime_type='application/json',
                    top_p=0.95,
                    top_k=40
                )
            )
            
            text = response.text if hasattr(response, 'text') else str(response)
            attempt_record["raw_response_length"] = len(text)
            
            if not text or not text.strip():
                attempt_record["error"] = "empty_response"
                record["attempts"].append(attempt_record)
                current_temp = min(0.8, current_temp + 0.15)
                continue
            
            parsed, method = _extract_json(text)
            attempt_record["extraction_method"] = method
            
            if not parsed:
                attempt_record["error"] = "json_extraction_failed"
                attempt_record["raw_sample"] = text[:500]
                record["attempts"].append(attempt_record)
                current_temp = min(0.8, current_temp + 0.15)
                continue
            
            if parsed.get("error") == "cannot_generate":
                attempt_record["error"] = "model_cannot_generate"
                record["attempts"].append(attempt_record)
                continue
            
            # Validate
            try:
                from plan_validator import validate_and_fill_plan
                filled, diag = validate_and_fill_plan(parsed)
            except ImportError:
                filled, diag = parsed, {"auto_filled": False, "validator": "not_available"}
            
            meta = filled.setdefault("meta", {})
            meta["confidence"] = "low" if diag.get("auto_filled") else "high"
            meta["extraction_method"] = method
            meta["attempts_needed"] = attempt + 1
            meta["model"] = model
            
            record["final_status"] = "success"
            record["validation_diag"] = diag
            record["total_time"] = time.time() - record["start_time"]
            _save_record(user_text, record)
            
            if save:
                safe_title = (filled.get("title") or "plan").strip().replace(" ", "_")[:40]
                safe_title = re.sub(r'[^\w\-_]', '', safe_title)
                fname = f"{int(time.time())}_{safe_title}.json"
                try:
                    with (PLANS_DIR / fname).open("w", encoding="utf-8") as f:
                        json.dump(filled, f, ensure_ascii=False, indent=2)
                    meta["saved_to"] = str(PLANS_DIR / fname)
                except Exception as e:
                    meta["save_error"] = str(e)
            
            return filled
            
        except Exception as e:
            attempt_record["error"] = str(e)
            record["attempts"].append(attempt_record)
            current_temp = min(0.8, current_temp + 0.2)
    
    record["total_time"] = time.time() - record["start_time"]
    _save_record(user_text, record)
    
    return {
        "error": "enhancement_failed",
        "details": record,
        "fallback_available": True
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="+")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--model", default="gemini-2.0-flash")
    
    args = parser.parse_args()
    q = " ".join(args.query)
    
    print(f"Generating plan for: {q[:100]}...")
    plan = enhance_to_json(q, model=args.model, save=args.save)
    
    if "error" in plan:
        print(f"\n❌ Failed: {plan['error']}")
        print(json.dumps(plan.get("details", {}), indent=2))
        exit(1)
    else:
        print(f"\n✅ Success! Confidence: {plan.get('meta', {}).get('confidence', 'unknown')}")
        print(json.dumps(plan, ensure_ascii=False, indent=2))