# src/main.py

"""
CLI entrypoint for Educational Animation Generator
Usage:
  python -m src.main "Your concept"
  python -m src.main "Your concept" --lang pa    # Punjabi
  python -m src.main "Your concept" --lang hi    # Hindi
"""

import sys
from .animator import EducationalAnimator


def main():

    if len(sys.argv) < 2:
        print('Usage: python -m src.main "Your concept here" [--lang LANG_CODE]')
        print("  Language codes: en, hi, pa, te, bn, ta, es, fr, de, zh, ja, ko")
        sys.exit(1)

    # Parse --lang flag
    language = "en"
    args = list(sys.argv[1:])
    if "--lang" in args:
        idx = args.index("--lang")
        if idx + 1 < len(args):
            language = args[idx + 1]
            args.pop(idx)  # remove --lang
            args.pop(idx)  # remove value

    concept = " ".join(args)

    print(f"Original input: {concept}")
    print(f"Language: {language}")

    animator = EducationalAnimator(language=language)

    video_path, plan = animator.generate(concept, language=language)

    if video_path:
        print(f"✅ Video created: {video_path}")
        print(f"Plan saved at: {plan.get('_saved_plan_file')}")
    else:
        print("❌ Failed to render animation.")


if __name__ == "__main__":
    main()