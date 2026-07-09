"""
Vectorize knowledge base files and import into vector store.
Run: python scripts/vectorize_knowledge.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from src.common.file_parser import parse_file
from src.common.vector_store import vector_store
from src.common.llm_client import llm_client

KNOWLEDGE_DIR = Path("data/knowledge_base")


async def main() -> None:
    print(f"Vectorizing knowledge base from: {KNOWLEDGE_DIR.absolute()}")
    if not KNOWLEDGE_DIR.exists():
        print(f"Directory not found: {KNOWLEDGE_DIR}")
        return

    for file_path in KNOWLEDGE_DIR.iterdir():
        if file_path.is_file():
            print(f"  Processing: {file_path.name}")
            text = parse_file(str(file_path))
            # TODO: chunk text, embed, and store in vector DB
            print(f"    Parsed {len(text)} characters")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
