from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.models.db import Habit as HabitModel
from src.models.api import Habit as HabitApiSchema
import json

user_habits_router = APIRouter(prefix="/user-habits", tags=["user-habits"])


@user_habits_router.get("/")
async def get_user_habits():
    return {"message": "Get user habits"}

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