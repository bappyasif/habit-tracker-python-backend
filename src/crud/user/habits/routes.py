from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
# from fastapi import HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jwcrypto import jwt, jwk
from src.util.db import get_db
from src.models.db import Habit as HabitModel
# from src.models.api import Habit as HabitApiSchema
# from src.models.db import User
import json
# import base64
from src.util.oauth2 import get_current_user

user_habits_router = APIRouter(prefix="/user-habits", tags=["user-habits"])


@user_habits_router.get("/")
async def get_user_habits():
    return {"message": "Get user habits"}

@user_habits_router.get("/secured")
async def get_current_user_habits(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    # get current user habits
    habits = db.query(HabitModel).filter(HabitModel.user_id == user_id).all()
    
    if not habits:
        return {"error": "No habits found for this given user"}
    
    modified_habits = []

    for habit in habits:
        modified_habit = {
            "id": habit.id,
            "title": habit.title,
            "description": habit.description,
            "duration": habit.duration,
            "frequency": habit.frequency.value,
            "steps": [
                {
                    "id": step.id,
                    "title": step.title,
                    "time": step.time.isoformat() if getattr(step, "time", None) else None,
                    "completed": step.completed,
                    "notes": step.notes,
                    "datestamp": step.datestamp.isoformat() if getattr(step, "datestamp", None) else None,
                }
                for step in habit.steps
            ],
            "measurement": json.loads(habit.measurement[0].measurement) if habit.measurement else None,
            "successDefinition": json.loads(habit.success_definition.success_definition) if habit.success_definition else None,
            "createdAt": habit.created_at.isoformat(),
            "updatedAt": habit.updated_at.isoformat(),
        }
        modified_habits.append(modified_habit)
        
    return {"habits": modified_habits}

# get user specefic habits
@user_habits_router.get("/{user_id}")
async def get_user_habits(user_id: int, db: Session = Depends(get_db)):
    habits = db.query(HabitModel).filter(HabitModel.user_id == user_id).all()
    
    if not habits:
        return {"error": "No habits found for this given user"}
    
    modified_habits = []
    for habit in habits:
        modified_habit = {
            "id": habit.id,
            "title": habit.title,
            "description": habit.description,
            "duration": habit.duration,
            "frequency": habit.frequency.value,
            "steps": [
                {
                    "id": step.id,
                    "title": step.title,
                    "time": step.time.isoformat() if getattr(step, "time", None) else None,
                    "completed": step.completed,
                    "notes": step.notes,
                    "datestamp": step.datestamp.isoformat() if getattr(step, "datestamp", None) else None,
                }
                for step in habit.steps
            ],
            "measurement": json.loads(habit.measurement[0].measurement) if habit.measurement else None,
            "successDefinition": json.loads(habit.success_definition.success_definition) if habit.success_definition else None,
            "createdAt": habit.created_at.isoformat(),
            "updatedAt": habit.updated_at.isoformat(),
        }
        modified_habits.append(modified_habit)
        
    return {"habits": modified_habits}



# get user specific habits but in more secured way
# 1. Define your signing key (Must match the key used to create tokens)
# SECRET_KEY = "your-secret-key-must-be-long-enough-for-jwcrypto"
# SECRET_KEY = "your-super-long-and-secure-secret-key-32-chars!!"

# jwcrypto requires a JWK object for verification
# signing_key = jwk.JWK(kty='oct', k=SECRET_KEY.encode('utf-8'))

# 1. Encode the plain text string to base64url bytes
# b64_key = base64.urlsafe_b64encode(SECRET_KEY.encode('utf-8')).decode('utf-8')

# 2. Clean up padding characters ("=") which jwcrypto dislikes
# b64_key = b64_key.rstrip("=")

# 3. Pass the valid base64url string to the JWK constructor
# signing_key = jwk.JWK(kty='oct', k=b64_key)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Update your oauth2_scheme instance to match your router path
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user-authorize/with-jwt")

# async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         # 2. Parse and verify the token using jwcrypto
#         jwt_token = jwt.JWT(jwt=token, key=signing_key)
        
#         # 3. Extract the JSON claims string and parse it to a dictionary
#         claims = json.loads(jwt_token.claims)
        
#         # 4. Extract your user ID from the claims (usually the 'sub' field)
#         decoded_user_id = claims.get("sub")
#         if decoded_user_id is None:
#             raise credentials_exception
            
#     except Exception as e: # Catches jwcrypto validation errors
#         # 🚨 THIS IS CRITICAL: Check your terminal logs for this print statement!
#         print(f"❌ Verification failed because: {str(e)}")
#         raise credentials_exception

#     # 5. Query your database
#     user = db.query(User).filter(User.id == int(decoded_user_id)).first()
#     print(user, "!!user found!!")
#     if user is None:
#         raise credentials_exception
        
#     return user

# @user_habits_router.get("/secured")
# async def get_current_user_habits(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     # return {"message": "Get current user habits", "user_id": user.id}
#     habits = db.query(HabitModel).filter(HabitModel.user_id == user.id).all()
    
#     if not habits:
#         return {"error": "No habits found for this given user"}
    
#     modified_habits = []
#     for habit in habits:
#         modified_habit = {
#             "id": habit.id,
#             "title": habit.title,
#             "description": habit.description,
#             "duration": habit.duration,
#             "frequency": habit.frequency.value,
#             "steps": [
#                 {
#                     "id": step.id,
#                     "title": step.title,
#                     "time": step.time.isoformat() if getattr(step, "time", None) else None,
#                     "completed": step.completed,
#                     "notes": step.notes,
#                     "datestamp": step.datestamp.isoformat() if getattr(step, "datestamp", None) else None,
#                 }
#                 for step in habit.steps
#             ],
#             "measurement": json.loads(habit.measurement[0].measurement) if habit.measurement else None,
#             "successDefinition": json.loads(habit.success_definition.success_definition) if habit.success_definition else None,
#             "createdAt": habit.created_at.isoformat(),
#             "updatedAt": habit.updated_at.isoformat(),
#         }
#         modified_habits.append(modified_habit)
        
#     return {"habits": modified_habits}