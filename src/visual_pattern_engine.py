# src/visual_pattern_engine.py

def generate_visual_plan(concept: str, explanation: dict):

    concept_type = explanation.get("concept_type", "abstract")

    visual_elements = []
    animation_sequence = []

    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": explanation.get("title", concept),
        "x": 100,
        "y": 80
    })

    scene1_ids = ["title"]

    if concept_type == "structure":
        visual_elements.append({
            "id": "grid",
            "type": "grid",
            "x": 350,
            "y": 200,
            "rows": 3,
            "cols": 3,
            "values": [[1,2,3],[4,5,6],[7,8,9]]
        })
        scene1_ids.append("grid")

    elif concept_type == "flow":
        visual_elements.append({
            "id": "flow_center",
            "type": "circle",
            "x": 500,
            "y": 300,
            "radius": 10
        })
        scene1_ids.append("flow_center")

    else:
        visual_elements.append({
            "id": "concept_box",
            "type": "rectangle",
            "x": 350,
            "y": 220,
            "width": 300,
            "height": 150
        })
        scene1_ids.append("concept_box")

    animation_sequence.append({
        "elements": scene1_ids,
        "duration": 5
    })

    scene2_ids = ["title"]

    for idx, point in enumerate(explanation.get("points", [])):
        elem_id = f"text_{idx}"
        visual_elements.append({
            "id": elem_id,
            "type": "text",
            "description": point,
            "x": 150,
            "y": 200 + idx*60
        })
        scene2_ids.append(elem_id)

    animation_sequence.append({
        "elements": scene2_ids,
        "duration": 8
    })

    return {
        "visual_elements": visual_elements,
        "animation_sequence": animation_sequence
    }