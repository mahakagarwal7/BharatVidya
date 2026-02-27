# src/latex_renderer.py

"""
LaTeX/Math Rendering Module
Renders mathematical equations using matplotlib with LaTeX-style rendering.
Outputs PNG images that can be embedded in video frames.
"""

import numpy as np
import cv2
import os
import hashlib
import re
from typing import Tuple, Optional, Dict, Any

# Matplotlib imports for LaTeX rendering
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib import mathtext


# Cache directory for rendered equations
CACHE_DIR = "outputs/latex_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def extract_math_expressions(text: str) -> list:
    """
    Extract mathematical expressions from text.
    Looks for patterns like:
    - $...$  (inline math)
    - $$...$$ (display math)
    - Common math patterns (equations, formulas)
    """
    expressions = []
    
    # Extract $$...$$ display math
    display_math = re.findall(r'\$\$(.*?)\$\$', text, re.DOTALL)
    expressions.extend(display_math)
    
    # Extract $...$ inline math
    inline_math = re.findall(r'(?<!\$)\$([^\$]+?)\$(?!\$)', text)
    expressions.extend(inline_math)
    
    # If no explicit math markers, try to detect common patterns
    if not expressions:
        # Look for equation-like patterns
        equation_patterns = [
            r'([a-zA-Z]\s*=\s*[^,\.\n]+)',  # x = ...
            r'(\d+\s*[\+\-\*\/]\s*\d+\s*=\s*\d+)',  # 2 + 2 = 4
            r'([a-zA-Z]\^\d+)',  # x^2
            r'(\\frac\{[^}]+\}\{[^}]+\})',  # \frac{}{} 
            r'(\\sqrt\{[^}]+\})',  # \sqrt{}
        ]
        for pattern in equation_patterns:
            matches = re.findall(pattern, text)
            expressions.extend(matches)
    
    return expressions


def render_latex_to_image(
    latex: str,
    fontsize: int = 24,
    text_color: str = 'white',
    bg_color: str = 'none',
    dpi: int = 150
) -> Optional[np.ndarray]:
    """
    Render a LaTeX expression to an image array.
    
    Args:
        latex: LaTeX expression (without $ delimiters)
        fontsize: Font size for rendering
        text_color: Color of the text
        bg_color: Background color ('none' for transparent)
        dpi: Resolution
        
    Returns:
        RGBA numpy array of the rendered equation, or None on error
    """
    # Check cache first
    cache_key = hashlib.md5(f"{latex}_{fontsize}_{text_color}_{dpi}".encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.png")
    
    if os.path.exists(cache_path):
        img = cv2.imread(cache_path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            return img
    
    try:
        # Create figure with transparent background
        fig, ax = plt.subplots(figsize=(10, 2), dpi=dpi)
        fig.patch.set_alpha(0.0)
        ax.set_facecolor('none')
        ax.axis('off')
        
        # Ensure LaTeX is properly formatted
        if not latex.startswith('$'):
            latex = f'${latex}$'
        
        # Render the equation
        ax.text(
            0.5, 0.5, latex,
            fontsize=fontsize,
            color=text_color,
            ha='center',
            va='center',
            transform=ax.transAxes,
            usetex=False,  # Use mathtext (built-in, no LaTeX installation needed)
            math_fontfamily='cm'  # Computer Modern font
        )
        
        # Tight layout to minimize whitespace
        fig.tight_layout(pad=0.1)
        
        # Save to buffer
        fig.canvas.draw()
        
        # Get the image data
        buf = fig.canvas.buffer_rgba()
        img = np.asarray(buf)
        
        plt.close(fig)
        
        # Crop to content (remove excess transparent area)
        img = crop_to_content(img)
        
        # Cache the result
        cv2.imwrite(cache_path, cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA))
        
        # Convert to BGR for OpenCV
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
        
    except Exception as e:
        print(f"LaTeX render error for '{latex}': {e}")
        plt.close('all')
        return None


def crop_to_content(img: np.ndarray, padding: int = 10) -> np.ndarray:
    """
    Crop image to non-transparent content with padding.
    """
    if img.shape[2] < 4:
        return img
    
    # Find non-transparent pixels
    alpha = img[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    
    if not np.any(rows) or not np.any(cols):
        return img
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    # Add padding
    rmin = max(0, rmin - padding)
    rmax = min(img.shape[0], rmax + padding)
    cmin = max(0, cmin - padding)
    cmax = min(img.shape[1], cmax + padding)
    
    return img[rmin:rmax, cmin:cmax]


def render_equation_on_frame(
    frame: np.ndarray,
    latex: str,
    x: int,
    y: int,
    max_width: int = 600,
    max_height: int = 200,
    fontsize: int = 28,
    text_color: str = 'white',
    center: bool = True
) -> np.ndarray:
    """
    Render a LaTeX equation directly onto a video frame.
    
    Args:
        frame: BGR numpy array (video frame)
        latex: LaTeX expression
        x, y: Position to place the equation
        max_width, max_height: Maximum size constraints
        fontsize: Base font size
        text_color: Color of the equation
        center: If True, center the equation at (x, y)
        
    Returns:
        Modified frame with equation rendered
    """
    # Render the equation to image
    eq_img = render_latex_to_image(latex, fontsize=fontsize, text_color=text_color)
    
    if eq_img is None:
        # Fallback: draw plain text
        cv2.putText(
            frame, latex.replace('$', ''),
            (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
        )
        return frame
    
    # Resize if needed to fit constraints
    h, w = eq_img.shape[:2]
    scale = min(max_width / w, max_height / h, 1.0)
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        eq_img = cv2.resize(eq_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        h, w = new_h, new_w
    
    # Calculate position
    if center:
        x = x - w // 2
        y = y - h // 2
    
    # Ensure we stay within frame bounds
    x = max(0, min(x, frame.shape[1] - w))
    y = max(0, min(y, frame.shape[0] - h))
    
    # Composite the equation onto the frame
    if eq_img.shape[2] == 4:
        # Has alpha channel - blend properly
        alpha = eq_img[:, :, 3:4] / 255.0
        bgr = eq_img[:, :, :3]
        
        # Get region of interest
        roi = frame[y:y+h, x:x+w]
        
        # Blend
        blended = (bgr * alpha + roi * (1 - alpha)).astype(np.uint8)
        frame[y:y+h, x:x+w] = blended
    else:
        # No alpha - direct copy
        frame[y:y+h, x:x+w] = eq_img[:, :, :3]
    
    return frame


def create_equation_element(
    latex: str,
    x: int = 500,
    y: int = 300,
    fontsize: int = 32,
    color: str = 'white',
    max_width: int = 700,
    max_height: int = 150
) -> Dict[str, Any]:
    """
    Create a visual element dict for a LaTeX equation.
    Can be added to a plan's visual_elements list.
    """
    return {
        "type": "latex",
        "latex": latex,
        "x": x,
        "y": y,
        "fontsize": fontsize,
        "color": color,
        "max_width": max_width,
        "max_height": max_height
    }


# Common math expressions for quick access
COMMON_EQUATIONS = {
    "quadratic_formula": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
    "pythagorean": r"a^2 + b^2 = c^2",
    "euler": r"e^{i\pi} + 1 = 0",
    "derivative": r"\frac{dy}{dx} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
    "integral": r"\int_a^b f(x)\,dx = F(b) - F(a)",
    "einstein": r"E = mc^2",
    "newtons_second": r"F = ma",
    "gravitational": r"F = G\frac{m_1 m_2}{r^2}",
    "kinetic_energy": r"KE = \frac{1}{2}mv^2",
    "potential_energy": r"PE = mgh",
    "wave_equation": r"v = f\lambda",
    "ohms_law": r"V = IR",
    "area_circle": r"A = \pi r^2",
    "circumference": r"C = 2\pi r",
    "slope": r"m = \frac{y_2 - y_1}{x_2 - x_1}",
    "distance": r"d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}",
}


def get_equation_for_topic(topic: str) -> Optional[str]:
    """
    Get a relevant equation for a given topic.
    """
    topic_lower = topic.lower()
    
    # Map topics to equations
    topic_equation_map = {
        "quadratic": "quadratic_formula",
        "pythagor": "pythagorean",
        "euler": "euler",
        "derivative": "derivative",
        "integral": "integral",
        "einstein": "einstein",
        "energy": "kinetic_energy",
        "force": "newtons_second",
        "gravity": "gravitational",
        "wave": "wave_equation",
        "ohm": "ohms_law",
        "circle": "area_circle",
        "slope": "slope",
        "distance": "distance",
        "motion": "newtons_second",
        "velocity": "kinetic_energy",
        "projectile": "kinetic_energy",
    }
    
    for keyword, eq_key in topic_equation_map.items():
        if keyword in topic_lower:
            return COMMON_EQUATIONS.get(eq_key)
    
    return None


def detect_math_topic(text: str) -> bool:
    """
    Detect if a topic is math-related and would benefit from LaTeX rendering.
    """
    math_keywords = [
        'equation', 'formula', 'math', 'calculus', 'algebra', 'geometry',
        'trigonometry', 'derivative', 'integral', 'function', 'graph',
        'quadratic', 'polynomial', 'exponential', 'logarithm', 'vector',
        'matrix', 'probability', 'statistics', 'physics', 'chemistry',
        'theorem', 'proof', 'solve', 'calculate', 'compute'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in math_keywords)
