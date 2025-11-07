from fastapi import APIRouter, Depends, HTTPException
from app.web.auth import get_current_admin
from app.db.mongo import get_database
from app.services.files import soft_delete_file, restore_file

router = APIRouter()


@router.get("/files", dependencies=[Depends(get_current_admin)])
async def api_get_files(skip: int = 0, limit: int = 50):
    """Get files list"""
    db = get_database()
    files = await db.files.find().skip(skip).limit(limit).to_list(limit)
    
    for file in files:
        file['_id'] = str(file['_id'])
    
    return {"files": files}


@router.delete("/files/{uuid}", dependencies=[Depends(get_current_admin)])
async def api_delete_file(uuid: str):
    """Delete a file"""
    await soft_delete_file(uuid, 0)
    return {"status": "success", "message": f"File {uuid} deleted"}


@router.patch("/files/{uuid}/restore", dependencies=[Depends(get_current_admin)])
async def api_restore_file(uuid: str):
    """Restore a file"""
    await restore_file(uuid, 0)
    return {"status": "success", "message": f"File {uuid} restored"}
