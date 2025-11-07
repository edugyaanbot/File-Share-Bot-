from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.web.auth import get_current_admin
from app.db.mongo import get_database
from app.services.users import ban_user, unban_user
from pydantic import BaseModel

router = APIRouter()


class BanUserRequest(BaseModel):
    user_id: int
    reason: str = ""


@router.get("/users", dependencies=[Depends(get_current_admin)])
async def api_get_users(skip: int = 0, limit: int = 50):
    """Get users list"""
    db = get_database()
    users = await db.users.find().skip(skip).limit(limit).to_list(limit)
    
    # Convert ObjectId to string
    for user in users:
        user['_id'] = str(user['_id'])
    
    return {"users": users}


@router.patch("/users/{user_id}/ban", dependencies=[Depends(get_current_admin)])
async def api_ban_user(user_id: int, admin_email: str = Depends(get_current_admin)):
    """Ban a user"""
    await ban_user(user_id, 0)  # 0 as admin actor ID
    return {"status": "success", "message": f"User {user_id} banned"}


@router.patch("/users/{user_id}/unban", dependencies=[Depends(get_current_admin)])
async def api_unban_user(user_id: int, admin_email: str = Depends(get_current_admin)):
    """Unban a user"""
    await unban_user(user_id, 0)
    return {"status": "success", "message": f"User {user_id} unbanned"}
