from fastapi import APIRouter, Depends
from app.web.auth import get_current_admin
from app.config import settings
from pydantic import BaseModel

router = APIRouter()


class SettingsResponse(BaseModel):
    maintenance_mode: bool
    max_file_size_mb: int
    user_rate_limit_per_min: int


@router.get("/settings", dependencies=[Depends(get_current_admin)])
async def api_get_settings():
    """Get current settings"""
    return SettingsResponse(
        maintenance_mode=settings.MAINTENANCE_MODE,
        max_file_size_mb=settings.MAX_FILE_SIZE_MB,
        user_rate_limit_per_min=settings.USER_RATE_LIMIT_PER_MIN
    )
