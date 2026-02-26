# src/local_llm_client.py

import requests
import json
import re
import ast

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"


# --------------------------
# LLM CALL
# --------------------------

def call_llm(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 2048
            }
        },
        timeout=180
    )

    response.raise_for_status()
    return response.json()["response"]


# --------------------------
# PROMPT BUILDER
# --------------------------

def build_structured_prompt(user_prompt: str) -> str:
    return f"""You are an animation planning assistant. Your ONLY job is to return a valid JSON object based on the user's topic.
DO NOT write any text other than the JSON object.
DO NOT use markdown.
DO NOT use comments.

The JSON structure is:

{{
  "title": "string",
  "description": "string",
  "scenes": [
    {{
      "id": "string",
      "title": "string",
      "objects": [ {{"id": "string", "type": "string", "params": {{}} }} ],
      "actions": [ {{"type": "string", "target": "string", "params": {{}} }} ]
    }}
  ]
}}

Allowed object types are: Text, Image, Circle, Square, Dot, Axes.
Use 'Image' objects for specific things like 'sun.png' or 'cell.png'.
Use 'Text' objects for labels.
Ensure every 'target' in an action refers to an 'id' in the objects list.

Topic: {user_prompt}

JSON:
"""


# --------------------------
# ROBUST JSON EXTRACTOR
# --------------------------

def repair_json(text: str) -> str:
    """Attempt to close open brackets/braces in truncated JSON."""
    text = text.strip()
    stack = []
    in_string = False
    escape = False

    for char in text:
        if escape:
            escape = False
            continue
        if char == '\\':
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}' or char == ']':
                if stack and stack[-1] == char:
                    stack.pop()
    
    if in_string:
        text += '"'
    
    # Close remaining
    while stack:
        text += stack.pop()
    
    return text

def _clean_ast(obj):
    """Recursively convert sets/tuples to lists for JSON serialization."""
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, list):
        return [_clean_ast(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _clean_ast(v) for k, v in obj.items()}
    return obj

def extract_json_from_text(text: str):

    if not text:
        return None

    text = text.strip()
    text = re.sub(r"```\w*", "", text)
    text = text.replace("```", "")
    text = text.replace("\ufeff", "")

    # Remove single-line comments that break JSON parsing
    text = re.sub(r"//.*", "", text)

    candidates = []

    # Strategy 1: Find the first balanced brace block (handles trailing text)
    idx = text.find("{")
    if idx != -1:
        balance = 0
        for i in range(idx, len(text)):
            if text[i] == "{":
                balance += 1
            elif text[i] == "}":
                balance -= 1
                if balance == 0:
                    candidates.append(text[idx : i + 1])
                    break

    # Strategy 2: Naive first { to last } (fallback)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        candidates.append(text[start : end + 1])

    # Strategy 3: First { to end (for truncated JSON)
    if start != -1:
        candidates.append(text[start:])

    for candidate in candidates:
        # Attempt 1: Standard JSON
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        # Attempt 2: Python literal eval (handles single quotes, None, etc.)
        try:
            # First, try a version with JSON keywords converted to Python keywords
            # This handles cases where the LLM mixes JSON keywords (true) with Python quotes (')
            py_candidate = re.sub(r':\s*true\b', ': True', candidate)
            py_candidate = re.sub(r':\s*false\b', ': False', py_candidate)
            py_candidate = re.sub(r':\s*null\b', ': None', py_candidate)
            return _clean_ast(ast.literal_eval(py_candidate))
        except (ValueError, SyntaxError):
            # If that fails, try the original candidate with ast.literal_eval
            try:
                return _clean_ast(ast.literal_eval(candidate))
            except (ValueError, SyntaxError):
                pass

        # Attempt 3: Regex repairs for trailing commas & single quotes
        try:
            fixed = candidate
            fixed = re.sub(r",\s*}", "}", fixed)
            fixed = re.sub(r",\s*]", "]", fixed)
            if "'" in fixed and '"' not in fixed:
                 fixed = fixed.replace("'", '"')
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Attempt 4: Repair truncated JSON
        try:
            repaired = repair_json(candidate)
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    return None


# --------------------------
# SAFE GENERATION
# --------------------------

def safe_generate_generic_plan(user_prompt: str):

    max_retries = 3
    for attempt in range(max_retries):
        try:
            prompt = build_structured_prompt(user_prompt)
            raw = call_llm(prompt)

            print(f"\nRAW LLM OUTPUT (Attempt {attempt+1}):\n")
            print(raw)
            print("\n--- END RAW OUTPUT ---\n")

            parsed = extract_json_from_text(raw)

            if not parsed:
                print(f"Failed to parse JSON from LLM output (Attempt {attempt+1}).")
                continue

            if not isinstance(parsed, dict):
                print(f"Invalid JSON structure (Attempt {attempt+1}).")
                continue

            if "scenes" not in parsed:
                print(f"Invalid plan format: missing 'scenes' (Attempt {attempt+1}).")
                continue

            return parsed

        except Exception as e:
            print(f"LLM JSON mode failed (Attempt {attempt+1}):", e)
            
    return None