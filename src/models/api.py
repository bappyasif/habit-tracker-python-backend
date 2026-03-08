from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class HabitMeasurement(BaseModel):
    metric: str
    target: int

class HabitStep(BaseModel):
    id: str
    title: str
    time: str
    completed: bool

class HabitSuccess(BaseModel):
    enabled: bool
    percentage: float

class Habit(BaseModel):
    id: int
    title: str
    description: str
    created_at: str
    updated_at: str
    duration: int
    steps: list[HabitStep]
    measurement: HabitMeasurement
    successDefinition: HabitSuccess
    frequency: Literal["daily", "weekly", "monthly", "yearly"]

class Week(BaseModel):
    weekStart: datetime
    weekEnd: datetime
    totalCompleted: float
    totalSteps: int
    percentile: float

class HabitCompletion(BaseModel):
    habit_id: int
    weeks: list[Week]

class WeeklySummaryRequest(BaseModel):
    hobbyName: str
    hobbyDescription: str
    hobbyFeedback: str

class SummaryResponse(BaseModel):
    summary: str

class WeeklySummaryResponse(BaseModel):
    response: SummaryResponse


# class WeeklySummaryResponse(BaseModel):
#     response: dict[str, str] = {"summary": ""}

class DailyHabitAiInferenceRequest(BaseModel):
    hobby: str
    description: str
    feedback: str

class InferenceResponseData(BaseModel):
    strengths: list[str]
    areas_for_improvement: list[str]
    actionable_steps: list[str]
    actions_legacy: list[HabitStep]
    examples: list[str]
    actions: list[HabitStep]

class DailyHabitAiInferenceResponse(BaseModel):
    response: InferenceResponseData

# class DailyHabitAiInferenceResponse(BaseModel):
#     response: dict