import asyncio, logging, datetime
from sqlalchemy import select
from src.common.database import StudentSessionLocal
from src.common.models_student import SyncLog

logger = logging.getLogger(__name__)
_sync_status = {}


async def run_sync(sync_type: str) -> dict:
    """Run a sync operation and log results."""
    log = SyncLog(sync_type=sync_type, status="running", started_at=datetime.datetime.now())
    async with StudentSessionLocal() as db:
        db.add(log)
        await db.commit()
        await db.refresh(log)
        log_id = log.id

    try:
        records = await _fetch_external_data(sync_type)
        await _save_sync_result(log_id, status="success", count=len(records))
        _sync_status[sync_type] = {
            "status": "success", "records_count": len(records),
            "last_sync": datetime.datetime.now().isoformat(),
        }
        return _sync_status[sync_type]
    except Exception as e:
        logger.error(f"Sync {sync_type} failed: {e}")
        await _save_sync_result(log_id, status="failed", error=str(e))
        _sync_status[sync_type] = {
            "status": "failed", "error": str(e),
            "last_sync": datetime.datetime.now().isoformat(),
        }
        return _sync_status[sync_type]


async def _fetch_external_data(sync_type: str) -> list[dict]:
    """Stub: call external system API. Replace with real HTTP calls."""
    await asyncio.sleep(0.5)
    return [{"source": sync_type, "sample": "data"}]


async def _save_sync_result(log_id: int, status: str, count: int = 0, error: str = None):
    async with StudentSessionLocal() as db:
        result = await db.execute(select(SyncLog).where(SyncLog.id == log_id))
        log = result.scalar_one_or_none()
        if log:
            log.status = status
            log.records_count = count
            log.error_message = error
            log.finished_at = datetime.datetime.now()
            await db.commit()


def get_sync_status() -> dict:
    return _sync_status


async def start_scheduler():
    """Run sync every hour for both sync types."""
    while True:
        for sync_type in ["campus_ddl", "crm_progress"]:
            try:
                await run_sync(sync_type)
            except Exception as e:
                logger.error(f"Scheduled sync error: {e}")
        await asyncio.sleep(3600)
