"""
Initialize database tables.
Run: python scripts/init_db.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.common.database import async_engine, Base, init_db
from src.common.models import *  # noqa: F401,F403 — ensure all models are imported


async def main() -> None:
    print("Creating database tables...")
    await init_db()
    print("Done! All tables created successfully.")


if __name__ == "__main__":
    asyncio.run(main())
