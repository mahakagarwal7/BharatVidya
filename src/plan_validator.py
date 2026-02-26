from typing import Dict


def normalize_plan(data: Dict):

    if "scenes" not in data or not isinstance(data["scenes"], list):
        data["scenes"] = []

    for scene in data["scenes"]:

        scene.setdefault("title", "Untitled Scene")
        scene.setdefault("description", "")
        scene.setdefault("objects", [])
        scene.setdefault("animations", [])

        safe_animations = []

        for anim in scene["animations"]:

            if not isinstance(anim, dict):
                continue

            safe_anim = {
                "type": anim.get("type", "fade_in"),
                "target": anim.get("target", None),
                "params": anim.get("params", {}),
                "duration": min(anim.get("duration", 2), 2)
            }

            safe_animations.append(safe_anim)

        if not safe_animations:
            safe_animations.append({
                "type": "fade_in",
                "target": None,
                "params": {},
                "duration": 2
            })

        scene["animations"] = safe_animations

    return data


def validate_plan(data: Dict):
    data = normalize_plan(data)

    if not data["scenes"]:
        raise ValueError("No valid scenes generated")

    return data