import random
import math


def generate_projectile_plan(prompt: str):

    velocity = random.randint(30, 60)
    angle_deg = random.randint(30, 60)
    angle = math.radians(angle_deg)

    elements = [
        {
            "id": "projectile",
            "type": "projectile",
            "velocity": velocity,
            "angle": angle
        }
    ]

    steps = [
        {"step": 1, "action": "animate_projectile", "duration": 6}
    ]

    return {
        "title": f"Projectile Motion (v={velocity}, θ={angle_deg}°)",
        "core_concept": prompt,
        "visual_elements": elements,
        "animation_sequence": steps
    }