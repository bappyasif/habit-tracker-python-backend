from fastapi import APIRouter

authorize_user_router = APIRouter(prefix="/user-authorize", tags=["authorize"])

@authorize_user_router.get("/health")
async def authorize_user_health_check():
    return {"status": "authorize router is healthy"}

# get a specefic authorized user by email
@authorize_user_router.get("/{email}")
async def get_authorized_user_by_email(email: str):
    # Here you would typically query your database to find the user by email.
    # For demonstration purposes, we'll return a mock response.
    mock_user = {
        "email": email,
        "name": "John Doe",
        "authorized": True
    }
    return {"user": mock_user}

# authorize a user with email, image, name in request object
@authorize_user_router.post("/")
async def authorize_user(user: dict):
    print(f"Authorizing user: {user}")
    
    # Here you would typically save the user to your database and perform any necessary authorization logic.
    # For demonstration purposes, we'll return a mock response.
    mock_response = {
        "message": "User authorized successfully",
        "user": user
    }

    return mock_response