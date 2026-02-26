import random
import math


def generate_quadratic_plan(prompt: str):

    # Generate non-trivial quadratic
    a = random.randint(1, 3)
    b = random.randint(-6, 6)
    c = random.randint(-6, 6)

    discriminant = b*b - 4*a*c

    # Compute roots if real
    roots = []
    if discriminant >= 0:
        r1 = (-b + math.sqrt(discriminant)) / (2*a)
        r2 = (-b - math.sqrt(discriminant)) / (2*a)
        roots = [r1, r2]

    # Vertex
    vertex_x = -b / (2*a)
    vertex_y = a*vertex_x**2 + b*vertex_x + c

    elements = [
        {
            "id": "parabola",
            "type": "parabola",
            "a": a,
            "b": b,
            "c": c
        },
        {
            "id": "vertex",
            "type": "point",
            "x": vertex_x,
            "y": vertex_y
        }
    ]

    if roots:
        elements.append({
            "id": "roots",
            "type": "roots",
            "values": roots
        })

    steps = [
        {
            "step": 1,
            "action": "show_equation",
            "duration": 2
        },
        {
            "step": 2,
            "action": "plot_parabola",
            "duration": 3
        },
        {
            "step": 3,
            "action": "highlight_vertex",
            "duration": 2
        }
    ]

    if roots:
        steps.append({
            "step": 4,
            "action": "show_roots",
            "duration": 2
        })

    return {
        "title": "Quadratic Equation Visualization",
        "core_concept": prompt,
        "visual_elements": elements,
        "animation_sequence": steps
    }