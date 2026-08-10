from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

import firebase_admin
from firebase_admin import credentials

from src.crud.genai.routes import genai_router
from src.crud.habits.routes import habits_router
from src.crud.habits.weekly_timeline.routes import weekly_timeline_router
from src.crud.habits.daily_tracking.routes import daily_tracking_router
from src.crud.user.routes import users_router
from src.crud.user.authorize.routes import authorize_user_router
from src.crud.user.habits.routes import user_habits_router
from src.crud.user.habits.daily_tracking.routes import user_daily_tracking_router
from src.crud.user.notifications.routes import notifications_router

# Check if the GitHub Actions CI generated file exists, otherwise use local file name
# if os.path.exists("serviceAccountKey.json"):
#     cred_path = "serviceAccountKey.json"
# else:
#     cred_path = "./habitflow-developed-by-abappy-firebase-adminsdk-fbsvc-767604dbb4.json"

# cred = credentials.Certificate("./habitflow-developed-by-abappy-firebase-adminsdk-fbsvc-767604dbb4.json")
# cred = credentials.Certificate(cred_path)
# firebase_admin.initialize_app(cred)

cred_path = "./habitflow-developed-by-abappy-firebase-adminsdk-fbsvc-767604dbb4.json"

# If the local JSON file doesn't exist (like on Render), generate it from the environment variable
if not os.path.exists(cred_path):
    json_secret = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if json_secret:
        # Write the secret string to the file path your code expects
        with open(cred_path, "w", encoding="utf-8") as f:
            f.write(json_secret)

# Now initialize firebase normally
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
else:
    raise FileNotFoundError("Firebase service account credentials could not be found.")


server = FastAPI(
    title="Habit Tracker Backend",
    description="FastAPI Server",
    version="0.0.1",
)

# CORS
# no trailing slashes or it will fail on live environment
origins = ["/localhost", "http://localhost:3000", "http://localhost:8000", "https://habit-tracker-phi-rouge.vercel.app"]

server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize db
from src.util.db import create_tables
create_tables()

# Routes
# server.include_router(genai_router)

# Versioned Routes
server.include_router(genai_router, prefix="/api/v1")

server.include_router(habits_router, prefix="/api/v1")

server.include_router(weekly_timeline_router, prefix="/api/v1")

server.include_router(daily_tracking_router, prefix="/api/v1")

server.include_router(users_router, prefix="/api/v1")
server.include_router(authorize_user_router, prefix="/api/v1")
server.include_router(user_habits_router, prefix="/api/v1")
server.include_router(user_daily_tracking_router, prefix="/api/v1")

server.include_router(notifications_router, prefix="/api/v1")

# Health Check
@server.get("/")
async def root():
    return {"message": "Hello World, from FastAPI!"}