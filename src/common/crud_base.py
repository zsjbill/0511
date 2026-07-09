import math
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    """Generic async CRUD base for SQLAlchemy models.

    Usage:
        customer_crud = CRUDBase(IntentCustomer, IntentCustomerCreate, IntentCustomerUpdate)
        result = await customer_crud.list(db, page=1, page_size=20, status="跟进中")
    """

    def __init__(self, model: type, schema_create: type, schema_update: type):
        self.model = model
        self.schema_create = schema_create
        self.schema_update = schema_update

    async def create(self, db: AsyncSession, data) -> Any:
        obj = self.model(**data.model_dump())
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def get(self, db: AsyncSession, id: int):
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def list(self, db: AsyncSession, *, page: int = 1, page_size: int = 20, **filters):
        query = select(self.model)

        for key, value in filters.items():
            if value is None or value == "" or value == []:
                continue
            if key.endswith("__like"):
                col_name = key[:-6]
                col = getattr(self.model, col_name, None)
                if col is not None:
                    query = query.where(col.like(f"%{value}%"))
            elif key.endswith("__gte"):
                col_name = key[:-5]
                col = getattr(self.model, col_name, None)
                if col is not None:
                    query = query.where(col >= value)
            elif key.endswith("__lte"):
                col_name = key[:-5]
                col = getattr(self.model, col_name, None)
                if col is not None:
                    query = query.where(col <= value)
            elif key == "start_date":
                col = getattr(self.model, "created_at", None)
                if col is not None:
                    query = query.where(col >= value)
            elif key == "end_date":
                col = getattr(self.model, "created_at", None)
                if col is not None:
                    query = query.where(col <= value)
            elif key == "min_score":
                for score_col_name in ["ielts_score", "major_course_score", "lab_score"]:
                    col = getattr(self.model, score_col_name, None)
                    if col is not None:
                        query = query.where(col >= value)
            elif key == "max_score":
                for score_col_name in ["ielts_score", "major_course_score", "lab_score"]:
                    col = getattr(self.model, score_col_name, None)
                    if col is not None:
                        query = query.where(col <= value)
            else:
                col = getattr(self.model, key, None)
                if col is not None:
                    query = query.where(col == value)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        }

    async def update(self, db: AsyncSession, id: int, data) -> Any:
        obj = await self.get(db, id)
        if obj is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        obj = await self.get(db, id)
        if obj is None:
            return False
        await db.delete(obj)
        await db.flush()
        return True
