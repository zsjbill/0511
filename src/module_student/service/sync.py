"""数据同步服务模块 — 外部系统数据同步。

支持两种同步类型：
  - campus_ddl：从校园教务系统同步教学计划/截止日期
  - crm_progress：从 CRM 系统同步学生学习/服务进度

每次同步记录到 SyncLog 表，并更新内存中的同步状态缓存。
"""

import asyncio, logging, datetime
from sqlalchemy import select
from src.common.database import StudentSessionLocal
from src.module_student.dbmodel.models import SyncLog

logger = logging.getLogger(__name__)
_sync_status = {}  # 内存中的同步状态缓存，记录各同步类型的最近一次执行结果


async def run_sync(sync_type: str) -> dict:
    """执行指定类型的数据同步操作并记录日志。

    同步流程：
    1. 在 SyncLog 表中创建一条状态为"running"的日志记录
    2. 调用 _fetch_external_data 从外部系统拉取数据
    3. 调用 _save_sync_result 更新日志为"success"或"failed"
    4. 更新 _sync_status 内存缓存供状态查询接口使用
    """
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
    """（桩函数）从外部系统 API 获取数据。

    当前为模拟实现，返回一条示例数据。
    需替换为真实的 HTTP 调用或数据库连接。
    """
    await asyncio.sleep(0.5)
    return [{"source": sync_type, "sample": "data"}]


async def _save_sync_result(log_id: int, status: str, count: int = 0, error: str = None):
    """更新同步日志的执行结果。

    根据同步执行情况，将日志状态更新为"success"或"failed"，
    并记录同步记录数和错误信息（如果有）。
    """
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
    """获取所有同步类型的最新状态。

    返回 _sync_status 字典，包含各同步类型的最近一次执行结果、
    记录数和同步时间。
    """
    return _sync_status


async def start_scheduler():
    """启动定时同步调度器，每小时执行一次所有同步任务。

    依次执行 campus_ddl 和 crm_progress 两种同步，
    每次间隔 3600 秒（1 小时）。
    """
    while True:
        for sync_type in ["campus_ddl", "crm_progress"]:
            try:
                await run_sync(sync_type)
            except Exception as e:
                logger.error(f"Scheduled sync error: {e}")
        await asyncio.sleep(3600)
