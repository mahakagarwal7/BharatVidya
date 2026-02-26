# src/topic_router.py

def detect_topics(prompt: str):
    p = prompt.lower()
    topics = []

    if "bubble" in p or "sort" in p:
        topics.append("bubble_sort")

    if "binary search" in p:
        topics.append("binary_search")

    if "quadratic" in p:
        topics.append("quadratic")

    if "sine" in p or "wave" in p:
        topics.append("sine")

    if "projectile" in p:
        topics.append("projectile")

    if not topics:
        topics.append("generic")

    return topics