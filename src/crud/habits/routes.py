from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.models.api import Habit as HabitApiSchema
from src.models.db import (
    Habit as HabitModel,
    HabitStep as HabitStepModel,
    HabitMeasurement as HabitMeasurementModel,
    HabitSuccess as HabitSuccessModel,
    HabitFrequency,
)

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
    data = habit.__dict__.copy()

    # Create base ORM Habit with scalar fields
    # Convert frequency string to HabitFrequency enum if provided
    freq_val = data.get("frequency")
    freq_enum = None
    if freq_val is not None:
        try:
            freq_enum = HabitFrequency(freq_val)
        except Exception:
            # fallback: leave as None so DB can raise a clearer error
            freq_enum = None

    db_habit = HabitModel(
        title=data.get("title"),
        description=data.get("description"),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
        duration=data.get("duration"),
        frequency=freq_enum,
    )

    # Convert and attach steps (store serialized dict/string if schema differs)
    for s in data.get("steps", []) or []:
        # HabitStepModel has a single `step` column in the ORM; serialize the incoming step dict
        step_text = str(s)
        db_step = HabitStepModel(step=step_text)
        db_habit.steps.append(db_step)

    # Convert and attach measurement
    measurement = data.get("measurement")
    if measurement:
        db_measure = HabitMeasurementModel(measurement=str(measurement))
        db_habit.measurement.append(db_measure)

    # Convert and attach success definition
    success = data.get("success_definition")
    if success:
        db_success = HabitSuccessModel(success_definition=str(success))
        db_habit.success_definition.append(db_success)

    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


@habits_router.put("/update")
async def update_habit(habit_id: int, habit_data: HabitApiSchema, db: Session = Depends(get_db)):
    habit = db.query(HabitModel).filter(HabitModel.id == habit_id).first()
    if not habit:
        return {"error": "Habit not found"}
    # Update scalar fields only; nested relationships require separate handling
    # update_data = habit_data.dict(exclude_unset=True) // deprecated
    update_data = dict(habit_data, exclude_unset=True)

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