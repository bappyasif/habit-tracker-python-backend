from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.models.db import User
from src.models.api import UserAuthorizeRequest

authorize_user_router = APIRouter(prefix="/user-authorize", tags=["authorize"])

@authorize_user_router.get("/health")
async def authorize_user_health_check():
    return {"status": "authorize router is healthy"}

# get a specefic authorized user by email
@authorize_user_router.get("/{email}")
async def get_authorized_user_by_email(email: str, db: Session = Depends(get_db)):
    print(f"Getting authorized user by email: {email}")

    # Query the database to find the user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "User not found"}

    # Return the user information
    return {"user": user}

    # Here you would typically query your database to find the user by email.
    # For demonstration purposes, we'll return a mock response.
    # mock_user = {
    #     "email": email,
    #     "name": "John Doe",
    #     "authorized": True
    # }
    # return {"user": mock_user}


@authorize_user_router.post("/")
async def authorize_user(payload: dict, db: Session = Depends(get_db)):
    print(f"Authorizing user: {payload}")

    # Check if the user already exists in the database
    existing_user = db.query(User).filter_by(email=payload["email"]).first()
    print(f"Existing user: {existing_user}", existing_user.id)

    if existing_user:
        return {"msg": "User already exists", "user": existing_user}

    # Create a new user in the database
    new_user = User(email=payload["email"], name=payload["name"], image=payload["image"])
    db.add(new_user)
    db.commit()

    return {"message": "User authorized successfully", "user": new_user}


# @authorize_user_router.post("/")
# async def authorize_user(user: dict, db: Session = Depends(get_db)):
#     print(f"Authorizing user: {user}")

#     # Here you would typically save the user to your database and perform any necessary authorization logic.
#     # For demonstration purposes, we'll return a mock response.
#     # mock_response = {
#     #     "message": "User authorized successfully",
#     #     "user": user
#     # }

#     # return mock_response

#     # Check if the user already exists in the database
#     existing_user = db.query(User).filter_by(email=user["email"]).first()
#     print(f"Existing user: {existing_user}", existing_user.id)
#     # Replace your existing_user line with this:
#     # existing_user = db.query(User.id).filter(User.email == user["email"]).first()
#     if existing_user:
#         return {"msg": "User already exists", "user": existing_user}

#     # Create a new user in the database
#     new_user = User(email=user["email"], name=user["name"], image=user["image"])
#     db.add(new_user)
#     db.commit()

#     return {"message": "User authorized successfully", "user": new_user}
    
#     # Here you would typically save the user to your database and perform any necessary authorization logic.
#     # For demonstration purposes, we'll return a mock response.
#     # mock_response = {
#     #     "message": "User authorized successfully",
#     #     "user": user
#     # }

#     # return mock_response