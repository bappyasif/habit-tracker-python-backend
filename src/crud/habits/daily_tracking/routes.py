from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import math

# from src.models.db import DailyTrackingOfHabit
# from src.models.api import DailyTrackingRequest as DailyTrackingApiSchema, DailyTrackingResponse as DailyTrackingResponseSchema
from src.models.api import DailyHabitTrackingRequest as DailyTrackingApiSchema
from src.models.db import DailyTrackingOfHabit, DailyTrackingStep
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
            "percentile": math.floor((entry.steps_completed/entry.steps_total) * 100),
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

@daily_tracking_router.put("/habit-timeline/{tracking_id}")
async def update_daily_tracking(tracking_id: int, daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db)):
    print(daily_tracking, "daily_tracking>><<>><<")

    tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.habit_id == daily_tracking.habitId).all()

    print(len(tracking_entry), "tracking_entry>>><<>><<")

    if not len(tracking_entry):
        return {"error": "Daily tracking entry not found"}
    
    # this piece confirms how to retrive only related dataStamped data from list  and later have to decide on which props to update based on the retrieved data
    filtered_entry = None

    for entry in tracking_entry:
        if entry.date_stamp == daily_tracking.dateStamp.date():
            filtered_entry = entry
            break

    # lets update filtered entry with recieved data and update completed steps ids based on recieved data

    filtered_entry.steps_completed = len(daily_tracking.completedSteps)
    filtered_entry.steps_total = daily_tracking.totalSteps
    filtered_entry.notes = daily_tracking.notes if hasattr(daily_tracking, 'notes') else None
    filtered_entry.completed_steps_ids = [step.id for step in daily_tracking.completedSteps]

    # i want this tracking entry data to be updated with filtered entry
    # tracking_entry[tracking_entry.index(filtered_entry.id)] = filtered_entry
    tracking_entry[tracking_entry.index(filtered_entry) -1] = filtered_entry


    if not filtered_entry:
        return {"error": "Daily tracking entry not found for the given date"}
    
    print(filtered_entry, "filtered_entry>>><<>><<", filtered_entry.__dict__.items())

    try:
        db.commit()
        db.refresh(filtered_entry)
    except Exception as e:
        db.rollback()
        print(e, "error>>><<>><<")
        return {"error": "Failed to update daily tracking entry"}
    
    return {"message": "Daily tracking entry found", "entry": tracking_entry}

# @daily_tracking_router.put("/habit-timeline/{tracking_id}")
# async def update_daily_tracking(tracking_id: int, daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db)):
#     print(daily_tracking, "daily_tracking>><<>><<")

#     tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.habit_id == daily_tracking.habitId).all()

#     print(len(tracking_entry), "tracking_entry>>><<>><<")

#     if not len(tracking_entry):
#         return {"error": "Daily tracking entry not found"}
    
#     # this piece confirms how to retrive only related dataStamped data from list  and later have to decide on which props to update based on the retrieved data
#     filtered_entry = None

#     for entry in tracking_entry:
#         if entry.date_stamp == daily_tracking.dateStamp.date():
#             filtered_entry = entry
#             break

#     if not filtered_entry:
#         return {"error": "Daily tracking entry not found for the given date"}
    
#     print(filtered_entry, "filtered_entry>>><<>><<", filtered_entry.__dict__.items())

#     # get daily steps from db
#     daily_steps = db.query(DailyTrackingStep).filter(DailyTrackingStep.daily_tracking_id == filtered_entry.id).all()

#     all_steps = db.query(DailyTrackingStep).all()

#     print(daily_steps, "daily_steps>>><<>><<", len(daily_steps))

#     print(all_steps, "all_steps>>><<>><<", len(all_steps))

#     # update daily steps
#     for step in daily_steps:
#         if step.habit_step_id in daily_tracking.completedStepsIds:
#             step.completed = True
#         else:
#             step.completed = False
    
#     return {"message": "Daily tracking entry found", "entry": tracking_entry}

# @daily_tracking_router.put("/habit-timeline/{tracking_id}")
# async def update_daily_tracking(tracking_id: int, daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db)):
#     # tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.id == tracking_id).first()

#     print(daily_tracking, "daily_tracking>><<>><<")

#     tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.habit_id == daily_tracking.habitId).all()

#     print(len(tracking_entry), "tracking_entry>>><<>><<")

#     if not len(tracking_entry):
#         return {"error": "Daily tracking entry not found"}
    
#     # this piece confirms how to retrive only related dataStamped data from list  and later have to decide on which props to update based on the retrieved data
#     filtered_entry = None

#     for entry in tracking_entry:
#         if entry.date_stamp == daily_tracking.dateStamp.date():
#             filtered_entry = entry
#             break

#     if not filtered_entry:
#         return {"error": "Daily tracking entry not found for the given date"}
    
#     print(filtered_entry, "filtered_entry>>><<>><<", filtered_entry.__dict__.items())

#     # get daily steps from db
#     daily_steps = db.query(DailyTrackingStep).filter(DailyTrackingStep.daily_tracking_id == filtered_entry.id).all()

#     all_steps = db.query(DailyTrackingStep).all()

#     print(daily_steps, "daily_steps>>><<>><<", len(daily_steps))

#     print(all_steps, "all_steps>>><<>><<", len(all_steps))

#     # for item in dir(daily_steps):
#     #     print(item, "item>>><<>><<")

#     # for item in daily_steps.__dict__.items():
#     #     print(item, "item>>><<>><<")

#     # update daily tracking entry
#     # filtered_entry.steps_completed = len(daily_tracking.completedSteps)
#     # filtered_entry.steps_total = daily_tracking.totalSteps
#     # filtered_entry.notes = daily_tracking.notes if hasattr(daily_tracking, 'notes') else None
#     # filtered_entry.completed_steps_ids = [step.id for step in daily_tracking.completedSteps]

#     # update daily steps
#     for step in daily_steps:
#         # step.completed_at = step.habit_step_id in daily_tracking.completedStepsIds
#         # print(step, "step>>><<>><<", step.__dict__.items())
#         if step.habit_step_id in daily_tracking.completedStepsIds:
#             step.completed = True
#         else:
#             step.completed = False
#     # this updates needs to be refined currently it only retrun filtered item leaving rest asa empty in response
#     # try:
#     #     db.commit()
#     #     db.refresh(filtered_entry)
#     # except Exception as e:
#     #     db.rollback()
#     #     print(e, "error>>><<>><<")
#     #     return {"error": "Failed to update daily tracking entry"}

#     # for item in filtered_entry.__dict__.items():
#     #     print(item, "item>>><<>><<")
    
#     return {"message": "Daily tracking entry found", "entry": tracking_entry}


# @daily_tracking_router.put("/habit-timeline/{tracking_id}")
# async def update_daily_tracking(tracking_id: int, daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db)):
#     # tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.id == tracking_id).first()

#     print(daily_tracking, "daily_tracking>><<>><<")

#     tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.habit_id == daily_tracking.habitId and DailyTrackingOfHabit.date_stamp == daily_tracking.dateStamp).all()

#     print(len(tracking_entry), "tracking_entry>>><<>><<")

#     if not len(tracking_entry):
#         return {"error": "Daily tracking entry not found"}
    
#     return {"message": "Daily tracking entry found", "entry": tracking_entry}

#     # Normalize and filter completed step ids. HabitStep.id in the API may be a string;
#     # convert to int where possible and ignore falsy/None ids.
#     step_ids = []
#     for step in (daily_tracking.completedSteps or []):
#         sid = getattr(step, 'id', None)
#         if sid is None:
#             continue
#         try:
#             step_ids.append(int(sid))
#         except (TypeError, ValueError):
#             # ignore ids that cannot be converted to int
#             continue

#     # Update counters and fields
#     tracking_entry.steps_completed = len(step_ids)
#     tracking_entry.steps_total = daily_tracking.totalSteps
#     # store only the date portion (DB column is Date)
#     # tracking_entry.date_stamp = getattr(daily_tracking.dateStamp, 'date', lambda: daily_tracking.dateStamp)()
#     tracking_entry.notes = getattr(daily_tracking, 'notes', None)
#     tracking_entry.completed_steps_ids = step_ids

#     print(tracking_entry, "updated tracking entry>>><<>><<", )

#     # try:
#     #     db.commit()
#     #     db.refresh(tracking_entry)
#     # except Exception:
#     #     db.rollback()
#     #     return {"error": "Failed to update daily tracking entry"}

#     resp =  {
#         "id": tracking_entry.id,
#         "habit_id": tracking_entry.habit_id,
#         "date_stamp": tracking_entry.date_stamp,
#         "steps_completed": tracking_entry.steps_completed,
#         "steps_total": tracking_entry.steps_total,
#         "notes": tracking_entry.notes,
#         "created_at": tracking_entry.created_at,
#         "updated_at": tracking_entry.updated_at,
#         "steps": daily_tracking.steps
#     }

#     return {"message": "Daily tracking entry updated", "entry": resp}

# @daily_tracking_router.put("/habit-timeline/{tracking_id}")
# async def update_daily_tracking(tracking_id: int, daily_tracking: DailyTrackingApiSchema, db: Session = Depends(get_db)):
#     tracking_entry = db.query(DailyTrackingOfHabit).filter(DailyTrackingOfHabit.id == tracking_id).first()
#     if not tracking_entry:
#         return {"error": "Daily tracking entry not found"}

#     # Normalize and filter completed step ids. HabitStep.id in the API may be a string;
#     # convert to int where possible and ignore falsy/None ids.
#     step_ids = []
#     for step in (daily_tracking.completedSteps or []):
#         sid = getattr(step, 'id', None)
#         if sid is None:
#             continue
#         try:
#             step_ids.append(int(sid))
#         except (TypeError, ValueError):
#             # ignore ids that cannot be converted to int
#             continue

#     # Update counters and fields
#     tracking_entry.steps_completed = len(step_ids)
#     tracking_entry.steps_total = daily_tracking.totalSteps
#     # store only the date portion (DB column is Date)
#     # tracking_entry.date_stamp = getattr(daily_tracking.dateStamp, 'date', lambda: daily_tracking.dateStamp)()
#     tracking_entry.notes = getattr(daily_tracking, 'notes', None)
#     tracking_entry.completed_steps_ids = step_ids

#     print(tracking_entry, "updated tracking entry>>><<>><<", )

#     # try:
#     #     db.commit()
#     #     db.refresh(tracking_entry)
#     # except Exception:
#     #     db.rollback()
#     #     return {"error": "Failed to update daily tracking entry"}

#     resp =  {
#         "id": tracking_entry.id,
#         "habit_id": tracking_entry.habit_id,
#         "date_stamp": tracking_entry.date_stamp,
#         "steps_completed": tracking_entry.steps_completed,
#         "steps_total": tracking_entry.steps_total,
#         "notes": tracking_entry.notes,
#         "created_at": tracking_entry.created_at,
#         "updated_at": tracking_entry.updated_at,
#         "steps": daily_tracking.steps
#     }

#     return {"message": "Daily tracking entry updated", "entry": resp}