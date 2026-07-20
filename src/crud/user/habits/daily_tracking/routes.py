from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import math

from src.models.api import DailyHabitTrackingRequest as DailyTrackingApiSchema
from src.models.db import DailyTrackingOfHabit
from src.util.db import get_db
from src.util.oauth2 import get_current_user

user_daily_tracking_router = APIRouter(prefix="/user-habit-daily-tracking", tags=["user-habit-daily-tracking"])


@user_daily_tracking_router.get("/health")
async def user_daily_tracking_health_check():
    return {"status": "user-daily-tracking router is healthy"}

@user_daily_tracking_router.get("/habit-timeline/{habit_id}")
async def get_user_daily_tracking(habit_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    if user_id is None:
        return {"error": "User not authenticated"}
    
    if habit_id is None:
        return {"error": "Habit ID not provided"}

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
            "percentile": math.floor((entry.steps_completed/entry.steps_total) * 100),
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
            # now will be working with step id and notes for each of those steps
            "steps_completed_with_notes": entry.steps_completed_with_notes
        })

    return {"daily_tracking_timeline": response}

@user_daily_tracking_router.post("/habit-timeline")
async def create_user_daily_tracking(daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):

    if user_id is None:
        return {"error": "User not authenticated"}
    
    step_ids_with_notes = [{"id": step.id, "notes": step.notes} for step in daily_tracking.completedSteps]
    
    new_tracking = DailyTrackingOfHabit(
        habit_id=daily_tracking.habitId,
        steps_completed=len(step_ids_with_notes),
        steps_total=daily_tracking.totalSteps,
        date_stamp=daily_tracking.dateStamp,
        steps_completed_with_notes=step_ids_with_notes
        
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
        "created_at": new_tracking.created_at,
        "updated_at": new_tracking.updated_at,
        "steps": daily_tracking.steps
    }

    return {"message": "Daily tracking entry created", "entry": resp}

@user_daily_tracking_router.put("/habit-timeline/{tracking_id}")
async def update_user_daily_tracking(tracking_id: int, daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):

    if user_id is None:
        return {"error": "User not authenticated"}
    
    tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.id == tracking_id).first()
    if not tracking_entry:
        return {"error": "No daily tracking entry found for the given ID"}
    
    # this piece confirms how to retrive only related dataStamped data from list  and later have to decide on which props to update based on the retrieved data
    filtered_entry = None

    for entry in tracking_entry:
        if entry.date_stamp == daily_tracking.dateStamp.date():
            filtered_entry = entry
            break

    # lets update filtered entry with recieved data and update completed steps ids based on recieved data

    filtered_entry.steps_completed = len(daily_tracking.completedSteps)
    filtered_entry.steps_total = daily_tracking.totalSteps
    filtered_entry.steps_completed_with_notes = [{"id": step.id, "notes": step.notes} for step in daily_tracking.completedSteps]
    tracking_entry[tracking_entry.index(filtered_entry) -1] = filtered_entry


    if not filtered_entry:
        return {"error": "Daily tracking entry not found for the given date"}

    try:
        db.commit()
        db.refresh(filtered_entry)
    except Exception as e:
        db.rollback()
        print(e, "error>>><<>><<")
        return {"error": "Failed to update daily tracking entry"}
    
    return {"message": "Daily tracking entry found", "entry": tracking_entry}