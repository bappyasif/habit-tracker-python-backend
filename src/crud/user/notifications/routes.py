from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.util.oauth2 import get_current_user
from src.models.api import FcmUserDeviceToken

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])

@notifications_router.post("/fcm-token-save-or-update-securely")
async def fcm_token_save_or_update_securely(payload: FcmUserDeviceToken, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    if payload.fcm_token is None:
        return {"error": "fcm_token is required"}
    
    if payload.device_type is None:
        return {"error": "device_type is required"}
    
    return {"message": "fcm_token is ready to be saved or updated"}