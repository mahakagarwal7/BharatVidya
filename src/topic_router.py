# src/topic_router.py

def detect_topic(concept: str) -> str:

    text = concept.lower()

    # Bubble Sort
    if "bubble sort" in text:
        return "bubble_sort"

    # Binary Search
    if "binary search" in text:
        return "binary_search"

    # Quadratic
    if "quadratic" in text or "ax^2" in text:
        return "quadratic"

    # Sine Wave
    if "sine" in text or "sin wave" in text:
        return "sine_wave"

    # Projectile Motion
    if "projectile" in text:
        return "projectile_motion"

    return "generic"