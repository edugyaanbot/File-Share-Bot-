from fastapi import APIRouter, Depends
from app.web.auth import get_current_admin
from app.services.stats import get_dashboard_stats

router = APIRouter()


@router.get("/stats", dependencies=[Depends(get_current_admin)])
async def api_get_stats():
    """Get dashboard statistics"""
    return await get_dashboard_stats()
