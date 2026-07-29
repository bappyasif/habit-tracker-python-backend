from sqlalchemy.orm import Session
from src.models.db import FcmUserDeviceToken as FcmUserDeviceTokenDbModel
from firebase_admin import messaging

def test_direct_token_based_push_notification(user_id, db: Session):
        # Grab the latest token for this user
    token_record = db.query(FcmUserDeviceTokenDbModel).filter_by(user_id=user_id).first()
    
    if not token_record:
        return {"status": "No token found in database for this user ID!"}
    
    print(f"Testing push to token: {token_record.fcm_token}")
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="Direct Test Title",
                body="Direct Test Body Works!"
            ),
            token=token_record.fcm_token
        )
        response = messaging.send(message)
        return {"status": "success", "firebase_response": response}
    except Exception as e:
        return {"status": "error", "error": str(e)}

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
            return {"status": "success", "firebase_response": response}
        except Exception as e:
            error_message = str(e)
            print(f"Failed to send to token {device_data.fcm_token}: {error_message}")
            
            # FIX: Correctly check if error strings match Firebase's unregistration responses
            if any(err in error_message for err in ["UNREGISTERED", "NOT_FOUND", "InvalidRegistrationToken"]):
                print(f"Removing dead/unregistered token from database: {device_data.fcm_token}")
                db.delete(device_data)
                db.commit()
        # except Exception as e:
        #     print("Error sending message:", str(e))

        #     # lets clean up if found error due to expired or unregistered device token
        #     if {"InvalidRegistrationToken", "NotFound", "UNREGISTERED"} in str(e):
        #         db.delete(device_data)
        #         db.commit()

    # return {"message": "Push notification sent successfully"}