from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.models.api import Habit as HabitApiSchema
from src.models.db import (
    Habit as HabitModel,
    HabitStep as HabitStepModel,
    HabitMeasurement as HabitMeasurementModel,
    # HabitSuccess as HabitSuccessModel,
    HabitFrequency,
)
import json
# from datetime import datetime

habits_router = APIRouter(prefix="/habits", tags=["habits"])

@habits_router.get("/health")
async def habits_health_check():
    return {"status": "habits router is healthy"}


@habits_router.get("/all")
async def get_all_habits(db: Session = Depends(get_db)):
    habits = db.query(HabitModel).all()
    return {"habits": habits}

@habits_router.post("/create")
async def create_habit(habit: HabitApiSchema, db: Session = Depends(get_db)):
    # Convert pydantic model to plain dict
    data = habit.dict()

    # frequency is required by the DB enum column
    freq_val = data.get("frequency")
    if not freq_val:
        raise HTTPException(status_code=400, detail="frequency is required")

    try:
        freq_enum = HabitFrequency(freq_val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"invalid frequency: {freq_val}")

    # create ORM Habit with scalar fields only
    db_habit = HabitModel(
        title=data.get("title"),
        description=data.get("description"),
        duration=data.get("duration"),
        frequency=freq_enum,
    )

    # Attach steps as ORM HabitStep instances (incoming steps are Pydantic models/dicts)
    for s in (data.get("steps") or []):
        if hasattr(s, "dict"):
            s_dict = s.dict()
        elif isinstance(s, dict):
            s_dict = s
        else:
            try:
                s_dict = dict(s)
            except Exception:
                s_dict = {"value": str(s)}

        db_step = HabitStepModel(step=json.dumps(s_dict))
        db_habit.steps.append(db_step)

    # Attach measurement (if provided) as ORM HabitMeasurement instance
    measurement = data.get("measurement")
    if measurement:
        if hasattr(measurement, "dict"):
            m_dict = measurement.dict()
        elif isinstance(measurement, dict):
            m_dict = measurement
        else:
            try:
                m_dict = dict(measurement)
            except Exception:
                m_dict = {"value": str(measurement)}

        db_measure = HabitMeasurementModel(measurement=json.dumps(m_dict))
        db_habit.measurement.append(db_measure)

    # persist the habit and its related child rows
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)

    # Build a JSON-serializable representation instead of returning raw ORM objects
    resp = {
        "id": db_habit.id,
        "title": db_habit.title,
        "description": db_habit.description,
        "duration": db_habit.duration,
        "frequency": db_habit.frequency.value if getattr(db_habit, "frequency", None) is not None else None,
        "steps": [],
        "measurement": None,
        "created_at": db_habit.created_at.isoformat() if getattr(db_habit, "created_at", None) else None,
        "updated_at": db_habit.updated_at.isoformat() if getattr(db_habit, "updated_at", None) else None,
    }

    for s in db_habit.steps or []:
        try:
            resp["steps"].append(json.loads(s.step))
        except Exception:
            # fallback: append raw string if JSON parsing fails
            resp["steps"].append(s.step)

    if db_habit.measurement:
        try:
            # assume a single measurement entry if present
            resp["measurement"] = json.loads(db_habit.measurement[0].measurement)
        except Exception:
            resp["measurement"] = db_habit.measurement[0].measurement

    return {"message": "Habit created successfully", "habit": resp}
# async def create_habit(habit: HabitApiSchema, db: Session = Depends(get_db)):
#     # Convert pydantic model to plain dict
#     data = habit.dict()

#     print(data, "user data chexck for save!!", data.get("steps"), data.get("measurement"))

#     # Create base ORM Habit with scalar fields only. Relationships handled below.
#     freq_val = data.get("frequency")
#     freq_enum = None
#     if freq_val is not None:
#         try:
#             freq_enum = HabitFrequency(freq_val)
#         except Exception:
#             freq_enum = None

#     db_habit = HabitModel(
#         title=data.get("title"),
#         description=data.get("description"),
#         duration=data.get("duration"),
#         frequency=freq_enum,
#     )

#     # Attach steps correctly as ORM instances. Incoming steps are Pydantic models/dicts.
#     for s in (data.get("steps") or []):
#         # Normalize to dict
#         if hasattr(s, "dict"):
#             s_dict = s.dict()
#         elif isinstance(s, dict):
#             s_dict = s
#         else:
#             # fallback
#             try:
#                 s_dict = dict(s)
#             except Exception:
#                 s_dict = {"value": str(s)}

#         # serialize the step dict into the single 'step' column on the ORM model
#         db_step = HabitStepModel(step=json.dumps(s_dict))
#         # defensive check: ensure we're appending an ORM-mapped instance
#         try:
#             if not hasattr(db_step, "_sa_instance_state"):
#                 # create a new ORM instance explicitly (fallback)
#                 db_step = HabitStepModel(step=json.dumps(s_dict))
#         except Exception:
#             # if anything goes wrong here, still try to append the ORM instance
#             db_step = HabitStepModel(step=json.dumps(s_dict))

#         db_habit.steps.append(db_step)

#     # Attach measurement if provided
#     measurement = data.get("measurement")
#     if measurement:
#         if hasattr(measurement, "dict"):
#             m_dict = measurement.dict()
#         elif isinstance(measurement, dict):
#             m_dict = measurement
#         else:
#             try:
#                 m_dict = dict(measurement)
#             except Exception:
#                 m_dict = {"value": str(measurement)}

#             db_measure = HabitMeasurementModel(measurement=json.dumps(m_dict))
#             # same defensive check for measurement
#             try:
#                 if not hasattr(db_measure, "_sa_instance_state"):
#                     db_measure = HabitMeasurementModel(measurement=json.dumps(m_dict))
#             except Exception:
#                 db_measure = HabitMeasurementModel(measurement=json.dumps(m_dict))

#             db_habit.measurement.append(db_measure)

#     print(db_habit.measurement, db_habit.steps, db_habit.frequency, db_habit.title, "!!what saving!!")


#     db.add(db_habit)
#     db.commit()
#     db.refresh(db_habit)
#     return {"message": "Habit created successfully", "habit": db_habit}


@habits_router.put("/update")
async def update_habit(habit_id: int, habit_data: HabitApiSchema, db: Session = Depends(get_db)):
    habit = db.query(HabitModel).filter(HabitModel.id == habit_id).first()
    if not habit:
        return {"error": "Habit not found"}
    # Update scalar fields only; nested relationships require separate handling
    # use Pydantic's dict to get only set fields
    update_data = habit_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        if key in {"title", "description", "created_at", "updated_at", "duration"}:
            setattr(habit, key, value)
        elif key == "frequency":
            try:
                setattr(habit, "frequency", HabitFrequency(value))
            except Exception:
                # ignore invalid enum value here; let DB/validation handle it later
                pass
    
    # habit.title = habit_data.title
    # habit.description = habit_data.description
    # habit.duration = habit_data.duration
    # habit.frequency = habit_data.frequency
    # habit.steps = habit_data.steps
    # habit.measurement = habit_data.measurement
    # habit.success_definition = habit_data.success_definition

    db.commit()
    return {"message": "Habit updated successfully"}


@habits_router.delete("/delete")
async def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(HabitModel).filter(HabitModel.id == habit_id).first()
    if not habit:
        return {"error": "Habit not found"}
    
    db.delete(habit)
    db.commit()
    return {"message": "Habit deleted successfully"}