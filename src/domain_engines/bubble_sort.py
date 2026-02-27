# src/domain_engines/bubble_sort.py

def generate_bubble_sort_plan(concept: str):

    arr = [5, 3, 8, 1, 2]

    visual_elements = []

    # Scene 1 – Array Visual
    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": "Bubble Sort",
        "x": 100,
        "y": 80
    })

    for i, val in enumerate(arr):
        visual_elements.append({
            "id": f"bar{i}",
            "type": "rectangle",
            "x": 200 + i*120,
            "y": 400 - val*20,
            "width": 60,
            "height": val*20
        })

    scene1_ids = ["title"] + [f"bar{i}" for i in range(len(arr))]

    # Scene 2 – Explanation
    explanation = [
        "Compare adjacent elements",
        "Swap if out of order",
        "Repeat until sorted"
    ]

    scene2_ids = ["title"]

    for idx, point in enumerate(explanation):
        elem_id = f"text_{idx}"
        visual_elements.append({
            "id": elem_id,
            "type": "text",
            "description": point,
            "x": 150,
            "y": 200 + idx*60
        })
        scene2_ids.append(elem_id)

    return {
        "visual_elements": visual_elements,
        "animation_sequence": [
            {"elements": scene1_ids, "duration": 5},
            {"elements": scene2_ids, "duration": 8}
        ]
    }