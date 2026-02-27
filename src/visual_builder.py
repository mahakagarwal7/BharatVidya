# src/visual_builder.py

import math


def build_visual_plan(concept: str, reasoning: dict):

    visual_elements = []
    animation_sequence = []

    title = reasoning.get("title", concept)
    steps = reasoning.get("steps", [])
    category = reasoning.get("category", "abstract")

    # --------------------------------
    # Title
    # --------------------------------

    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": title,
        "x": 150,
        "y": 80
    })

    count = len(steps)

    # ============================================
    # CATEGORY-BASED LAYOUTS
    # ============================================

    # PROCESS → Horizontal Flow
    if category == "process":

        for i in range(count):
            visual_elements.append({
                "id": f"node_{i}",
                "type": "rectangle",
                "x": 150 + i * 180,
                "y": 300,
                "width": 140,
                "height": 60
            })

        animation_sequence.append({
            "elements": ["title"] + [f"node_{i}" for i in range(count)],
            "duration": 4
        })

    # HIERARCHY → Vertical Stack
    elif category == "hierarchy":

        for i in range(count):
            visual_elements.append({
                "id": f"node_{i}",
                "type": "rectangle",
                "x": 400,
                "y": 150 + i * 100,
                "width": 200,
                "height": 60
            })

        animation_sequence.append({
            "elements": ["title"] + [f"node_{i}" for i in range(count)],
            "duration": 4
        })

    # STRUCTURE → Grid Layout
    elif category == "structure":

        size = int(math.ceil(math.sqrt(count)))

        for i in range(count):
            row = i // size
            col = i % size

            visual_elements.append({
                "id": f"node_{i}",
                "type": "rectangle",
                "x": 300 + col * 180,
                "y": 180 + row * 120,
                "width": 150,
                "height": 80
            })

        animation_sequence.append({
            "elements": ["title"] + [f"node_{i}" for i in range(count)],
            "duration": 4
        })

    # SYSTEM → Central Hub with Satellites
    elif category == "system":

        visual_elements.append({
            "id": "central",
            "type": "circle",
            "x": 500,
            "y": 300,
            "radius": 80
        })

        radius = 200

        for i in range(count):
            angle = (2 * math.pi / max(count, 1)) * i
            x = 500 + radius * math.cos(angle)
            y = 300 + radius * math.sin(angle)

            visual_elements.append({
                "id": f"node_{i}",
                "type": "circle",
                "x": int(x),
                "y": int(y),
                "radius": 50
            })

        animation_sequence.append({
            "elements": ["title", "central"] +
                        [f"node_{i}" for i in range(count)],
            "duration": 4
        })

    # ABSTRACT → Minimal Focus Layout
    else:

        visual_elements.append({
            "id": "main",
            "type": "circle",
            "x": 500,
            "y": 300,
            "radius": 100
        })

        animation_sequence.append({
            "elements": ["title", "main"],
            "duration": 4
        })

    # --------------------------------
    # Step Explanation Scenes
    # --------------------------------

    for i, step in enumerate(steps):

        step_id = f"text_step_{i}"

        visual_elements.append({
            "id": step_id,
            "type": "text",
            "description": step,
            "x": 150,
            "y": 200
        })

        animation_sequence.append({
            "elements": ["title", step_id],
            "duration": 4
        })

    return {
        "visual_elements": visual_elements,
        "animation_sequence": animation_sequence
    }