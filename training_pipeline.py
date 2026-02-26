#!/usr/bin/env python3
"""
training_pipeline.py (FINAL FIXED VERSION + Visual Upgrades)

Upgrades added:
- Support for ImageMobject
- Support for Text positioning (top/bottom/left/right/center)
- Safe scaling for images
- Does NOT break existing structure
"""

import argparse
import json
import os
import glob
import subprocess
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
import textwrap

# Try importing PIL for asset generation
try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None

from plan_validator import validate_and_fill_plan, projectile_parametric_expr

# Output folders
ROOT = Path(".")
PLANS_GLOB = ROOT / "outputs" / "plans" / "*.json"
MANIM_DIR = ROOT / "outputs" / "manim_code"
VIDEO_DIR = ROOT / "outputs" / "videos"
DATASET_DIR = ROOT / "training" / "generated_data"

for p in (MANIM_DIR, VIDEO_DIR, DATASET_DIR):
    p.mkdir(parents=True, exist_ok=True)


# --------------------------
# Utility Functions
# --------------------------

def slugify(text: str) -> str:
    base = "".join(ch if ch.isalnum() else "_" for ch in str(text))[:30].strip("_")
    h = hashlib.sha1((str(text) + str(time.time())).encode()).hexdigest()[:8]
    return f"{base}_{h}"


def _make_valid_class_name(title: str) -> str:
    clean = "".join(ch for ch in str(title).title() if ch.isalnum())
    if not clean:
        clean = "GeneratedAnimation"
    if not clean[0].isalpha():
        clean = "Scene" + clean
    return clean


def obj_var(obj_id: str) -> str:
    return "obj_" + "".join(ch if ch.isalnum() else "_" for ch in obj_id)


# --------------------------
# Manim Code Generator
# --------------------------

def _ensure_assets(plan: Dict[str, Any]):
    """Generate placeholder images for any Image objects in the plan."""
    if not Image:
        return

    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)

    for scene in plan.get("scenes", []):
        for obj in scene.get("objects", []):
            if obj.get("type") == "Image":
                params = obj.get("params", {})
                path_str = params.get("path", "").strip()

                # Standardize path: use only the filename and put it in 'assets'
                if path_str:
                    filename = Path(path_str).name
                else:
                    safe_id = "".join(c for c in obj.get("id", "img") if c.isalnum())
                    filename = f"{safe_id}.png"

                # Update the plan with the standardized path
                standardized_path = assets_dir / filename
                params["path"] = str(standardized_path).replace('\\', '/') # Use forward slashes

                # Create placeholder if file doesn't exist
                if not standardized_path.exists():
                    try:
                        img = Image.new('RGB', (512, 512), color=(50, 50, 80))
                        d = ImageDraw.Draw(img)
                        d.text((20, 20), "Placeholder for:", fill=(255, 255, 255))
                        d.text((20, 60), f"{filename}", fill=(220, 220, 255))
                        d.text((20, 120), "To use a real image, replace this file", fill=(200, 200, 200))
                        d.text((20, 150), "in the 'assets' folder.", fill=(200, 200, 200))
                        img.save(standardized_path)
                        print(f"[Asset] Created placeholder: {standardized_path}")
                    except Exception as e:
                        print(f"[Asset] Failed to create {standardized_path}: {e}")

def generate_manim_code(plan: Dict[str, Any]) -> Tuple[str, str]:

    # Pre-generation: Ensure assets exist
    _ensure_assets(plan)

    title = plan.get("title", "Animation")
    description = plan.get("description", "")
    class_name = _make_valid_class_name(title)
    scenes = plan.get("scenes", [])

    lines = []
    lines.append("from manim import *")
    lines.append("import numpy as np")
    lines.append("import os")
    lines.append("")
    lines.append(f"class {class_name}(Scene):")
    lines.append("    def construct(self):")

    # --- Add a title card ---
    lines.append(f"        title_text = Text({repr(title)}, font_size=48).to_edge(UP)")
    lines.append(f"        self.play(Write(title_text))")
    lines.append(f"        self.wait(1.5)")
    if description:
        wrapped_desc = textwrap.fill(description, width=50)
        lines.append(f"        desc_text = Text({repr(wrapped_desc)}, font_size=24).next_to(title_text, DOWN, buff=0.5)")
        lines.append(f"        self.play(FadeIn(desc_text, shift=UP))")
        lines.append(f"        self.wait(2.5)")
        lines.append(f"        self.play(FadeOut(title_text), FadeOut(desc_text))")
    else:
        lines.append(f"        self.play(FadeOut(title_text))")
    lines.append(f"        self.wait(0.5)")

    defined_vars = set()

    for i, scene in enumerate(scenes):
        scene_vars = []
        objects = scene.get("objects", [])
        actions = scene.get("actions", [])
        hint = (scene.get("hint", "") or "").lower()

        scene_title = scene.get("title", "")
        scene_title_var = f"scene_title_{i}"
        if scene_title:
            lines.append(f"        {scene_title_var} = Text({repr(scene_title)}, font_size=36).to_edge(UP)")
            lines.append(f"        self.play(Write({scene_title_var}))")
            scene_vars.append(scene_title_var)

        # Identify objects that are explicitly introduced via animation
        introduced_ids = set()
        for act in actions:
            if isinstance(act, dict) and act.get("type") in ["Create", "FadeIn", "Write", "DrawBorderThenFill"]:
                tgt = act.get("target")
                if isinstance(tgt, list):
                    introduced_ids.update(tgt)
                else:
                    introduced_ids.add(tgt)

        # ---------------------------
        # Create Scene Objects
        # ---------------------------
        previous_text_var = None

        for obj in objects:
            oid = obj.get("id", "obj")
            otype = obj.get("type", "Dot")
            params = obj.get("params", {}) or {}
            var = obj_var(oid)
            defined_vars.add(var)
            scene_vars.append(var)

            # ---------- DOT ----------
            if otype == "Dot":
                color = repr(params.get("color", "WHITE"))
                lines.append(f"        {var} = Dot(color={color})")
                if oid not in introduced_ids:
                    lines.append(f"        self.add({var})")

            # ---------- TEXT ----------
            elif otype == "Text":
                raw_txt = params.get("text", "").strip()
                # If text is empty, use the object ID as a fallback for visibility.
                display_txt = repr(raw_txt if raw_txt else oid)
                lines.append(f"        {var} = Text({display_txt})")
                lines.append(f"        {var}.set_z_index(10)")
                if oid not in introduced_ids:
                    lines.append(f"        self.add({var})")

                # Positioning support
                position_val = params.get("position", "")
                pos = ""
                if isinstance(position_val, str):
                    pos = position_val.lower()

                if pos == "top":
                    lines.append(f"        {var}.to_edge(UP)")
                elif pos == "bottom":
                    lines.append(f"        {var}.to_edge(DOWN)")
                elif pos == "left":
                    lines.append(f"        {var}.to_edge(LEFT)")
                elif pos == "right":
                    lines.append(f"        {var}.to_edge(RIGHT)")
                elif pos == "center":
                    lines.append(f"        {var}.move_to(ORIGIN)")
                else:
                    if previous_text_var:
                        lines.append(f"        {var}.next_to({previous_text_var}, DOWN)")
                    else:
                        lines.append(f"        {var}.to_edge(UP)")
                previous_text_var = var

            # ---------- IMAGE ----------
            elif otype == "Image":
                path = params.get("path", "")
                scale = params.get("scale", 1)
                lines.append(f"        {var} = ImageMobject(os.path.abspath(r'{path}'))")
                lines.append(f"        {var}.scale({scale})")
                if oid not in introduced_ids:
                    lines.append(f"        self.add({var})")

                position_val = params.get("position", "")
                pos = ""
                if isinstance(position_val, str):
                    pos = position_val.lower()

                if pos == "top":
                    lines.append(f"        {var}.to_edge(UP)")
                elif pos == "bottom":
                    lines.append(f"        {var}.to_edge(DOWN)")
                elif pos == "left":
                    lines.append(f"        {var}.to_edge(LEFT)")
                elif pos == "right":
                    lines.append(f"        {var}.to_edge(RIGHT)")
                elif pos == "center":
                    lines.append(f"        {var}.move_to(ORIGIN)")

            # ---------- CIRCLE ----------
            elif otype == "Circle":
                radius = params.get("radius", 0.7)
                lines.append(f"        {var} = Circle(radius={radius})")
                if oid not in introduced_ids:
                    lines.append(f"        self.add({var})")

            # ---------- SQUARE ----------
            elif otype == "Square":
                side = params.get("side", 1.0)
                lines.append(f"        {var} = Square(side_length={side})")
                if oid not in introduced_ids:
                    lines.append(f"        self.add({var})")

            # ---------- AXES ----------
            elif otype == "Axes":
                xr = params.get("x_range", [0, 10])
                yr = params.get("y_range", [0, 5])
                lines.append(f"        {var} = Axes(x_range={xr}, y_range={yr})")
                lines.append(f"        self.play(Create({var}), run_time=0.5)")

            # ---------- PARAMETRIC ----------
            elif otype == "ParametricFunction":
                expr = params.get("expr", "lambda t: np.array([t, 0, 0])")
                tr = params.get("t_range", [0, 1])
                lines.append(f"        {var} = ParametricFunction({expr}, t_range={tr})")

            else:
                lines.append(f"        {var} = Dot()  # fallback object")
                if oid not in introduced_ids:
                    lines.append(f"        self.add({var})")

        # ---------------------------
        # SPECIAL CASE: Projectile Motion
        # ---------------------------
        if "projectile" in hint or "parabola" in hint or "trajectory" in hint:
            phys = (scene.get("params") or {}).get("physics", {})
            v0 = float(phys.get("v0", 12))
            ang = float(phys.get("angle_degrees", 45))
            g = float(phys.get("g", 9.81))

            expr, t_end = projectile_parametric_expr(v0, ang, g)

            lines.append(f"        traj = ParametricFunction({expr}, t_range=[0,{t_end:.4f}])")
            defined_vars.add("traj")
            lines.append("        ball = Dot(color=YELLOW)")
            defined_vars.add("ball")
            lines.append("        self.play(FadeIn(ball))")
            lines.append(f"        self.play(MoveAlongPath(ball, traj), run_time={t_end:.4f})")
            lines.append("        self.wait(0.3)")
            continue

        # ---------------------------
        # Playback Actions
        # ---------------------------
        for act in actions:
            if not isinstance(act, dict):
                continue
            
            # Handle list targets
            raw_targets = act.get("target")
            if not isinstance(raw_targets, list):
                raw_targets = [raw_targets]

            for target in raw_targets:
                atype = act.get("type")
                var = obj_var(target) if target else None
                params = act.get("params", {}) or {}
                dur = params.get("duration", 0.8)

                if var and var not in defined_vars:
                    lines.append(f"        # Skipped action for undefined object: {target}")
                    continue

                if atype == "FadeIn" and var:
                    lines.append(f"        self.play(FadeIn({var}), run_time={dur})")

                elif atype == "Create" and var:
                    lines.append(f"        self.play(Create({var}), run_time={dur})")

                elif atype == "FadeOut" and var:
                    lines.append(f"        self.play(FadeOut({var}), run_time={dur})")

                elif atype == "MoveAlongPath" and var:
                    path = params.get("path")
                    if path:
                        lines.append(f"        p_{var} = {path}")
                        lines.append(f"        self.play(MoveAlongPath({var}, p_{var}), run_time={dur})")

        lines.append("        self.wait(2)")
        
        if scene_vars:
            v_list = ", ".join(scene_vars)
            lines.append(f"        self.play(*[FadeOut(v) for v in [{v_list}] if v in self.mobjects], run_time=0.5)")

    lines.append("        self.wait(1)")

    code = "\n".join(lines)
    return code, class_name


# --------------------------
# Dataset Utility
# --------------------------

def plan_to_example(plan: Dict[str, Any]):
    code, _ = generate_manim_code(plan)
    return {
        "instruction": "Convert the JSON scene plan into Manim CE Python code.",
        "input": json.dumps(plan, ensure_ascii=False),
        "output": code
    }


# --------------------------
# Bulk Processing
# --------------------------

def process_plans(plans_dir: str = str(PLANS_GLOB), out_dataset: str = None):
    files = glob.glob(plans_dir)
    results = []
    dataset_entries = []

    for fp in files:
        plan = json.load(open(fp, "r", encoding="utf-8"))
        filled, diag = validate_and_fill_plan(plan)

        slug = slugify(filled.get("title", "plan"))
        code, class_name = generate_manim_code(filled)

        out_path = MANIM_DIR / f"{slug}.py"
        out_path.write_text(code, encoding="utf-8")

        dataset_entries.append(plan_to_example(filled))
        results.append({"slug": slug, "class": class_name})

    if out_dataset:
        p = Path(out_dataset)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            for e in dataset_entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

    return results, dataset_entries


# --------------------------
# Command Line
# --------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plans_dir", default=str(PLANS_GLOB))
    parser.add_argument("--out_dataset", default=str(DATASET_DIR / "data.jsonl"))
    args = parser.parse_args()

    results, ds = process_plans(args.plans_dir, args.out_dataset)
    print(json.dumps(results, indent=2, ensure_ascii=False))