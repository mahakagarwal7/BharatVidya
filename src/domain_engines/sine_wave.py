import math


def generate_sine_wave_plan(prompt: str):

    elements = [
        {"id": "wave", "type": "wave"}
    ]

    steps = [
        {"step": 1, "action": "animate_wave", "duration": 6}
    ]

    return {
        "title": "Sine Wave Animation",
        "core_concept": prompt,
        "visual_elements": elements,
        "animation_sequence": steps
    }