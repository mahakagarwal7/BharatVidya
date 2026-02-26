import json
import os
import subprocess
from pathlib import Path

from src.local_llm_client import safe_generate_generic_plan
from training_pipeline import generate_manim_code
from plan_validator import validate_and_fill_plan

PLAN_DIR = Path("outputs/plans")
MANIM_DIR = Path("outputs/manim_code")

PLAN_DIR.mkdir(parents=True, exist_ok=True)
MANIM_DIR.mkdir(parents=True, exist_ok=True)


def clean_ellipsis(obj):
    """Recursively remove Python Ellipsis objects from plan."""
    if obj is ...:
        return None
    if isinstance(obj, dict):
        return {k: clean_ellipsis(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_ellipsis(v) for v in obj]
    return obj


topic = input("Enter topic: ").strip()

if not topic:
    print("No topic entered.")
    exit()

print("\nGenerating structured plan using Ollama...\n")
plan = safe_generate_generic_plan(topic)

if not plan:
    print("Planning failed.")
    exit()

# Clean possible ellipsis objects
plan = clean_ellipsis(plan)

# Debug print (optional but useful)
print("Generated Plan:")
print(json.dumps(plan, indent=2, ensure_ascii=False))

# Save raw plan safely
safe_name = topic.replace(" ", "_").replace("/", "_")
plan_path = PLAN_DIR / f"{safe_name}.json"

with open(plan_path, "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=2, ensure_ascii=False)

print(f"\nPlan saved to: {plan_path}")

# Validate & convert to Manim
plan, diagnostics = validate_and_fill_plan(plan)

if not diagnostics.get("success", True):
    print("Plan validation failed:")
    print(diagnostics)
    exit()

code, class_name = generate_manim_code(plan)

py_file = MANIM_DIR / f"{class_name}.py"

with open(py_file, "w", encoding="utf-8") as f:
    f.write(code)

print(f"\nManim script generated: {py_file}")
print("Rendering video...\n")

# Use subprocess for safer execution
import sys

cmd = [sys.executable, "-m", "manim", "-pqh", str(py_file), class_name]

try:
    subprocess.run(cmd, check=True)
    print("\nVideo rendered successfully.")
except subprocess.CalledProcessError as e:
    print("\nManim rendering failed.")
    print("Error:", e)