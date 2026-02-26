# src/main.py

"""
CLI entrypoint for Educational Animation Generator
"""

import sys
from .animator import EducationalAnimator


def main():

    if len(sys.argv) < 2:
        print("Usage: python -m src.main \"Your concept here\"")
        sys.exit(1)

    concept = " ".join(sys.argv[1:])

    print(f"Original input: {concept}")
    print(f"Enhanced input: {concept}")

    animator = EducationalAnimator()

    video_path, plan = animator.generate(concept)

    if video_path:
        print(f"✅ Video created: {video_path}")
        print(f"Plan saved at: {plan.get('_saved_plan_file')}")
    else:
        print("❌ Failed to render animation.")


if __name__ == "__main__":
    main()