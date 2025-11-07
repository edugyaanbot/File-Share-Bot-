from datetime import datetime
from typing import Optional
from app.db.mongo import get_database


async def log_audit(
    actor_id: int,
    action: str,
    target_uuid: Optional[str] = None,
    notes: Optional[str] = None
):
    """Log audit event"""
    db = get_database()
    
    audit_doc = {
        "at": datetime.utcnow(),
        "actor_id": actor_id,
        "action": action,
        "target_uuid": target_uuid,
        "notes": notes
    }
    
    await db.audits.insert_one(audit_doc)
