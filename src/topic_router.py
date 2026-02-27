# src/topic_router.py

import re

def detect_topic(concept: str) -> str:

    text = concept.lower()

    # Bubble Sort
    if "bubble sort" in text:
        return "bubble_sort"

    # Binary Search
    if "binary search" in text:
        return "binary_search"

    # Quadratic / Parabola / Second Degree
    quadratic_patterns = [
        r"x\^?2",          # x^2 or x2
        r"\bx²\b",         # x²
        r"quadratic",
        r"parabola",
        r"second degree",
        r"ax\^?2",
        r"discriminant",
        r"roots? of"
    ]

    for pattern in quadratic_patterns:
        if re.search(pattern, text):
            return "quadratic"

    # Sine Wave
    if "sine" in text or "sin wave" in text or "sin(x)" in text:
        return "sine_wave"

    # Projectile Motion
    if "projectile" in text or "launch angle" in text:
        return "projectile_motion"

    return "generic"