# src/local_llm_client.py

import json
import subprocess

MODEL_NAME = "phi3:mini"


# --------------------------------------------------
# TOPIC ANALYSIS - Context vs Simulation Classification
# --------------------------------------------------

def analyze_topic_type(concept: str) -> dict:
    """
    Analyze whether a topic is simulation-heavy or context-heavy.
    Returns analysis dict with:
      - topic_type: 'simulation' or 'context'
      - visual_approach: detailed visual strategy
      - animation_style: type of animations to use
    """
    text = str(concept).lower()

    # Simulation-heavy: needs step-by-step animated visuals
    simulation_keywords = {
        "physics": ["projectile", "trajectory", "velocity", "acceleration", "pendulum",
                   "wave", "optics", "reflection", "refraction", "gravity", "force",
                   "momentum", "collision", "oscillation", "frequency"],
        "algorithm": ["binary search", "bubble sort", "merge sort", "quick sort",
                     "insertion sort", "selection sort", "bfs", "dfs", "dijkstra",
                     "sorting", "searching", "tree traversal", "linked list"],
        "math_process": ["matrix multiplication", "determinant", "eigenvalue",
                        "integration", "differentiation", "derivative", "limit",
                        "graph", "plot", "equation solving", "factorization"],
        "chemistry": ["reaction", "titration", "oxidation", "reduction", "bonding",
                     "precipitation", "combustion", "electrolysis"],
        "biology_process": ["photosynthesis", "respiration", "cell division", "mitosis",
                           "meiosis", "digestion", "circulation", "osmosis", "diffusion"]
    }

    # Context-heavy: needs explanatory text with static visuals
    context_keywords = {
        "history": ["history", "historical", "timeline", "war", "revolution",
                   "independence", "colonial", "ancient", "medieval", "renaissance",
                   "world war", "civil war", "freedom struggle"],
        "philosophy": ["philosophy", "ethics", "morality", "existentialism",
                      "metaphysics", "epistemology", "logic", "reasoning"],
        "literature": ["poem", "poetry", "novel", "story", "literature", "drama",
                      "shakespeare", "author", "prose", "verse", "narrative"],
        "social": ["democracy", "constitution", "government", "politics", "civics",
                  "society", "culture", "economics", "capitalism", "socialism"],
        "abstract": ["theory", "concept", "principle", "law of", "theorem",
                    "definition", "meaning of", "what is", "explain"]
    }

    # Check for simulation match
    simulation_category = None
    for category, keywords in simulation_keywords.items():
        if any(k in text for k in keywords):
            simulation_category = category
            break

    # Check for context match
    context_category = None
    for category, keywords in context_keywords.items():
        if any(k in text for k in keywords):
            context_category = category
            break

    # Determine topic type (simulation takes priority for dual-matches)
    if simulation_category and not context_category:
        topic_type = "simulation"
        matched_category = simulation_category
    elif context_category and not simulation_category:
        topic_type = "context"
        matched_category = context_category
    elif simulation_category and context_category:
        # Both matched - prefer simulation for technical topics
        topic_type = "simulation"
        matched_category = simulation_category
    else:
        # Default to context for unknown topics
        topic_type = "context"
        matched_category = "general"

    # Define visual approach based on topic type
    if topic_type == "simulation":
        visual_approach = {
            "image_style": "process_diagram",
            "text_density": "minimal",
            "scene_count": 6,
            "animation_focus": True,
            "show_steps": True,
            "caption_length": "short"
        }
        animation_style = {
            "type": "step_progression",
            "transitions": ["fade", "slide"],
            "element_animations": True,
            "simulation_elements": True,
            "timing": "dynamic"
        }
    else:
        visual_approach = {
            "image_style": "concept_card",
            "text_density": "rich",
            "scene_count": 5,
            "animation_focus": False,
            "show_steps": False,
            "caption_length": "detailed"
        }
        animation_style = {
            "type": "text_reveal",
            "transitions": ["fade"],
            "element_animations": False,
            "simulation_elements": False,
            "timing": "steady"
        }

    return {
        "topic_type": topic_type,
        "category": matched_category,
        "visual_approach": visual_approach,
        "animation_style": animation_style
    }


def _is_subjective_concept(concept: str) -> bool:
    text = str(concept).lower()
    subjective_keywords = [
        "history", "philosophy", "literature", "poem", "novel", "ethics",
        "politics", "civics", "sociology", "psychology", "culture", "biography",
        "freedom struggle", "renaissance", "democracy", "constitution"
    ]
    objective_keywords = [
        "matrix", "multiplication", "vector", "equation", "calculus", "physics",
        "chemistry", "algorithm", "binary search", "bubble sort", "sine", "quadratic",
        "projectile", "probability", "statistics"
    ]

    if any(k in text for k in objective_keywords):
        return False
    if any(k in text for k in subjective_keywords):
        return True
    return False


def _filter_objective_steps(steps, concept: str):
    history_words = [
        "history", "historical", "origin", "invented", "inventor", "developed by",
        "in year", "in the year", "timeline", "century", "background", "biography"
    ]

    clean_steps = []
    for step in steps:
        step_text = str(step).strip()
        low = step_text.lower()
        if any(word in low for word in history_words):
            continue
        # Keep step if it has meaningful content
        if len(step_text) > 10:
            clean_steps.append(step_text)

    if len(clean_steps) >= 3:
        return clean_steps

    # Generate topic-specific fallback steps
    return _generate_topic_specific_steps(concept)


def _generate_topic_specific_steps(concept: str):
    """Generate descriptive fallback steps based on concept keywords."""
    text = concept.lower()
    
    # Physics concepts
    if "projectile" in text or "motion" in text:
        return [
            "An object is launched at an angle with initial velocity, creating a curved path through the air",
            "Gravity pulls the object downward while horizontal motion continues at constant speed",
            "The trajectory forms a parabola, with maximum height at the midpoint of flight"
        ]
    if "wave" in text or "oscillation" in text:
        return [
            "A disturbance creates periodic motion that transfers energy through a medium",
            "The wave oscillates between peaks and troughs with measurable frequency and amplitude",
            "Wave properties like wavelength and speed determine how energy propagates"
        ]
    
    # Math concepts
    if "matrix" in text and "multipl" in text:
        return [
            "Two matrices are arranged with rows of the first aligned with columns of the second",
            "Each element is calculated by multiplying corresponding entries and summing the products",
            "The result matrix has dimensions from the first matrix's rows and second matrix's columns"
        ]
    if "determinant" in text:
        return [
            "The determinant is calculated from matrix elements using cross-multiplication",
            "For a 2x2 matrix, multiply diagonals and subtract: ad minus bc",
            "A non-zero determinant indicates the matrix is invertible"
        ]
    if "quadratic" in text or "parabola" in text:
        return [
            "A quadratic equation has the form ax² + bx + c = 0 with a curved graph",
            "The parabola opens upward or downward depending on the sign of coefficient a",
            "Solutions are found using the quadratic formula or by factoring"
        ]
    if "linear" in text and "equation" in text:
        return [
            "A linear equation represents a straight line with constant rate of change",
            "The slope m determines steepness while b sets the y-intercept",
            "Any point on the line satisfies the equation y = mx + b"
        ]
    
    # Algorithm concepts
    if "binary" in text and "search" in text:
        return [
            "Start with a sorted array and identify the middle element",
            "Compare target with middle: search left half if smaller, right half if larger",
            "Repeat until target is found or search space is exhausted"
        ]
    if "bubble" in text or "sort" in text:
        return [
            "Compare adjacent elements and swap if they are in wrong order",
            "Larger elements bubble up to the end with each pass",
            "Repeat passes until no swaps are needed - the array is sorted"
        ]
    
    # Biology/Chemistry concepts
    if "photosynthe" in text:
        return [
            "Plants capture sunlight energy using chlorophyll in their leaves",
            "Carbon dioxide and water are converted into glucose through chemical reactions",
            "Oxygen is released as a byproduct, providing air for other organisms"
        ]
    
    # Probability
    if "probability" in text or "dice" in text or "chance" in text:
        return [
            "Each outcome has a likelihood expressed as a fraction or percentage",
            "Total probability of all possible outcomes always equals 1 or 100%",
            "Events can be independent or dependent based on how they affect each other"
        ]
    
    # Context-heavy topics (history, social, philosophy)
    if "democracy" in text:
        return [
            "Democracy is a system where citizens participate in decision-making through voting",
            "Key principles include equal rights, free elections, and protection of minorities",
            "Modern democracies balance majority rule with individual freedoms and rule of law"
        ]
    if "revolution" in text:
        return [
            "A revolution represents a fundamental change in political or social structures",
            "Causes often include inequality, oppression, and demands for representation",
            "Revolutions reshape societies and establish new systems of governance"
        ]
    if "constitution" in text:
        return [
            "A constitution establishes the fundamental principles and structure of government",
            "It defines the powers and limits of different branches of authority",
            "Constitutional rights protect citizens from arbitrary government action"
        ]
    if "philosophy" in text or "ethics" in text:
        return [
            "Philosophy examines fundamental questions about existence, knowledge, and values",
            "Different schools of thought offer varied perspectives on truth and morality",
            "Philosophical reasoning helps evaluate arguments and ethical decisions"
        ]
    
    # Generic but descriptive fallback
    return [
        f"Understanding the core definition and key components of {concept}",
        f"Examining how {concept} works through a step-by-step breakdown",
        f"Applying {concept} to real-world scenarios and practical examples"
    ]


def _call_ollama(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180
        )
        return result.stdout.decode("utf-8").strip()
    except Exception as e:
        print("Ollama call failed:", e)
        return ""


# --------------------------------------------------
# REASONING + CATEGORY GENERATOR
# --------------------------------------------------

def generate_reasoning_plan(concept: str):

    # Analyze topic type first
    topic_analysis = analyze_topic_type(concept)
    topic_type = topic_analysis["topic_type"]
    topic_category = topic_analysis["category"]

    subjective = _is_subjective_concept(concept)
    style = "subjective" if subjective else "objective"

    # Build topic-specific prompt
    if topic_type == "simulation":
        pedagogy_instructions = f"""
Pedagogy rules for SIMULATION-HEAVY topic (detected: {topic_category}):
- Focus on step-by-step process visualization
- Describe each step as an actionable simulation frame
- Include inputs, transformations, and outputs
- NO historical background, origin stories, or inventor details
- Each step should be visually demonstrable
- Think: "What would this look like animated frame-by-frame?"
"""
    else:
        pedagogy_instructions = f"""
Pedagogy rules for CONTEXT-HEAVY topic (detected: {topic_category}):
- Focus on clear explanatory text
- Provide rich context and definitions first
- Use descriptive language suitable for text overlays
- Include key concepts, significance, and relationships
- Final step can include modern relevance or application
"""

    prompt = f"""
You are an educational AI.

Explain the concept clearly and classify it.

Concept: {concept}

Classify the concept into ONE of:
- process
- structure
- hierarchy
- system
- abstract

Then provide structured explanation steps.

{pedagogy_instructions}

Detected topic type: {topic_type}
Detected pedagogy style: {style}

Return ONLY valid JSON.

Format:

{{
  "title": "Short clear title",
  "category": "one of the five",
  "pedagogy_style": "objective or subjective",
  "steps": [
    "Step 1 explanation",
    "Step 2 explanation",
    "Step 3 explanation"
  ]
}}
"""

    raw_output = _call_ollama(prompt)

    if not raw_output:
        return None

    try:
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1

        if start == -1 or end == -1:
            return None

        data = json.loads(raw_output[start:end])

        if "title" not in data or "steps" not in data:
            return None

        if not isinstance(data["steps"], list):
            return None

        if "category" not in data:
            data["category"] = "abstract"

        if data.get("pedagogy_style") not in {"objective", "subjective"}:
            data["pedagogy_style"] = style

        if data["pedagogy_style"] == "objective":
            data["steps"] = _filter_objective_steps(data["steps"], concept)

        # Guarantee minimum 3 steps
        if len(data["steps"]) < 3:
            data["steps"] = [
                f"Introduction to {concept}",
                f"Key aspects of {concept}",
                f"Applications of {concept}"
            ]

        # Include topic analysis for visual builder
        data["topic_analysis"] = topic_analysis

        return data

    except:
        return None