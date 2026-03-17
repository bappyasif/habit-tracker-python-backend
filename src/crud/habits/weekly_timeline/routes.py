from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.db import Habit as HabitModel
from src.util.db import get_db

weekly_timeline_router = APIRouter(prefix="/weekly-timeline", tags=["weekly-timeline"])

@weekly_timeline_router.get("/health")
async def weekly_timeline_health_check():
    return {"status": "weekly-timeline router is healthy"}

@weekly_timeline_router.get("/habits/{id}")
async def get_habit_by_id(id: int, db: Session = Depends(get_db)):
    habit = db.query(HabitModel).filter(HabitModel.id == id).first()
    return {"habit": habit}