# src/topic_router.py

"""
Topic detection and animation routing.
Detects topic type from concept text and optionally provides animation clips.
"""

import re
from typing import Optional, Tuple, Any


__all__ = [
    "detect_topic",
    "has_animation",
    "has_specialized_animation",
    "get_animation_clip",
    "get_animation_info",
]


def detect_topic(concept: str) -> str:
    """
    Detect the topic category from concept text.
    Returns topic identifier string.
    
    IMPORTANT: Only returns animated topics when the concept is 
    specifically about that topic, NOT when it's a related but different concept.
    """
    text = concept.lower()
    
    # ============================================
    # Exclusion patterns - topics that should NOT match animations
    # even if they contain animation keywords
    # ============================================
    
    # Data structure topics (not algorithm animations)
    data_structure_patterns = [
        r"linked\s*list",
        r"tree\s+(insertion|deletion|traversal|node)",
        r"binary\s+search\s+tree",  # BST is different from binary search algorithm
        r"bst\b",
        r"heap\b",
        r"stack\b",
        r"queue\b",
        r"graph\b",
        r"hash\s*(table|map)",
        r"array\s+(insertion|deletion)",
    ]
    
    for pattern in data_structure_patterns:
        if re.search(pattern, text):
            return "generic"  # These get card-based presentation, not algorithm animation
    
    # ============================================
    # Specific topic detection (strict matching)
    # ============================================
    
    # Bubble Sort - only if specifically about bubble sort algorithm
    if "bubble sort" in text and "tree" not in text:
        return "bubble_sort"

    # Binary Search - algorithm only, NOT binary search tree
    # Must have "binary search" but NOT "tree" or "bst"
    if "binary search" in text:
        if "tree" not in text and "bst" not in text and "node" not in text:
            return "binary_search"

    # Quadratic / Parabola / Second Degree
    quadratic_patterns = [
        r"\bquadratic\s+(equation|function|formula)",
        r"\bparabola\b",
        r"second\s+degree\s+(equation|polynomial)",
        r"\bax\^?2\s*[+-]",
        r"\bdiscriminant\b",
        r"roots?\s+of\s+(a\s+)?quadratic",
    ]

    for pattern in quadratic_patterns:
        if re.search(pattern, text):
            return "quadratic"

    # Sine Wave - physics/math sine waves
    sine_patterns = [
        r"\bsine\s+wave\b",
        r"\bsin\s*\(\s*x\s*\)",
        r"sinusoidal",
        r"trigonometric\s+wave",
    ]
    for pattern in sine_patterns:
        if re.search(pattern, text):
            return "sine_wave"

    # Projectile Motion - physics topic
    projectile_patterns = [
        r"\bprojectile\s+motion\b",
        r"\bprojectile\b.*\b(trajectory|angle|velocity)\b",
        r"\blaunch\s+angle\b",
        r"\bparabolic\s+trajectory\b",
    ]
    for pattern in projectile_patterns:
        if re.search(pattern, text):
            return "projectile_motion"

    # Pendulum - physics topic
    pendulum_patterns = [
        r"\bpendulum\b",
        r"\bsimple\s+harmonic\s+motion\b",
        r"\bshm\b",
    ]
    for pattern in pendulum_patterns:
        if re.search(pattern, text):
            return "pendulum"

    # ============================================
    # Additional topic-specific animations
    # ============================================

    # Linear Equation / Linear Function / Graphical analysis of lines
    linear_patterns = [
        r"\blinear\s+(equation|function|graph)",
        r"\bslope\b.*\b(intercept|line)\b",
        r"\by\s*=\s*m\s*x",
        r"\bstraight\s+line\b",
        r"\bgraph(ical)?\s+(analysis|of)\s+.*linear",
        r"\bline(ar)?\s+graph\b",
        r"\bgraph\s+of\s+.*line\b",
    ]
    for pattern in linear_patterns:
        if re.search(pattern, text):
            return "linear_equation"

    # Heat / Thermodynamics / Temperature
    heat_patterns = [
        r"\bheat\b.*\b(transfer|flow|energy)\b",
        r"\b(heat|thermal)\s+(and\s+)?temperature\b",
        r"\bthermodynamics\b",
        r"\bthermal\s+(energy|equilibrium|conductivity)\b",
        r"\bconduction\b|\bconvection\b|\bradiation\b",
        r"\bspecific\s+heat\b",
        r"\blatent\s+heat\b",
    ]
    for pattern in heat_patterns:
        if re.search(pattern, text):
            return "heat"

    # Geometry / Shapes
    # Check coordinate geometry FIRST (more specific)
    coordinate_patterns = [
        r"\bcoordinate\s+geometr(y|ic)",
        r"\bdistance\s+formula\b",
        r"\bmidpoint\s+(formula|theorem)",
        r"\bplotting\s+points\b",
        r"\bcartesian\s+(plane|coordinate)",
        r"\bgraphical\s+analysis\b",
        r"\bgraph\s+plotting\b",
        r"\bcoordinate\s+system\b",
        r"\bpoint(s)?\s+on\s+(a\s+)?plane\b",
    ]
    for pattern in coordinate_patterns:
        if re.search(pattern, text):
            return "coordinate_geometry"

    # General Geometry / Shapes (after coordinate geometry check)
    geometry_patterns = [
        r"\bgeometr(y|ic)\b",
        r"\b(triangle|square|circle|rectangle)\s+(area|perimeter|properties)",
        r"\bpythagoras\b|\bpythagorean\b",
        r"\bangle(s)?\s+(of|in|measurement)",
        r"\bpolygon\b",
        r"\bcongruence\b|\bsimilarity\b",
        r"\barea\s+and\s+perimeter\b",
    ]
    for pattern in geometry_patterns:
        if re.search(pattern, text):
            return "geometry"

    # ============================================
    # Check Organic Chemistry BEFORE general chemistry (more specific)
    # ============================================
    
    # Organic Chemistry (check first - more specific)
    organic_patterns = [
        r"\borganic\s+chem(istry|ical)\b",
        r"\bcarbon\s+(chain|compound|atom)s?\b",
        r"\bhydrocarbon(s)?\b",
        r"\bfunctional\s+group(s)?\b",
        r"\b(alkane|alkene|alkyne|alcohol|aldehyde|ketone|ester|ether)(s)?\b",
        r"\b(methane|ethane|propane|butane|ethanol|methanol)\b",
        r"\biupac\s+nam(e|ing)\b",
        r"\bisomer(s|ism)?\\b",
        r"\bhomolog(ous|y)\b",
        r"\bsaturated\s+(and\s+)?unsaturated\b",
        r"\bcombustion\s+(of\s+)?(hydro)?carbon\b",
        r"\bcarboxylic\s+acid\b",
        r"\b(addition|substitution|elimination)\s+reaction\b",
    ]
    for pattern in organic_patterns:
        if re.search(pattern, text):
            return "organic_chemistry"

    # Organic Reactions (more specific)
    organic_reaction_patterns = [
        r"\borganic\s+reaction(s)?\b",
        r"\bcombustion\s+reaction\b",
        r"\bpolymer(ization)?\b",
        r"\bferment(ation)?\b",
        r"\bhydrolysis\b",
        r"\boxidation\s+of\s+alcohol\b",
        r"\besterification\b",
    ]
    for pattern in organic_reaction_patterns:
        if re.search(pattern, text):
            return "organic_reaction"

    # Physical Chemistry (Thermodynamics, Kinetics, Gas Laws)
    physical_chem_patterns = [
        r"\bgas\s+law(s)?\b",
        r"\bboyle'?s?\s+law\b",
        r"\bcharles'?\s+law\b",
        r"\bideal\s+gas\b",
        r"\bpv\s*=\s*nrt\b",
        r"\bchemical\s+kinetics\b",
        r"\breaction\s+rate(s)?\b",
        r"\bactivation\s+energy\b",
        r"\bequilibrium\s+constant\b",
        r"\ble\s+chatelier",
    ]
    for pattern in physical_chem_patterns:
        if re.search(pattern, text):
            return "physical_chemistry"

    # Inorganic Chemistry (Periodic Table, Crystal Structures)
    inorganic_chem_patterns = [
        r"\bcrystal\s+(lattice|structure|system)",
        r"\bunit\s+cell\b",
        r"\bcoordination\s+(compound|chemistry|number)",
        r"\bligand(s)?\b",
        r"\btransition\s+metal(s)?\b",
        r"\bmetallurgy\b",
        r"\bperiodic\s+trend(s)?\b",
        r"\bionization\s+energy\b",
    ]
    for pattern in inorganic_chem_patterns:
        if re.search(pattern, text):
            return "inorganic_chemistry"

    # General Chemistry / Atoms / Molecules (after organic chemistry check)
    chemistry_patterns = [
        r"\bchem(istry|ical)\b",
        r"\batom(ic|s)?\b",
        r"\bmolecule(s|ar)?\b",
        r"\belectron(s)?\b.*\b(orbit|shell|configuration)\b",
        r"\bperiodic\s+table\b",
        r"\bchemical\s+(bond|reaction|equation)",
        r"\bion(s|ic)?\b",
        r"\bvalence\b",
    ]
    for pattern in chemistry_patterns:
        if re.search(pattern, text):
            return "chemistry"

    # Wave / Wave motion (general physics)
    wave_patterns = [
        r"\bwave\s+(motion|propagation|nature)\b",
        r"\b(transverse|longitudinal)\s+wave\b",
        r"\bwavelength\b",
        r"\bamplitude\b.*\b(wave|frequency)\b",
        r"\bfrequency\b.*\bwave\b",
        r"\bwave\s+(interference|diffraction)\b",
        r"\bsound\s+wave\b",
        r"\blight\s+wave\b",
    ]
    for pattern in wave_patterns:
        if re.search(pattern, text):
            return "wave"

    # Statistics / Data Analysis
    statistics_patterns = [
        r"\bstatistics\b",
        r"\bmean\b.*\b(median|mode)\b",
        r"\bstandard\s+deviation\b",
        r"\bprobability\s+distribution\b",
        r"\bbar\s+(chart|graph)\b",
        r"\bhistogram\b",
        r"\bdata\s+(analysis|visualization)\b",
        r"\bnormal\s+distribution\b",
        r"\bregression\b",
    ]
    for pattern in statistics_patterns:
        if re.search(pattern, text):
            return "statistics"

    # Electric Circuits
    circuit_patterns = [
        r"\belectric\s+circuit\b",
        r"\bcircuit\s+(diagram|analysis)\b",
        r"\bohm'?s?\s+law\b",
        r"\bresist(or|ance)\b.*\bcircuit\b",
        r"\bvoltage\b.*\bcurrent\b",
        r"\bcurrent\b.*\bvoltage\b",
        r"\bseries\s+(and\s+)?parallel\s+circuit",
        r"\bkirchh?off'?s?\s+law\b",
        r"\bcapacitor\b.*\bcircuit\b",
    ]
    for pattern in circuit_patterns:
        if re.search(pattern, text):
            return "circuit"

    # Optics / Light
    optics_patterns = [
        r"\boptics\b",
        r"\blight\s+(reflection|refraction)\b",
        r"\breflection\s+(of\s+)?light\b",
        r"\brefraction\s+(of\s+)?light\b",
        r"\bsnell'?s?\s+law\b",
        r"\brefractive\s+index\b",
        r"\bmirror\s+(image|reflection)\b",
        r"\blens\s+(formula|equation)\b",
        r"\btotal\s+internal\s+reflection\b",
        r"\bangle\s+of\s+(incidence|reflection|refraction)\b",
    ]
    for pattern in optics_patterns:
        if re.search(pattern, text):
            return "optics"

    # Force / Newton's Laws
    force_patterns = [
        r"\bnewton'?s?\s+(first|second|third)\s+law\b",
        r"\bnewton'?s?\s+laws?\s+(of\s+)?motion\b",
        r"\bforce\s+(and\s+)?(motion|acceleration)\b",
        r"\b(motion|acceleration)\s+(and\s+)?force\b",
        r"\bforce\s+vector(s)?\b",
        r"\bf\s*=\s*m\s*a\b",
        r"\bfriction(al)?\s+force\b",
        r"\bnet\s+force\b",
        r"\bfree\s+body\s+diagram\b",
        r"\baction\s+(and\s+)?reaction\b",
        r"\bequilibrium\s+of\s+forces\b",
        r"\bapplied\s+force\b",
        r"\bforces\s+on\b",
    ]
    for pattern in force_patterns:
        if re.search(pattern, text):
            return "force"

    # Electromagnetic Induction / Faraday's Law (check BEFORE magnetic - more specific)
    em_induction_patterns = [
        r"\belectromagnetic\s+induction\b",
        r"\bfaraday'?s?\s+law\b",
        r"\blenz'?s?\s+law\b",
        r"\binduced\s+(emf|current|voltage)\b",
        r"\bflux\s+(change|linkage)\b",
        r"\bgenerator\s+(principle|working)\b",
        r"\btransformer\s+(principle|working)\b",
        r"\bmotor\s+(principle|effect)\b",
        r"\bac\s+generator\b",
        r"\bdc\s+motor\b",
    ]
    for pattern in em_induction_patterns:
        if re.search(pattern, text):
            return "electromagnetic"

    # Magnetic Field / Magnetism (after electromagnetic induction)
    magnetic_patterns = [
        r"\bmagnetic\s+field\s*(lines?)?\b",
        r"\bfield\s+lines?\s*(of\s+)?magnet",
        r"\bmagnet(ism|ic)?\b.*\b(field|pole|force)\b",
        r"\b(north|south)\s+pole\b.*\bmagnet",
        r"\bbar\s+magnet\b",
        r"\belectromagnet\b",  # Just electromagnet (device), not electromagnetic induction
        r"\bmagnetic\s+(flux|force)\b",  # Removed "induction" - that goes to electromagnetic
        r"\biron\s+filing(s)?\b",
        r"\bcompass\s+needle\b",
        r"\bearth'?s?\s+magnetic\s+field\b",
    ]
    for pattern in magnetic_patterns:
        if re.search(pattern, text):
            return "magnetic_field"

    # Gravity / Gravitational Force
    gravity_patterns = [
        r"\bgravit(y|ational)\b",
        r"\bfree\s+fall\b",
        r"\bweight\s+(and\s+)?mass\b",
        r"\bg\s*=\s*9\.8",
        r"\bacceleration\s+due\s+to\s+gravity\b",
        r"\bnewton'?s?\s+law\s+of\s+gravitation\b",
        r"\buniversal\s+gravitation\b",
        r"\bgravitational\s+(field|force|potential)\b",
        r"\bescape\s+velocity\b",
        r"\borbital\s+(motion|velocity)\b",
        r"\bkepler'?s?\s+law\b",
    ]
    for pattern in gravity_patterns:
        if re.search(pattern, text):
            return "gravity"

    return "generic"


def has_animation(concept: str) -> bool:
    """
    Check if an animation is available for the given concept.
    Returns True for all topics since we have a generic animation fallback.
    """
    # Always return True - we have generic animations for any topic
    return True


def has_specialized_animation(concept: str) -> bool:
    """
    Check if a specialized (non-generic) animation is available.
    Returns True only for topics with custom animations.
    """
    topic = detect_topic(concept)
    animated_topics = [
        "bubble_sort", "binary_search", "quadratic", 
        "sine_wave", "projectile_motion", "pendulum",
        "linear_equation", "heat", "geometry", "chemistry", "wave", "statistics",
        "coordinate_geometry", "circuit", "optics", "force",
        "organic_chemistry", "organic_reaction", 
        "physical_chemistry", "inorganic_chemistry",
        "magnetic_field", "electromagnetic", "gravity"
    ]
    return topic in animated_topics


def get_animation_clip(concept: str, duration: float = 5.0, **kwargs) -> Optional[Any]:
    """
    Get an animated VideoClip for the concept if available.
    This is an ADDITIVE feature - does not modify existing rendering.
    
    Args:
        concept: Topic/concept text
        duration: Animation duration in seconds
        **kwargs: Additional animation parameters
    
    Returns:
        MoviePy VideoClip or None if no animation available
    """
    topic = detect_topic(concept)
    
    try:
        from .animation_clips import (
            create_projectile_clip,
            create_sine_wave_clip,
            create_bubble_sort_clip,
            create_binary_search_clip,
            create_quadratic_clip,
            create_pendulum_clip,
            create_linear_equation_clip,
            create_heat_clip,
            create_geometry_clip,
            create_chemistry_clip,
            create_wave_clip,
            create_statistics_clip,
            create_generic_clip,
            create_coordinate_geometry_clip,
            create_circuit_clip,
            create_optics_clip,
            create_force_clip,
            create_organic_chemistry_clip,
            create_organic_reaction_clip,
            create_magnetic_field_clip,
            create_electromagnetic_clip,
            create_gravity_clip,
            create_gas_law_clip,
            create_crystal_lattice_clip
        )
        
        if topic == "projectile_motion":
            return create_projectile_clip(
                duration=duration,
                velocity=kwargs.get("velocity", 50),
                angle=kwargs.get("angle", 45),
                title=kwargs.get("title", "Projectile Motion")
            )
        
        elif topic == "sine_wave":
            return create_sine_wave_clip(
                duration=duration,
                amplitude=kwargs.get("amplitude", 1.0),
                frequency=kwargs.get("frequency", 1.0),
                title=kwargs.get("title", "Sine Wave")
            )
        
        elif topic == "bubble_sort":
            return create_bubble_sort_clip(
                duration=duration,
                array=kwargs.get("array"),
                title=kwargs.get("title", "Bubble Sort")
            )
        
        elif topic == "binary_search":
            return create_binary_search_clip(
                duration=duration,
                array=kwargs.get("array"),
                target=kwargs.get("target", 7),
                title=kwargs.get("title", "Binary Search")
            )
        
        elif topic == "quadratic":
            return create_quadratic_clip(
                duration=duration,
                a=kwargs.get("a", 1.0),
                b=kwargs.get("b", -3.0),
                c=kwargs.get("c", 2.0),
                title=kwargs.get("title", "Quadratic Function")
            )
        
        elif topic == "pendulum":
            return create_pendulum_clip(
                duration=duration,
                length=kwargs.get("length", 1.0),
                max_angle=kwargs.get("max_angle", 30.0),
                title=kwargs.get("title", "Simple Pendulum")
            )
        
        elif topic == "linear_equation":
            return create_linear_equation_clip(
                duration=duration,
                slope=kwargs.get("slope", 2.0),
                intercept=kwargs.get("intercept", 1.0),
                title=kwargs.get("title", "Linear Equation")
            )
        
        elif topic == "heat":
            return create_heat_clip(
                duration=duration,
                title=kwargs.get("title", "Heat & Temperature")
            )
        
        elif topic == "geometry":
            return create_geometry_clip(
                duration=duration,
                title=kwargs.get("title", "Geometry")
            )
        
        elif topic == "chemistry":
            return create_chemistry_clip(
                duration=duration,
                title=kwargs.get("title", "Chemistry")
            )
        
        elif topic == "wave":
            return create_wave_clip(
                duration=duration,
                title=kwargs.get("title", "Wave Motion")
            )
        
        elif topic == "statistics":
            return create_statistics_clip(
                duration=duration,
                title=kwargs.get("title", "Statistics")
            )
        
        elif topic == "coordinate_geometry":
            return create_coordinate_geometry_clip(
                duration=duration,
                title=kwargs.get("title", "Coordinate Geometry")
            )
        
        elif topic == "circuit":
            return create_circuit_clip(
                duration=duration,
                title=kwargs.get("title", "Electric Circuit")
            )
        
        elif topic == "optics":
            return create_optics_clip(
                duration=duration,
                title=kwargs.get("title", "Light & Optics")
            )
        
        elif topic == "force":
            return create_force_clip(
                duration=duration,
                title=kwargs.get("title", "Forces & Newton's Laws")
            )
        
        elif topic == "organic_chemistry":
            return create_organic_chemistry_clip(
                duration=duration,
                title=kwargs.get("title", "Organic Chemistry")
            )
        
        elif topic == "organic_reaction":
            return create_organic_reaction_clip(
                duration=duration,
                title=kwargs.get("title", "Organic Reaction")
            )
        
        elif topic == "physical_chemistry":
            return create_gas_law_clip(
                duration=duration,
                title=kwargs.get("title", "Gas Laws (PV=nRT)")
            )
            
        elif topic == "inorganic_chemistry":
            return create_crystal_lattice_clip(
                duration=duration,
                title=kwargs.get("title", "Crystal Lattice")
            )
        
        elif topic == "magnetic_field":
            return create_magnetic_field_clip(
                duration=duration,
                title=kwargs.get("title", "Magnetic Field Lines")
            )
        
        elif topic == "electromagnetic":
            return create_electromagnetic_clip(
                duration=duration,
                title=kwargs.get("title", "Electromagnetic Induction")
            )
        
        elif topic == "gravity":
            return create_gravity_clip(
                duration=duration,
                title=kwargs.get("title", "Gravitational Force")
            )
        
        else:
            # Generic animation for any other topic
            return create_generic_clip(
                duration=duration,
                title=kwargs.get("title", concept)
            )
        
    except ImportError as e:
        print(f"   ⚠️ Animation import failed: {e}")
        return None
    
    return None


def get_animation_info(concept: str) -> dict:
    """
    Get animation availability info for a concept.
    
    Returns:
        Dict with keys: has_animation, topic, description, is_specialized
    """
    topic = detect_topic(concept)
    
    descriptions = {
        "bubble_sort": "Watch the bubble sort algorithm in action, comparing and swapping elements step by step.",
        "binary_search": "See how binary search efficiently finds a target by halving the search space.",
        "quadratic": "Observe the parabolic curve of a quadratic function with its vertex and roots.",
        "sine_wave": "Watch the sine wave propagate, showing the periodic nature of trigonometric functions.",
        "projectile_motion": "See a projectile follow its parabolic trajectory under gravity.",
        "pendulum": "Observe simple harmonic motion as the pendulum swings back and forth.",
        "linear_equation": "Watch a linear equation graph being drawn with slope and y-intercept visualization.",
        "heat": "Observe heat transfer between hot and cold regions with particle motion visualization.",
        "geometry": "See geometric shapes rotating with their properties and formulas displayed.",
        "chemistry": "Explore the atomic model with electrons orbiting the nucleus in energy shells.",
        "wave": "Watch wave propagation with amplitude and wavelength visualization.",
        "statistics": "See data come alive with animated bar charts and statistical measures.",
        "coordinate_geometry": "Visualize coordinate plane with point plotting, distance and midpoint formulas.",
        "circuit": "See electric current flow through a circuit with Ohm's law visualization.",
        "optics": "Watch light reflection and refraction with Snell's law demonstration.",
        "force": "See force vectors and Newton's laws in action with acceleration visualization.",
        "organic_chemistry": "Explore organic molecules with carbon chains, functional groups, and molecular structures.",
        "organic_reaction": "Watch organic reactions with reactants transforming into products step by step.",
        "physical_chemistry": "Visualize gas particles in motion demonstrating pressure, volume, and temperature relationships.",
        "inorganic_chemistry": "Explore 3D crystal lattice structures and unit cells rotating in space.",
        "magnetic_field": "Visualize magnetic field lines from N to S pole with compass needle alignment.",
        "electromagnetic": "Watch electromagnetic induction with magnet moving through coil, inducing current.",
        "gravity": "See gravitational force in action with free fall, field lines, and orbital motion.",
        "generic": "Animated visualization with floating concepts and dynamic effects."
    }
    
    specialized_topics = [
        "bubble_sort", "binary_search", "quadratic", "sine_wave", 
        "projectile_motion", "pendulum", "linear_equation", "heat", 
        "geometry", "chemistry", "wave", "statistics",
        "coordinate_geometry", "circuit", "optics", "force",
        "organic_chemistry", "organic_reaction", 
        "physical_chemistry", "inorganic_chemistry",
        "magnetic_field", "electromagnetic", "gravity"
    ]
    is_specialized = topic in specialized_topics
    
    return {
        "has_animation": True,  # Always True - we have generic animations for any topic
        "is_specialized": is_specialized,
        "topic": topic,
        "description": descriptions.get(topic, descriptions["generic"])
    }