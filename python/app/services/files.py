from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any, List
from app.db.mongo import get_database
from app.services.audits import log_audit
import logging

logger = logging.getLogger(__name__)


async def create_file_record(
    owner_id: int,
    file_type: str,
    storage_message_id: int,
    file_id: str,
    file_unique_id: str,
    file_name: Optional[str],
    mime_type: Optional[str],
    size_bytes: int,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new file record in database"""
    db = get_database()
    
    file_doc = {
        "uuid": str(uuid4()),
        "owner_id": owner_id,
        "type": file_type,
        "storage_channel_message_id": storage_message_id,
        "file_id": file_id,
        "file_unique_id": file_unique_id,
        "file_name": file_name,
        "mime_type": mime_type,
        "size_bytes": size_bytes,
        "width": width,
        "height": height,
        "downloads": 0,
        "created_at": datetime.utcnow(),
        "deleted_at": None
    }
    
    result = await db.files.insert_one(file_doc)
    file_doc["_id"] = result.inserted_id
    
    await log_audit(owner_id, "FILE_CREATED", file_doc["uuid"])
    logger.info(f"Created file record {file_doc['uuid']} for user {owner_id}")
    
    return file_doc


async def get_file_by_uuid(uuid: str) -> Optional[Dict[str, Any]]:
    """Get file by UUID"""
    db = get_database()
    return await db.files.find_one({"uuid": uuid})


async def increment_downloads(uuid: str):
    """Increment download count for file"""
    db = get_database()
    await db.files.update_one(
        {"uuid": uuid},
        {"$inc": {"downloads": 1}}
    )


async def get_user_files(
    user_id: int,
    page: int = 1,
    page_size: int = 10
) -> List[Dict[str, Any]]:
    """Get paginated files for user"""
    db = get_database()
    
    skip = (page - 1) * page_size
    
    cursor = db.files.find({
        "owner_id": user_id,
        "deleted_at": None
    }).sort("created_at", -1).skip(skip).limit(page_size)
    
    return await cursor.to_list(length=page_size)


async def count_user_files(user_id: int) -> int:
    """Count non-deleted files for user"""
    db = get_database()
    return await db.files.count_documents({
        "owner_id": user_id,
        "deleted_at": None
    })


async def soft_delete_file(uuid: str, actor_id: int):
    """Soft delete file"""
    db = get_database()
    
    await db.files.update_one(
        {"uuid": uuid},
        {"$set": {"deleted_at": datetime.utcnow()}}
    )
    
    await log_audit(actor_id, "FILE_DELETED", uuid)
    logger.info(f"Soft deleted file {uuid} by user {actor_id}")


async def restore_file(uuid: str, actor_id: int):
    """Restore soft-deleted file"""
    db = get_database()
    
    await db.files.update_one(
        {"uuid": uuid},
        {"$set": {"deleted_at": None}}
    )
    
    await log_audit(actor_id, "FILE_RESTORED", uuid)
    logger.info(f"Restored file {uuid} by user {actor_id}")
