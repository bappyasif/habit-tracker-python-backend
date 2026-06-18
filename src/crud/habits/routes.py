from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.util.db import get_db
from src.models.api import Habit as HabitApiSchema, HabitUpdate as HabitUpdateSchema
from src.models.db import (
    Habit as HabitModel,
    HabitStep as HabitStepModel,
    HabitMeasurement as HabitMeasurementModel,
    HabitSuccess as HabitSuccessModel,
    HabitFrequency,
)
import json
from datetime import datetime


def _parse_iso_dt(val):
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val)
        except Exception:
            return None
    return val


def _make_habit_step_from_dict(d: dict) -> HabitStepModel:
    return HabitStepModel(
        id=d.get("id"),
        title=d.get("title"),
        time=_parse_iso_dt(d.get("time")),
        completed=bool(d.get("completed", False)),
        notes=d.get("notes"),
    )


def _make_measurement_from_dict(d: dict) -> HabitMeasurementModel:
    return HabitMeasurementModel(measurement=json.dumps(d))


def _make_success_from_dict(d: dict) -> HabitSuccessModel:
    sd_clean = {"enabled": bool(d.get("enabled", False)), "percentage": int(d.get("percentage") or 0)}
    return HabitSuccessModel(success_definition=json.dumps(sd_clean))

habits_router = APIRouter(prefix="/habits", tags=["habits"])

@habits_router.get("/health")
async def habits_health_check():
    return {"status": "habits router is healthy"}


@habits_router.get("/all")
async def get_all_habits(db: Session = Depends(get_db)):
    habits = db.query(HabitModel).all()
    # let serialize HabitModel for frontend as per POST request for each habit model data
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

# lets create a habit tracking updates for a habit that only been done for Tracking Page from frontend, wghere oinly Habit's step, notes, time, title, and datestanmp are updated

@habits_router.delete("/delete/{habit_id}")
async def delete_habit(habit_id: int, db: Session = Depends(get_db)):

    habit = db.query(HabitModel).filter(HabitModel.id == habit_id).first()
    
    if not habit:
        return {"error": "Habit not found"}
    
    db.delete(habit)
    db.commit()
    return {"message": "Habit deleted successfully"}

@habits_router.post("/create")
async def create_habit(habit: HabitApiSchema, db: Session = Depends(get_db)):
    # Convert pydantic model to plain dict
    data = habit.dict()

    print(data, "user data chexck for save!!", data.get("steps"), data.get("measurement"))

    habit_data = HabitModel(
        title=data.get("title"),
        description=data.get("description"),
        duration=data.get("duration")
    )

    # Always convert incoming dict/Pydantic objects into ORM model instances before appending. Use explicit constructors

    # steps/measurement/success_definition are relationship collections or separate tables and must be converted into proper SQLAlchemy ORM instances (with the correct constructor keyword names) before assigning or appending.

    # normalize steps -> create ORM HabitStep instances
    normalized_steps = []
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

        # create ORM instance for step using helper
        normalized_steps.append(_make_habit_step_from_dict(s_dict))
    habit_data.steps = normalized_steps  # replace the collection with ORM instances

    # normalize measurement (single-entry collection in your design)
    m = data.get("measurement")
    if m is not None:
        if hasattr(m, "dict"):
            m_dict = m.dict()
        elif isinstance(m, dict):
            m_dict = m
        else:
            try:
                m_dict = dict(m)
            except Exception:
                m_dict = {"value": str(m)}
        habit_data.measurement = [_make_measurement_from_dict(m_dict)]

    # normalize success definition
    sd = data.get("success_definition") or data.get("successDefinition")
    if sd is not None:
        if hasattr(sd, "dict"):
            sd_dict = sd.dict()
        elif isinstance(sd, dict):
            sd_dict = sd
        else:
            try:
                sd_dict = dict(sd)
            except Exception:
                sd_dict = {"enabled": False, "percentage": 0}
        habit_data.success_definition = _make_success_from_dict(sd_dict)

    # need to map frequency string to enum before saving, freq_val is a simple scalar (string) so we can map it directly to an Enum and assign it to the Habit instanc
    freq_val = data.get("frequency")
    if freq_val is not None:
        try:
            freq_enum = HabitFrequency(freq_val)
            habit_data.frequency = freq_enum
        except Exception:
            freq_enum = None
    

    db.add(habit_data)
    db.commit()
    db.refresh(habit_data)

    return {"message": "Habit created successfully", "habit": habit_data}

@habits_router.put("/update")
async def update_habit(habit_data: HabitUpdateSchema, db: Session = Depends(get_db)):
    habit = db.query(HabitModel).filter(HabitModel.id == habit_data.id).first()
    
    if not habit:
        return {"error": "Habit not found"}
    # Update scalar fields only; nested relationships require separate handling
    # use Pydantic v2's model_dump to get only set fields for partial update
    update_data = habit_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        # never overwrite the id
        if key == "id":
            continue

        # direct scalar fields
        if key in {"title", "description", "created_at", "updated_at", "duration"}:
            setattr(habit, key, value)

        elif key == "frequency":
            # convert to enum safely
            try:
                setattr(habit, "frequency", HabitFrequency(value))
            except Exception:
                # ignore invalid enum values here; validation can handle it upstream
                pass

        elif key == "steps":
            # Expect a list of step objects/dicts; replace existing collection
            try:
                # i want to add addintional steps data instead of clearing it first, so we will just append the new steps to the existing collection instead of clearing it first
                
                for s in (value or []):
                    if hasattr(s, "dict"):
                        s_dict = s.dict()
                    elif isinstance(s, dict):
                        s_dict = s
                    else:
                        try:
                            s_dict = dict(s)
                        except Exception:
                            s_dict = {"value": str(s)}

                    # i need to filter out any steps that have the same id as the incoming step, so we will just check if the step with the same id already exists in the habit.steps collection and if it does we will update it instead of appending a new one, and if it doesn't exist we will append a new one

                    existing_step = next((step for step in habit.steps if step.id == s_dict.get("id")), None)
                    if existing_step:
                        # update existing step
                        for k, v in s_dict.items():
                            setattr(existing_step, k, v)
                    else:
                        # append new step
                        db_step = _make_habit_step_from_dict(s_dict)
                        habit.steps.append(db_step)

            except Exception:
                # fallback - assign new list if clear not supported
                habit.steps = []

        elif key == "measurement":
            # measurement is represented as a (single) related object in the DB
            try:
                habit.measurement.clear()
            except Exception:
                habit.measurement = []

            m = value
            if m is not None:
                if hasattr(m, "dict"):
                    m_dict = m.dict()
                elif isinstance(m, dict):
                    m_dict = m
                else:
                    try:
                        m_dict = dict(m)
                    except Exception:
                        m_dict = {"value": str(m)}

                db_measure = _make_measurement_from_dict(m_dict)
                habit.measurement.append(db_measure)

        elif key in {"success_definition", "successDefinition"}:
            sd_val = value
            if sd_val is None:
                # clear the relation
                try:
                    habit.success_definition = None
                except Exception:
                    pass
            else:
                if hasattr(sd_val, "dict"):
                    sd = sd_val.dict()
                elif isinstance(sd_val, dict):
                    sd = sd_val
                else:
                    try:
                        sd = dict(sd_val)
                    except Exception:
                        sd = None

                if sd is None:
                    # reset to defaults
                    if habit.success_definition:
                        habit.success_definition.success_definition = json.dumps({"enabled": False, "percentage": 0})
                else:
                    sd_clean = {
                        "enabled": bool(sd.get("enabled", False)),
                        "percentage": int(sd.get("percentage", 0)) if sd.get("percentage") is not None else 0,
                    }
                    if habit.success_definition:
                        habit.success_definition.success_definition = json.dumps(sd_clean)
                    else:
                        habit.success_definition = _make_success_from_dict(sd_clean)

        else:
            # fallback: try to set attribute if model has it
            if hasattr(habit, key):
                try:
                    setattr(habit, key, value)
                except Exception:
                    # ignore anything we can't set directly
                    pass

    db.commit()
    # refresh to bring ORM relationships up-to-date if caller needs them
    try:
        db.refresh(habit)
    except Exception:
        pass

    return {"message": "Habit updated successfully"}