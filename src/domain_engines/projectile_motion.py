# src/domain_engines/projectile_motion.py

def generate_projectile_plan(concept: str):

    visual_elements = []

    visual_elements.append({
        "id": "title",
        "type": "text",
        "description": "Projectile Motion",
        "x": 100,
        "y": 80
    })

    visual_elements.append({
        "id": "projectile_graph",
        "type": "projectile"
    })

    scene1_ids = ["title", "projectile_graph"]

    explanation = [
        "Object moves under gravity",
        "Follows parabolic path",
        "Horizontal velocity constant"
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