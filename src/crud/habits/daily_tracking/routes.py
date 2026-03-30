from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from src.models.db import DailyTrackingOfHabit
# from src.models.api import DailyTrackingRequest as DailyTrackingApiSchema, DailyTrackingResponse as DailyTrackingResponseSchema
from src.models.api import DailyHabitTrackingRequest as DailyTrackingApiSchema
from src.util.db import get_db

daily_tracking_router = APIRouter(prefix="/daily-tracking", tags=["daily-tracking"])

@daily_tracking_router.get("/health")
async def daily_tracking_health_check():
    return {"status": "daily-tracking router is healthy"}

@daily_tracking_router.post("/habit-timeline")
async def create_daily_tracking(daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db)):
    if not daily_tracking:
        return {"error": "Daily tracking data not found"}
    print(daily_tracking, "daily_tracking>><<>><<")
    # new_tracking = DailyTrackingOfHabit(
    #     habit_id=daily_tracking.habitId,
    #     steps_completed=len(daily_tracking.completedSteps),
    #     steps_total=daily_tracking.totalSteps,
    #     notes=daily_tracking.notes if hasattr(daily_tracking, 'notes') else None,
    #     created_at=daily_tracking.dateStamp,
    #     updated_at=daily_tracking.dateStamp
    # )

    # db.add(new_tracking)
    # db.commit()
    # db.refresh(new_tracking)
    return {"message": "Daily tracking entry created", "entry": daily_tracking}