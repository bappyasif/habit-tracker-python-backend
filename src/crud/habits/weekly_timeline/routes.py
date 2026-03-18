from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.db import HabitTimelineDbModel
from src.models.api import HabitTimelineTrackingRequest as HabitTimelineApiSchema, HabitTimelineTrackingResponse as HabitTimelineResponseSchema
from src.util.db import get_db

weekly_timeline_router = APIRouter(prefix="/weekly-timeline", tags=["weekly-timeline"])

@weekly_timeline_router.get("/health")
async def weekly_timeline_health_check():
    return {"status": "weekly-timeline router is healthy"}

@weekly_timeline_router.get("/habits/{id}")
async def get_habit_by_id(id: int, db: Session = Depends(get_db)):
    habit_timeline = db.query(HabitTimelineDbModel).filter(HabitTimelineDbModel.id == id).first()
    
    if not habit_timeline:
        return {"error": "Habit not found"}
    
    return { "habit_timeline": habit_timeline }

@weekly_timeline_router.post("/habits", response_model=HabitTimelineResponseSchema)
async def create_habit_weekly_timeline(habit_timeline: HabitTimelineApiSchema, db: Session = Depends(get_db)):
    if not habit_timeline:
        return {"error": "Habit timeline not found"}
        
    print(habit_timeline, "habit_timeline>><<>><<")

    # return { "message": "Habit timeline health test"}

    #  check if habit weekly timeline exists
    habit_timeline_exists = db.query(HabitTimelineDbModel).filter(HabitTimelineDbModel.habit_id == habit_timeline.habitId).first()
    
    if not habit_timeline_exists:
        # new_habit_timeline = HabitTimelineDbModel(habit_id=habit_timeline.habitId, weeks=habit_timeline.weeks)
        # db.add(new_habit_timeline)
        # db.commit()
        # db.refresh(new_habit_timeline)
        return {"weeks": [], "habitId": 0}
    
    return {"error": "Habit timeline already exists"}