"""Script to manually initialize MongoDB indexes"""
import asyncio
from app.db.mongo import connect_db, create_indexes, close_db


async def main():
    await connect_db()
    await create_indexes()
    await close_db()
    print("✅ Indexes created successfully")


if __name__ == "__main__":
    asyncio.run(main())
