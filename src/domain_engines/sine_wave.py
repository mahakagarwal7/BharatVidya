# src/domain_engines/sine_wave.py

def generate_sine_wave_plan(concept: str):

    visual_elements = []

    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": "Sine Wave",
        "x": 100,
        "y": 80
    })

    visual_elements.append({
        "id": "sine_graph",
        "type": "sine_wave"
    })

    scene1_ids = ["title", "sine_graph"]

    explanation = [
        "Sine wave represents periodic motion",
        "Amplitude controls height",
        "Frequency controls cycles"
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