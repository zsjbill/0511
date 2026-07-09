"""Import documents from data/knowledge_base/ into kb_documents table."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from src.common.file_parser import parse_file
from src.common.database import StudentSessionLocal
from src.common.models_student import KBDocument

KB_SOURCE_DIR = Path("data/knowledge_base")


async def import_documents(source_dir: Path = None):
    if source_dir is None:
        source_dir = KB_SOURCE_DIR

    if not source_dir.exists():
        print(f"KB source directory not found: {source_dir}")
        return

    count = 0
    async with StudentSessionLocal() as db:
        for file_path in source_dir.iterdir():
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in (".pdf", ".docx", ".txt", ".md"):
                continue

            print(f"Importing: {file_path.name}")
            try:
                content = parse_file(str(file_path))
            except Exception as e:
                print(f"  Failed to parse: {e}")
                continue

            # Auto-categorize by filename keywords
            category = "general"
            lower_name = file_path.stem.lower()
            if any(kw in lower_name for kw in ["海外", "生活", "abroad", "life"]):
                category = "life abroad"
            elif any(kw in lower_name for kw in ["升学", "study", "课程", "course"]):
                category = "study guide"
            elif any(kw in lower_name for kw in ["政策", "policy", "法规", "law"]):
                category = "policy"

            doc = KBDocument(
                title=file_path.stem,
                content=content,
                category=category,
                source_file=file_path.name,
            )
            db.add(doc)
            count += 1
            print(f"  OK ({len(content)} chars, category={category})")

        await db.commit()
    print(f"Imported {count} documents.")


if __name__ == "__main__":
    asyncio.run(import_documents())
