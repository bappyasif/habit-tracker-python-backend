from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/")
async def get_all_authorized_users():
    return {"message": "Get all users"}