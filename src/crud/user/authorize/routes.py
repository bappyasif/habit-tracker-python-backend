from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.models.db import User
from src.models.api import UserAuthorizeRequest
import json
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jwcrypto import jwt, jwk
import base64
from src.util.oauth2 import create_access_token

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

@authorize_user_router.post("/with-jwt")
async def authorize_user(payload: UserAuthorizeRequest, db: Session = Depends(get_db)):
    print(f"Authorizing user: {payload}")

    # Check if the user already exists in the database
    # existing_user = db.query(User).filter_by(email=payload["email"]).first()
    existing_user = db.query(User).filter_by(email=payload.email).first()

    print(f"Existing user: {existing_user}")

    access_token = None

    if not existing_user:
        # new_user = User(email=payload["email"], name=payload["name"], image=payload["image"])
        new_user = User(email=payload.email, name=payload.name, image=payload.image)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = create_access_token(new_user.id)
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": new_user
        }
    else:
        access_token = create_access_token(existing_user.id)

    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": existing_user
        }


@authorize_user_router.post("/with-jwt-legacy")
async def authorize_user(payload: UserAuthorizeRequest, db: Session = Depends(get_db)):
    print(f"Authorizing user: {payload}")

    # Check if the user already exists in the database
    # existing_user = db.query(User).filter_by(email=payload["email"]).first()
    # Change this:
# existing_user = db.query(User).filter_by(email=payload["email"]).first()

# To this:
    existing_user = db.query(User).filter_by(email=payload.email).first()

    print(f"Existing user: {existing_user}", existing_user.id)

    if not existing_user:
        new_user = User(email=payload["email"], name=payload["name"], image=payload["image"])
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    token_expiry = datetime.now(timezone.utc) + timedelta(days=1)
    claims = {
        "sub": str(existing_user.id),
        "email": existing_user.email,
        "exp": int(token_expiry.timestamp()),
    }
    
    # Generate the signed token using JWCrypto
    # (Ensure SECRET_KEY_STRING matches the key used in your token verification script)
    SECRET_KEY_STRING = "your-super-long-and-secure-secret-key-32-chars!!"
    # signing_key = jwk.JWK(kty='oct', k=SECRET_KEY_STRING.encode('utf-8'))
    # 1. Encode the plain text string to base64url bytes
    b64_key = base64.urlsafe_b64encode(SECRET_KEY_STRING.encode('utf-8')).decode('utf-8')

    # 2. Clean up padding characters ("=") which jwcrypto dislikes
    b64_key = b64_key.rstrip("=")

    # 3. Pass the valid base64url string to the JWK constructor
    signing_key = jwk.JWK(kty='oct', k=b64_key)

    jwt_token = jwt.JWT(header={"alg": "HS256"}, claims=claims)
    jwt_token.make_signed_token(signing_key)
    access_token = jwt_token.serialize().encode('utf-8')

    # 5. Return the access token alongside user info to the frontend
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "email": existing_user.email,
            "name": existing_user.name,
            "image": existing_user.image
        }
    }



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