from fastapi import APIRouter, Depends, HTTPException
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
import json
# from datetime import datetime

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
            "steps": [json.loads(step.step) for step in habit.steps],
            "measurement": json.loads(habit.measurement[0].measurement) if habit.measurement else None,
            "successDefinition": json.loads(habit.success_definition.success_definition) if habit.success_definition else None,
            "createdAt": habit.created_at.isoformat(),
            "updatedAt": habit.updated_at.isoformat(),
        }
        modified_habits.append(modified_habit)
        
    return {"habits": modified_habits}
    # return {"habits": habits, "modified_habits": modified_habits}

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

    # Attach success_definition (optional) as HabitSuccess (single object)
    success_def = data.get("success_definition") or data.get("successDefinition")
    if success_def is not None:
        if hasattr(success_def, "dict"):
            sd = success_def.dict()
        elif isinstance(success_def, dict):
            sd = success_def
        else:
            try:
                sd = dict(success_def)
            except Exception:
                sd = {"enabled": False, "percentage": 0}

        # ensure basic types
        sd_clean = {
            "enabled": bool(sd.get("enabled", False)),
            "percentage": int(sd.get("percentage", 0)) if sd.get("percentage") is not None else 0,
        }

        db_success = HabitSuccessModel(success_definition=json.dumps(sd_clean))
        # assign single related object
        db_habit.success_definition = db_success

    # (old single-string success_definition handling removed)

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
        "successDefinition": None,
        "createdAt": db_habit.created_at.isoformat() if getattr(db_habit, "created_at", None) else None,
        "updatedAt": db_habit.updated_at.isoformat() if getattr(db_habit, "updated_at", None) else None,
    }

    # debug: success_definition is handled as a single related object (enabled/percentage)

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

    # include success_definition in response (stored as JSON string)
    sd_obj = getattr(db_habit, "success_definition", None)
    if sd_obj and getattr(sd_obj, "success_definition", None):
        try:
            resp["successDefinition"] = json.loads(sd_obj.success_definition)
        except Exception:
            # fallback: return raw string
            resp["successDefinition"] = sd_obj.success_definition
    else:
        resp["successDefinition"] = {"enabled": False, "percentage": 0}

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


# @habits_router.put("/update")
# async def update_habit(habit_id: int, habit_data: HabitApiSchema, db: Session = Depends(get_db)):
#     habit = db.query(HabitModel).filter(HabitModel.id == habit_id).first()
#     if not habit:
#         return {"error": "Habit not found"}
#     # Update scalar fields only; nested relationships require separate handling
#     # use Pydantic's dict to get only set fields
#     update_data = habit_data.dict(exclude_unset=True)

#     for key, value in update_data.items():
#         if key in {"title", "description", "created_at", "updated_at", "duration"}:
#             setattr(habit, key, value)
#         elif key == "frequency":
#             try:
#                 setattr(habit, "frequency", HabitFrequency(value))
#             except Exception:
#                 # ignore invalid enum value here; let DB/validation handle it later
#                 pass
#         elif key == "success_definition":
#             # value expected to be a dict or pydantic model with enabled and percentage
#             sd = None
#             if value is None:
#                 sd = None
#             elif hasattr(value, "dict"):
#                 sd = value.dict()
#             elif isinstance(value, dict):
#                 sd = value
#             else:
#                 try:
#                     sd = dict(value)
#                 except Exception:
#                     sd = None

#                 if sd is None:
#                     # reset existing to defaults (store JSON string)
#                     if habit.success_definition:
#                         habit.success_definition.success_definition = json.dumps({"enabled": False, "percentage": 0})
#                 else:
#                     sd_clean = {
#                         "enabled": bool(sd.get("enabled", False)),
#                         "percentage": int(sd.get("percentage", 0)) if sd.get("percentage") is not None else 0,
#                     }

#                     if habit.success_definition:
#                         habit.success_definition.success_definition = json.dumps(sd_clean)
#                     else:
#                         habit.success_definition = HabitSuccessModel(success_definition=json.dumps(sd_clean))
    
#     # habit.title = habit_data.title
#     # habit.description = habit_data.description
#     # habit.duration = habit_data.duration
#     # habit.frequency = habit_data.frequency
#     # habit.steps = habit_data.steps
#     # habit.measurement = habit_data.measurement
#     # habit.success_definition = habit_data.success_definition

#     db.commit()
#     return {"message": "Habit updated successfully"}

@habits_router.put("/update")
async def update_habit(habit_data: HabitApiSchema, db: Session = Depends(get_db)):
    habit = db.query(HabitModel).filter(HabitModel.id == habit_data.id).first()
    
    if not habit:
        return {"error": "Habit not found"}
    # Update scalar fields only; nested relationships require separate handling
    # use Pydantic's dict to get only set fields
    update_data = habit_data.dict(exclude_unset=True)

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
            # Clear existing steps and append new ORM HabitStepModel instances
            try:
                habit.steps.clear()
            except Exception:
                # fallback - assign new list if clear not supported
                habit.steps = []

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

                db_step = HabitStepModel(step=json.dumps(s_dict))
                habit.steps.append(db_step)

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

                db_measure = HabitMeasurementModel(measurement=json.dumps(m_dict))
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
                        habit.success_definition = HabitSuccessModel(success_definition=json.dumps(sd_clean))

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


@habits_router.delete("/delete/{habit_id}")
async def delete_habit(habit_id: int, db: Session = Depends(get_db)):

    # print("habit", habit_id)


    habit = db.query(HabitModel).filter(HabitModel.id == habit_id).first()

    # print("habit", habit, habit_id)
    
    if not habit:
        return {"error": "Habit not found"}
    
    db.delete(habit)
    db.commit()
    return {"message": "Habit deleted successfully"}