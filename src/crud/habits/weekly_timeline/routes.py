from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.db import HabitTimelineDbModel, WeekTrackingDbModel
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
        # build a WeekTrackingDbModel from the incoming Pydantic WeekTracking
        week_db = WeekTrackingDbModel(
            week_start=habit_timeline.week.weekStart,
            week_end=habit_timeline.week.weekEnd,
            total_completed=int(habit_timeline.week.totalCompleted),
            total_steps=habit_timeline.week.totalSteps,
            percentile=int(habit_timeline.week.percentile),
        )

        new_habit_timeline = HabitTimelineDbModel(habit_id=habit_timeline.habitId, weeks=[week_db])
        db.add(new_habit_timeline)
        db.commit()
        db.refresh(new_habit_timeline)
        # return the week we just created (use the incoming pydantic model for correct field names)
        return {"weeks": [habit_timeline.week], "habitId": habit_timeline.habitId}
    else:
        # update existing weeks with newly added week data
        week_db = WeekTrackingDbModel(
            week_start=habit_timeline.week.weekStart,
            week_end=habit_timeline.week.weekEnd,
            total_completed=int(habit_timeline.week.totalCompleted),
            total_steps=habit_timeline.week.totalSteps,
            percentile=int(habit_timeline.week.percentile),
        )

        habit_timeline_exists.weeks.append(week_db)
        db.add(habit_timeline_exists)
        db.commit()
        db.refresh(habit_timeline_exists)

        # build response weeks from DB objects to match response_model names
        response_weeks = []
        for w in habit_timeline_exists.weeks:
            response_weeks.append({
                "weekStart": w.week_start,
                "weekEnd": w.week_end,
                "totalCompleted": w.total_completed,
                "totalSteps": w.total_steps,
                "percentile": w.percentile,
            })

        return {"weeks": response_weeks, "habitId": habit_timeline_exists.habit_id}

    
    return {"error": "Habit timeline already exists"}