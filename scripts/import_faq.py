"""
Import FAQ Q&A pairs into the system.
Run: python scripts/import_faq.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> None:
    faq_path = Path("data/faq/common_questions.json")
    if not faq_path.exists():
        print(f"FAQ file not found: {faq_path}")
        return

    with open(faq_path, encoding="utf-8") as f:
        faqs = json.load(f)

    print(f"Importing {len(faqs)} FAQ entries...")
    for i, faq in enumerate(faqs[:5]):
        print(f"  [{i+1}] Q: {faq.get('question', 'N/A')[:50]}...")

    # TODO: embed and store in vector DB
    print("Done!")


if __name__ == "__main__":
    main()
