from datetime import datetime, timedelta
from typing import Dict, Any
from app.db.mongo import get_database
from app.services.cache import cache_get, cache_set
import orjson


async def get_dashboard_stats() -> Dict[str, Any]:
    """Get cached dashboard statistics"""
    cache_key = "stats:dashboard"
    
    # Try cache
    cached = await cache_get(cache_key)
    if cached:
        return orjson.loads(cached)
    
    db = get_database()
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    
    # Total users
    total_users = await db.users.count_documents({})
    
    # Active users (24h)
    active_24h = await db.users.count_documents({
        "last_seen_at": {"$gte": day_ago}
    })
    
    # New users (24h)
    new_24h = await db.users.count_documents({
        "created_at": {"$gte": day_ago}
    })
    
    # Banned users
    banned = await db.users.count_documents({"is_banned": True})
    
    # Total files
    total_files = await db.files.count_documents({"deleted_at": None})
    
    # Files created (24h)
    files_24h = await db.files.count_documents({
        "created_at": {"$gte": day_ago},
        "deleted_at": None
    })
    
    # Deleted files
    deleted_files = await db.files.count_documents({"deleted_at": {"$ne": None}})
    
    # Storage used
    storage_pipeline = [
        {"$match": {"deleted_at": None}},
        {"$group": {"_id": None, "total": {"$sum": "$size_bytes"}}}
    ]
    storage_result = await db.files.aggregate(storage_pipeline).to_list(1)
    storage_bytes = storage_result[0]["total"] if storage_result else 0
    
    # Top 10 files
    top_files = await db.files.find(
        {"deleted_at": None}
    ).sort("downloads", -1).limit(10).to_list(10)
    
    stats = {
        "total_users": total_users,
        "active_24h": active_24h,
        "new_24h": new_24h,
        "banned_users": banned,
        "total_files": total_files,
        "files_24h": files_24h,
        "deleted_files": deleted_files,
        "storage_bytes": storage_bytes,
        "storage_human": humanize_bytes(storage_bytes),
        "top_files": [
            {
                "uuid": f["uuid"],
                "file_name": f.get("file_name", "Unnamed"),
                "downloads": f["downloads"]
            }
            for f in top_files
        ]
    }
    
    # Cache for 60 seconds
    await cache_set(cache_key, orjson.dumps(stats), ttl=60)
    
    return stats


def humanize_bytes(bytes_size: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
