import random

def generate_bubble_sort_plan(prompt: str):

    values = random.sample(range(30, 120), 5)

    elements = []
    for i, val in enumerate(values):
        elements.append({
            "id": f"bar{i}",
            "type": "rectangle",
            "value": val
        })

    steps = []
    arr = values[:]
    step_num = 1

    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):

            steps.append({
                "step": step_num,
                "action": "compare",
                "indices": [j, j+1],
                "duration": 1.2
            })
            step_num += 1

            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

                steps.append({
                    "step": step_num,
                    "action": "swap",
                    "indices": [j, j+1],
                    "duration": 1.8
                })
                step_num += 1

    return {
        "title": "Bubble Sort Visualization",
        "core_concept": prompt,
        "visual_elements": elements,
        "animation_sequence": steps
    }