# src/domain_engines/quadratic.py

import math


def generate_quadratic_plan(concept: str):
    """
    Premium deterministic quadratic visualization
    Compatible with:
    - 2 scene structure
    - Fade transitions
    - Progressive text reveal
    """

    # Default coefficients (can later be parsed from user input)
    a, b, c = 1, -3, 2

    discriminant = b*b - 4*a*c

    vertex_x = -b / (2*a)
    vertex_y = a*vertex_x**2 + b*vertex_x + c

    roots = []
    if discriminant >= 0:
        r1 = (-b + math.sqrt(discriminant)) / (2*a)
        r2 = (-b - math.sqrt(discriminant)) / (2*a)
        roots = [round(r1, 2), round(r2, 2)]

    equation_text = f"{a}x² + {b}x + {c} = 0"

    visual_elements = []

    # ==========================================================
    # SCENE 1 – Visual Graph Animation
    # ==========================================================

    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": "Quadratic Equation",
        "x": 100,
        "y": 80
    })

    visual_elements.append({
        "id": "equation",
        "type": "text",
        "description": equation_text,
        "x": 350,
        "y": 130
    })

    # Custom graph primitive (handled in renderer)
    visual_elements.append({
        "id": "quadratic_graph",
        "type": "quadratic_graph",
        "a": a,
        "b": b,
        "c": c,
        "vertex": [vertex_x, vertex_y],
        "roots": roots
    })

    scene1_ids = ["title", "equation", "quadratic_graph"]

    # ==========================================================
    # SCENE 2 – Explanation
    # ==========================================================

    explanation_points = [
        f"Discriminant = {discriminant}",
        f"Vertex at ({round(vertex_x,2)}, {round(vertex_y,2)})"
    ]

    if roots:
        explanation_points.append(f"Roots are {roots[0]} and {roots[1]}")
    else:
        explanation_points.append("No real roots")

    scene2_ids = ["title"]

    for idx, point in enumerate(explanation_points):
        elem_id = f"text_{idx}"
        visual_elements.append({
            "id": elem_id,
            "type": "text",
            "description": point,
            "x": 150,
            "y": 200 + idx * 60
        })
        scene2_ids.append(elem_id)

    animation_sequence = [
        {
            "elements": scene1_ids,
            "duration": 5
        },
        {
            "elements": scene2_ids,
            "duration": 8
        }
    ]

    return {
        "visual_elements": visual_elements,
        "animation_sequence": animation_sequence
    }