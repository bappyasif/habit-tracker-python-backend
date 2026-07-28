from sqlalchemy.orm import Session
from src.models.db import FcmUserDeviceToken as FcmUserDeviceTokenDbModel
from firebase_admin import messaging

def send_push_notification_to_all_user_devices(db: Session, user_id, message_title, message_body):
    # fetch all dvices tokens for this user
    user_tokens = db.query(FcmUserDeviceTokenDbModel).filter(FcmUserDeviceTokenDbModel.user_id == user_id).all()

    if not user_tokens:
        return {"error": "No device tokens found for this user"}
    
    # send push notification to all device tokens
    for device_data in user_tokens:
        # send push notification to this device token
        message = messaging.Message(
            notification=messaging.Notification(
                title=message_title,
                body=message_body
            ),
            token = device_data.fcm_token # targets specific device token
        )

        try:
            response = messaging.send(message)
            print("Successfully sent message:", response)
        except Exception as e:
            print("Error sending message:", str(e))

            # lets clean up if found error due to expired or unregistered device token
            if {"InvalidRegistrationToken", "NotFound", "UNREGISTERED"} in str(e):
                db.delete(device_data)
                db.commit()

    return {"message": "Push notification sent successfully"}