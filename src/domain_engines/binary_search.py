import random


def generate_binary_search_plan(prompt: str):

    arr = sorted(random.sample(range(10, 100), 7))
    target = random.choice(arr)

    elements = [
        {"id": f"bar{i}", "type": "rectangle", "value": val}
        for i, val in enumerate(arr)
    ]

    steps = []

    left, right = 0, len(arr) - 1
    step = 1

    while left <= right:
        mid = (left + right) // 2

        steps.append({
            "step": step,
            "action": "check_mid",
            "mid": mid,
            "target": target,
            "duration": 2
        })
        step += 1

        if arr[mid] == target:
            steps.append({
                "step": step,
                "action": "found",
                "mid": mid,
                "duration": 2
            })
            break
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return {
        "title": f"Binary Search (Target: {target})",
        "core_concept": prompt,
        "visual_elements": elements,
        "animation_sequence": steps
    }