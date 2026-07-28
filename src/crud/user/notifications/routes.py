from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.util.oauth2 import get_current_user
from src.models.api import FcmUserDeviceToken
from src.models.db import FcmUserDeviceToken as FcmUserDeviceTokenDbModel
from src.util.push_notification import send_push_notification_to_all_user_devices
from src.models.api import UserPushNotificationRequest

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])

# lets create push notification endpoint for authorize user
@notifications_router.post("/push-to-user-device-securely")
async def send_push_notification_to_user_device(payload: UserPushNotificationRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    if payload.message_title is None:
        return {"error": "message_title is required"}
    
    if payload.message_body is None:
        return {"error": "message_body is required"}
    
    return send_push_notification_to_all_user_devices(db, user_id, payload.message_title, payload.message_body)

@notifications_router.post("/fcm-token-save-or-update-securely")
async def fcm_token_save_or_update_securely(payload: FcmUserDeviceToken, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    if payload.fcm_token is None:
        return {"error": "fcm_token is required"}
    
    if payload.device_type is None:
        return {"error": "device_type is required"}
    
    existing_fcm_token = db.query(FcmUserDeviceTokenDbModel).filter_by(user_id=user_id).first()
    if existing_fcm_token:
        existing_fcm_token.fcm_token = payload.fcm_token
        existing_fcm_token.device_type = payload.device_type
        db.commit()
        db.refresh(existing_fcm_token)
        print("fcm_token is now updated")
        return {"message": "fcm_token is now updated"}
    else:
        new_fcm_token = FcmUserDeviceTokenDbModel(user_id=user_id, fcm_token=payload.fcm_token, device_type=payload.device_type)
        db.add(new_fcm_token)
        db.commit()
        print("fcm_token is now saved")
        return {"message": "fcm_token is now saved"}

@notifications_router.post("/fcm-token-save-or-update-test")
async def fcm_token_save_or_update_securely(payload: FcmUserDeviceToken, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    if payload.fcm_token is None:
        return {"error": "fcm_token is required"}
    
    if payload.device_type is None:
        return {"error": "device_type is required"}
    
    return {"message": "fcm_token is ready to be saved or updated"}