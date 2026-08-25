from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from src.util.db import get_db
from src.util.oauth2 import get_current_user

from src.models.db import UserSettings
from src.models.api import UserSettingsRequest

settings_router = APIRouter(prefix="/settings", tags=["settings"])


@settings_router.get("/health")
async def settings_health_check():
    return {"status": "settings router is healthy"}

@settings_router.put("/toggle-send-emails-notifications-securely")
async def toggle_send_emails_notifications( payload: UserSettingsRequest, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    print(f'--> DEBUG: user_id: {user_id}, email_permission: {payload.email_permission}')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    
    user = db.query(UserSettings).filter_by(user_id=user_id).first()

    # Access the property using payload.email_permission
    if user is None:
        user_settings = UserSettings(
            user_id=user_id, 
            settings={"send_emails_notifications": payload.email_permission}
        )
        db.add(user_settings)
        db.commit()
        return {"message": "Email notifications initialized"}
    
    print(f'--> DEBUG: User settings found: {user.settings}')
    
    # 3. Update the dict AND flag it so SQLAlchemy tracks the change
    user.settings["send_emails_notifications"] = payload.email_permission
    flag_modified(user, "settings") 
    
    # 4. Commit the changes
    db.commit()

    print(f'--> DEBUG: User settings updated: {user.settings}')
    
    return {"message": "Email notifications updated"}

    # if user_id is None:
    #     return {"error": "User not authenticated"}
    
    # user = db.query(UserSettings).filter_by(user_id=user_id).first()

    # if user is None:
    #     # lets create a new user settings row
    #     user_settings = UserSettings(user_id=user_id, settings={"send_emails_notifications": True})
    #     db.add(user_settings)
    #     db.commit()
    #     user = db.query(UserSettings).filter_by(user_id=user_id).first()
    #     print(f'--> DEBUG: User settings created: {user.settings}')
    #     return {"message": "Email notifications defaulted to on"}
    
    # print(f'--> DEBUG: User settings found: {user.settings}')

    # converted_email_permission = True if payload.email_permission == "true" else False

    # print(f'--> DEBUG: Converted email permission: {converted_email_permission}')
    
    # # user.settings["send_emails_notifications"] = not user.settings["send_emails_notifications"]
    # user.settings["send_emails_notifications"] = converted_email_permission
    # db.commit()
    
    # print(f'--> DEBUG: User settings updated: {user.settings}')

    # return {"message": "Email notifications toggled"}