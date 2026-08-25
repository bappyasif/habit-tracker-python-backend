from pydantic import BaseModel, Field, BeforeValidator
from typing import Literal, Optional, List
from datetime import datetime
from typing import Annotated


class HabitMeasurement(BaseModel):
    metric: str
    target: int


class HabitStep(BaseModel):
    id: Optional[str]
    title: str
    # time: Optional[datetime] = None
    time: Optional[str]
    completed: Optional[bool] = False
    notes: Optional[str] = None


class HabitSuccess(BaseModel):
    enabled: bool = False
    percentage: float = 0.0


class Habit(BaseModel):
    userId: int = 1
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


# Habit update schema for partial updates
class HabitUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    steps: Optional[List[HabitStep]] = None
    measurement: Optional[HabitMeasurement] = None
    frequency: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = None
    notes: Optional[str] = None



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
    habitId: str
    dateStamp: datetime
    # dateStamp: str
    totalSteps: int
    # percentile: float
    completedSteps: list[HabitStep]
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

class UserAuthorizeRequest(BaseModel):
    # email: EmailStr
    email: str = Field(..., example="user@example.com")
    name: str
    image: Optional[str] = None

class FcmUserDeviceToken(BaseModel):
    fcm_token: str
    device_type: str

class UserPushNotificationRequest(BaseModel):
    message_title: str
    message_body: str

# Helper to normalize incoming data ("true", "false", True, False) into an actual Boolean
def parse_flexible_bool(v):
    if isinstance(v, str):
        return v.lower() == "true"
    return bool(v)

FlexibleBool = Annotated[bool, BeforeValidator(parse_flexible_bool)]    

class UserSettingsRequest(BaseModel):
    email_permission: FlexibleBool  # Accepts true, false, "true", or "false"