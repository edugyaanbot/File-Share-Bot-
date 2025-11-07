from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = Database()


async def connect_db():
    """Connect to MongoDB Atlas with optimized connection pool"""
    try:
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=100,
            minPoolSize=10,
            serverSelectionTimeoutMS=3000,
            retryWrites=True,
            w='majority'
        )
        db.db = db.client.filebot
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("✅ Connected to MongoDB Atlas")
        
        await create_indexes()
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise


async def close_db():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        logger.info("Closed MongoDB connection")


async def create_indexes():
    """Create all required indexes for optimal performance"""
    try:
        # Users collection indexes
        users_indexes = [
            IndexModel([("user_id", ASCENDING)], unique=True),
            IndexModel([("last_seen_at", DESCENDING)])
        ]
        
        # Files collection indexes
        files_indexes = [
            IndexModel([("uuid", ASCENDING)], unique=True),
            IndexModel([("owner_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("file_unique_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("deleted_at", ASCENDING)])
        ]
        
        # Audits collection indexes
        audits_indexes = [
            IndexModel([("at", DESCENDING)]),
            IndexModel([("actor_id", ASCENDING), ("at", DESCENDING)])
        ]

        await db.db.users.create_indexes(users_indexes)
        await db.db.files.create_indexes(files_indexes)
        await db.db.audits.create_indexes(audits_indexes)
        
        logger.info("✅ MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"❌ Index creation error: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.db
