# src/domain_engines/binary_search.py

def generate_binary_search_plan(concept: str):

    arr = [1, 3, 5, 7, 9, 11]

    visual_elements = []

    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": "Binary Search",
        "x": 100,
        "y": 80
    })

    for i, val in enumerate(arr):
        visual_elements.append({
            "id": f"box{i}",
            "type": "rectangle",
            "x": 150 + i*120,
            "y": 300,
            "width": 80,
            "height": 80
        })

    scene1_ids = ["title"] + [f"box{i}" for i in range(len(arr))]

    explanation = [
        "Array must be sorted",
        "Check middle element",
        "Eliminate half each step"
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