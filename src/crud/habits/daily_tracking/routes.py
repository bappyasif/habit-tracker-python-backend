from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from src.models.db import DailyTrackingOfHabit
# from src.models.api import DailyTrackingRequest as DailyTrackingApiSchema, DailyTrackingResponse as DailyTrackingResponseSchema
from src.models.api import DailyHabitTrackingRequest as DailyTrackingApiSchema
from src.models.db import DailyTrackingOfHabit
from src.util.db import get_db

daily_tracking_router = APIRouter(prefix="/daily-tracking", tags=["daily-tracking"])

@daily_tracking_router.get("/health")
async def daily_tracking_health_check():
    return {"status": "daily-tracking router is healthy"}

@daily_tracking_router.get("/habit-timeline/{habit_id}")
async def get_daily_tracking(habit_id: int, db: Session = Depends(get_db)):
    tracking_entries = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.habit_id == habit_id).all()
    if not tracking_entries:
        return {"error": "No daily tracking entries found for the given habit ID"}
    
    response = []
    for entry in tracking_entries:
        response.append({
            "id": entry.id,
            "habit_id": entry.habit_id,
            "date_stamp": entry.date_stamp,
            "steps_completed": entry.steps_completed,
            "steps_total": entry.steps_total,
            # "steps": [step.id for step in entry.steps],  # Assuming you want to return the IDs of the steps
            "completed_steps_ids": entry.completed_steps_ids,
            "notes": entry.notes,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at
        })

    return {"daily_tracking_timeline": response}

@daily_tracking_router.post("/habit-timeline")
async def create_daily_tracking(daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db)):
    if not daily_tracking:
        return {"error": "Daily tracking data not found"}
    print(daily_tracking, "daily_tracking>><<>><<")

    step_ids = [step.id for step in daily_tracking.completedSteps]
    print(step_ids, "step_ids>>><<>><<")
    
    new_tracking = DailyTrackingOfHabit(
        habit_id=daily_tracking.habitId,
        # steps_completed=len(daily_tracking.completedSteps),
        steps_completed=len(step_ids),
        steps_total=daily_tracking.totalSteps,
        date_stamp=daily_tracking.dateStamp,
        notes=daily_tracking.notes if hasattr(daily_tracking, 'notes') else None,
        # created_at=daily_tracking.dateStamp,
        # updated_at=daily_tracking.dateStamp
        completed_steps_ids=step_ids
    )

    db.add(new_tracking)
    db.commit()
    db.refresh(new_tracking)

    resp =  {
        "id": new_tracking.id,
        "habit_id": new_tracking.habit_id,
        "date_stamp": new_tracking.date_stamp,
        "steps_completed": new_tracking.steps_completed,
        "steps_total": new_tracking.steps_total,
        "notes": new_tracking.notes,
        "created_at": new_tracking.created_at,
        "updated_at": new_tracking.updated_at,
        "steps": daily_tracking.steps
    }

    return {"message": "Daily tracking entry created", "entry": resp}