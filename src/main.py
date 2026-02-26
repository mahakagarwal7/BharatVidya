# src/main.py

import sys
import os

if __name__ == "__main__" and __package__ is None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

try:
    from src.animator import EducationalAnimator
except Exception:
    from animator import EducationalAnimator


def main():

    if len(sys.argv) < 2:
        print("Usage: python -m src.main \"Your educational concept description\"")
        sys.exit(1)

    concept = " ".join(sys.argv[1:])

    print("Original input:", concept)
    print("Enhanced input:", concept)

    animator = EducationalAnimator()

    # Now returns (video_path, plans_list)
    video, plans = animator.generate(concept)

    if video:
        print(f"\n✅ Final Video created: {video}")

        print("\n📄 Plans generated:")
        for idx, p in enumerate(plans):
            print(f"  Scene {idx+1}: {p.get('_saved_plan_file')}")

    else:
        print("❌ Failed to render animation.")


if __name__ == "__main__":
    main()