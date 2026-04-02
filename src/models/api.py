from pydantic import BaseModel
from typing import Literal, Optional, List
from datetime import datetime


class HabitMeasurement(BaseModel):
    metric: str
    target: int

class HabitStep(BaseModel):
    id: Optional[str] = None
    title: str
    # time: Optional[datetime] = None
    time: Optional[str] = None
    completed: Optional[bool] = False
    note: Optional[str] = None

class HabitSuccess(BaseModel):
    enabled: bool = False
    percentage: float = 0.0


class Habit(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    # created_at: str
    # updated_at: str
    duration: Optional[int] = None
    steps: List[HabitStep] = []
    measurement: Optional[HabitMeasurement] = None
    # this needs to be on Habit dbd model not so much so for API schema
    # successDefinition: HabitSuccess = HabitSuccess(enabled=False, percentage=0)
    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    # createdAt: Optional[datetime] = None
    # currentStreak: Optional[int] = 0
    # totalCompleted: Optional[int] = 0

# {
#         habitId: number | string,
#         weeks: {
#             weekStart: Date,
#             weekEnd: Date,
#             totalCompleted: number,
#             totalSteps: number,
#             percentile: number, // 0-100 percentage
#         }[]
#     }

class WeekTracking(BaseModel):
    weekStart: datetime
    weekEnd: datetime
    totalCompleted: float
    totalSteps: int
    percentile: float

class HabitTimelineTrackingRequest(BaseModel):
    habitId: int
    week: WeekTracking

class HabitTimelineTrackingResponse(BaseModel):
    habitId: int
    weeks: list[WeekTracking]

class DailyHabitTrackingRequest(BaseModel):
    habitId: int
    dateStamp: datetime
    # totalSteps: int
    # percentile: float
    # completedSteps: list[HabitStep]
    steps: list[HabitStep]
    

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