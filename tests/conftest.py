"""
pytest configuration and shared fixtures.
"""
import asyncio
import pytest
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator:
    """Provide a test database session."""
    # TODO: create test DB session
    yield None
