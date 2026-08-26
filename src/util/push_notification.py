from sqlalchemy.orm import Session
from datetime import date, datetime, time
from src.models.db import FcmUserDeviceToken as FcmUserDeviceTokenDbModel, UserNotification as UserNotificationDbModel, User, UserSettings
from firebase_admin import messaging
from src.util.email_service import send_habit_completion_email, send_habit_deleted_email

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
    
def send_notification_on_completing_habit_daily_steps_fully(user_id, db: Session):
    today = date.today()

    # 1. Define the start and end timestamps for the current day
    today_start = datetime.combine(date.today(), time.min) # e.g., 2026-07-30 00:00:00
    today_end = datetime.combine(date.today(), time.max)     # e.g., 2026-07-30 23:59:59

    existing_notification = db.query(UserNotificationDbModel).filter(UserNotificationDbModel.user_id == user_id, UserNotificationDbModel.created_at.between(today_start, today_end), UserNotificationDbModel.title == "All steps completed for today").first()

    print(f"existing_notification: {existing_notification}")

    if existing_notification:
        return {"status": "success", "firebase_response": "Notification already sent for today"}
    
    # now that we are sure its not sent yet lets add it to notifications table
    add_notification_to_db(db, user_id, "All steps completed for today", "You have completed all your steps for today!")

def send_push_notification_to_users_devices_on_daily_completion(user_id, db: Session):
    send_notification_on_completing_habit_daily_steps_fully(user_id, db)
    send_push_notification_to_all_user_devices(db, user_id, "All steps completed for today", "You have completed all your steps for today!")
    try:
        user = db.query(User).filter_by(id=user_id).first()
        send_habit_completion_email(user.email, user.name)
    except Exception as e:
        print(f"Failed to send daily habit steps completed fully milestone email: {e}")

def send_push_notification_to_user_devices_completing_one_habit_step(user_id, db: Session):
    title = "Habit step successfully completed!"
    body = "You have successfully completed a step in one of your habit!"
    send_push_notification_to_all_user_devices(db, user_id, title, body)
    add_notification_to_db(db, user_id, title, body)

def send_push_notification_to_user_devices_updating_one_habit_step(user_id, db: Session):
    title = "Habit step successfully Updated!"
    body = "You have successfully updated a step in one of your habit!"
    send_push_notification_to_all_user_devices(db, user_id, title, body)
    add_notification_to_db(db, user_id, title, body)

def send_push_notification_user_device_on_creating_new_habit(user_id, db: Session):
    title = "New Habit Created!"
    body = "You have successfully created a new habit!"
    send_push_notification_to_all_user_devices(db, user_id, title, body)
    add_notification_to_db(db, user_id, title, body)

def send_push_notification_user_device_on_deleting_habit(user_id, db: Session):
    title = "Habit Deleted!"
    body = "You have successfully deleted a habit!"
    send_push_notification_to_all_user_devices(db, user_id, title, body)
    add_notification_to_db(db, user_id, title, body)

    try:
        user = db.query(User).filter_by(id=user_id).first()
        send_habit_deleted_email(user.email, user.name)
    except Exception as e:
        print(f"Failed to send habit deleted milestone email: {e}")

def send_push_notification_user_device_on_updating_habit(user_id, db: Session):
    title = "Habit Updated!"
    body = "You have successfully updated a habit!"
    send_push_notification_to_all_user_devices(db, user_id, title, body)
    add_notification_to_db(db, user_id, title, body)

def check_user_permission_for_emails_push_notifications(user_id, db: Session):
    user_settings = db.query(UserSettings).filter_by(user_id=user_id).first()
    return user_settings.settings["send_emails_notifications"]

def add_notification_to_db(db: Session, user_id, message_title, message_body):
    try:
        if check_user_permission_for_emails_push_notifications(user_id, db):
            new_notification = UserNotificationDbModel(user_id=user_id, title=message_title, body=message_body)
            db.add(new_notification)
            db.commit()
        else:
            print("User has disabled email notifications")
    except Exception as e:
        print(f"Error saving notification to database: {e}")
        return {"error": str(e)}

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