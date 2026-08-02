from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.util.oauth2 import get_current_user
from src.models.api import FcmUserDeviceToken
from src.models.db import FcmUserDeviceToken as FcmUserDeviceTokenDbModel, UserNotification as UserNotificationDbModel
from src.util.push_notification import send_push_notification_to_all_user_devices, test_direct_token_based_push_notification, send_push_notification_to_users_devices_on_daily_completion, send_push_notification_to_user_devices_completing_one_habit_step, send_push_notification_to_user_devices_updating_one_habit_step
from src.models.api import UserPushNotificationRequest

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])

@notifications_router.get("/tray-list-securely")
async def get_notification_tray(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    try:
        notifications = db.query(UserNotificationDbModel).filter_by(user_id=user_id).all()
        
        formatted_for_frontend = []
        
        for notification in notifications:
            formatted_for_frontend.append({
                "id": notification.id,
                "title": notification.title,
                "description": notification.body,
                "isRead": notification.is_read,
                "createdAt": notification.created_at
            })
        
        return {"notifications": formatted_for_frontend}
    except Exception as e:
        return {"error": str(e)}
    
@notifications_router.put("/mark-notification-as-read-securely/{notification_id}")
async def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    if notification_id is None:
        return {"error": "notification_id is required"}
    
    try:
        notification = db.query(UserNotificationDbModel).filter_by(id=notification_id).first()
        if notification:
            notification.is_read = True
            db.commit()
            return {"message": "Notification marked as read"}
        else:
            return {"error": "Notification not found"}
    except Exception as e:
        return {"error": str(e)}

@notifications_router.post("/daily-habit-step-completion-securely")
async def daily_habit_step_completion(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    return send_push_notification_to_user_devices_completing_one_habit_step(user_id, db)

@notifications_router.post("/daily-habit-step-updates-securely")
async def daily_habit_step_completion(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    return send_push_notification_to_user_devices_updating_one_habit_step(user_id, db)

@notifications_router.post("/habit-daily-total-steps-completion-securely")
async def daily_total_steps_completion(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    return send_push_notification_to_users_devices_on_daily_completion(user_id, db)

@notifications_router.post("/test-direct-push/{user_id}")
async def test_direct_push(user_id: int, db: Session = Depends(get_db)):
    return test_direct_token_based_push_notification(user_id, db)

# lets create push notification endpoint for authorize user
@notifications_router.post("/push-to-user-device-securely")
async def send_push_notification_to_user_device(payload: UserPushNotificationRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    if payload.message_title is None:
        return {"error": "message_title is required"}
    
    if payload.message_body is None:
        return {"error": "message_body is required"}
    
    print(f"--> DEBUG: Notification requested by verified user_id: {user_id}")
    
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