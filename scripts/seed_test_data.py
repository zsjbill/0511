"""
Generate test data for development.
Run: python scripts/seed_test_data.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.common.database import AsyncSessionLocal
from src.common.models import Customer, Employee, Student, User


async def seed_users() -> None:
    """Seed test users."""
    async with AsyncSessionLocal() as session:
        # Check if data already exists
        from sqlalchemy import select, func
        count = (await session.execute(select(func.count()).select_from(User))).scalar()
        if count and count > 0:
            print(f"Users table already has {count} records, skipping.")
            return

        users = [
            User(username="admin", email="admin@ai-csm.com", hashed_password="hash_admin", role="admin"),
            User(username="agent_zhang", email="zhang@ai-csm.com", hashed_password="hash_agent", role="agent"),
            User(username="agent_li", email="li@ai-csm.com", hashed_password="hash_agent", role="agent"),
        ]
        session.add_all(users)
        await session.commit()
        print(f"Seeded {len(users)} users.")


async def seed_customers() -> None:
    """Seed test customers."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        count = (await session.execute(select(func.count()).select_from(Customer))).scalar()
        if count and count > 0:
            print(f"Customers table already has {count} records, skipping.")
            return

        customers = [
            Customer(name="测试客户A", phone="13800001111", wechat="wx_a", source="百度推广", tags='["高意向"]', profile_score=85),
            Customer(name="测试客户B", phone="13800002222", wechat="wx_b", source="微信朋友圈", tags='["中意向"]', profile_score=55),
            Customer(name="测试客户C", phone="13800003333", source="朋友推荐", tags='["高意向","VIP"]', profile_score=90),
        ]
        session.add_all(customers)
        await session.commit()
        print(f"Seeded {len(customers)} customers.")


async def seed_students() -> None:
    """Seed test students."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        count = (await session.execute(select(func.count()).select_from(Student))).scalar()
        if count and count > 0:
            print(f"Students table already has {count} records, skipping.")
            return

        students = [
            Student(name="学生张三", student_code="STU001", stage="语言班", target_country="澳大利亚"),
            Student(name="学生李四", student_code="STU002", stage="预科", target_country="英国"),
            Student(name="学生王五", student_code="STU003", stage="本科申请", target_country="美国"),
        ]
        session.add_all(students)
        await session.commit()
        print(f"Seeded {len(students)} students.")


async def seed_employees() -> None:
    """Seed test employees."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        count = (await session.execute(select(func.count()).select_from(Employee))).scalar()
        if count and count > 0:
            print(f"Employees table already has {count} records, skipping.")
            return

        employees = [
            Employee(name="管理员", department="管理部", position="CEO", email="ceo@ai-csm.com"),
            Employee(name="技术张三", department="技术部", position="高级工程师", email="tech@ai-csm.com"),
            Employee(name="运营李四", department="运营部", position="运营经理", email="ops@ai-csm.com"),
        ]
        session.add_all(employees)
        await session.commit()
        print(f"Seeded {len(employees)} employees.")


async def main() -> None:
    print("Seeding test data...")
    await seed_users()
    await seed_customers()
    await seed_students()
    await seed_employees()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
