from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum, DateTime, Date, UniqueConstraint
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class HabitStep(Base):
    __tablename__ = 'habit_step'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'))
    title = Column(String)
    # add any other fields you need for the HabitStep
    time = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    note = Column(String, default=None)

    habit = relationship('Habit', back_populates='steps')

class HabitMeasurement(Base):
    __tablename__ = 'habit_measurement'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'))
    measurement = Column(String)
    # add any other fields you need for the HabitMeasurement

    habit = relationship('Habit', back_populates='measurement')

class HabitSuccess(Base):
    __tablename__ = 'habit_success'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'))
    # keep a single column named `success_definition` that stores a JSON string
    # (client-facing shape: {"enabled": bool, "percentage": int})
    success_definition = Column(String)

    habit = relationship('Habit', back_populates='success_definition')

class HabitFrequency(PyEnum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'

class Habit(Base):
    __tablename__ = 'habit'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    # use callable defaults so the timestamp is evaluated at insert time
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    duration = Column(Integer)
    total_completed = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    
    steps = relationship('HabitStep', back_populates='habit')
    measurement = relationship('HabitMeasurement', back_populates='habit')
    # relationship to a single success definition object
    success_definition = relationship(
        'HabitSuccess', back_populates='habit', uselist=False, cascade='all, delete-orphan'
    )
    # frequency = Column(Enum('daily', 'weekly', 'monthly', 'yearly'), nullable=False)
    # frequency = Column(Enum(HabitFrequency), nullable=False)
    frequency = Column(SQLEnum(HabitFrequency), nullable=False)
    # i want this table to have relationshiop with HabitTimelineDbModel so that i dont have keep track of habit_it from there
    # timeline = relationship('WeekTrackingDbModel', back_populates='habit_timeline')

    # relationship back to HabitTimelineDbModel so that i can access the weeks associated with a habit through the timeline
    # timeline = relationship('HabitTimelineDbModel', back_populates='habit', uselist=False, cascade="all, delete-orphan")
    timeline = relationship('HabitWeeklyTimelineDbModel', back_populates='habit', uselist=False, cascade="all, delete-orphan")

    # daily tracking - keep as a collection (one entry per date for a habit)
    daily_tracking = relationship('DailyTrackingOfHabit', back_populates='habit', cascade="all, delete-orphan")


# class WeekTracking(BaseModel):
#     weekStart: datetime
#     weekEnd: datetime
#     totalCompleted: float
#     totalSteps: int
#     percentile: float
class WeekTrackingDbModel(Base):
    __tablename__ = 'week_tracking'

    id = Column(Integer, primary_key=True)
    week_start = Column(DateTime)
    week_end = Column(DateTime)
    total_completed = Column(Integer)
    total_steps = Column(Integer)
    percentile = Column(Integer)
    # relationship with HabitWeeklyTimelineDbModel
    habit_timeline_id = Column(Integer, ForeignKey('habit_timeline_by_weeks.id'))

    # relationship back to HabitWeeklyTimelineDbModel
    habit_timeline = relationship('HabitWeeklyTimelineDbModel', back_populates='weeks')

    # I don't need to relate WeekTrackingDbModel with Habit because I've already related HabitTimelineDbModel with Habit and HabitTimelineDbModel with WeekTrackingDbModel. This means that I can already access the habit associated with a week tracking entry through the habit timeline.   

    # habit_id = Column(Integer, ForeignKey('habit.id'))

    # habit = relationship('Habit', back_populates='weeks')

# class HabitTimeline(BaseModel):
#     habitId: int
#     weeks: list[WeekTracking]
class HabitWeeklyTimelineDbModel(Base):
    # __tablename__ = 'habit_timeline'
    __tablename__ = 'habit_timeline_by_weeks'

    id = Column(Integer, primary_key=True)
    # habit_id = Column(Integer, unique=True, nullable=False)
    habit_id = Column(Integer, ForeignKey('habit.id'), unique=True, nullable=False)
    # define a relationship between HabitTimeline and WeekTrackingDbModel
    # this relationship allows us to access the weeks associated with a habit timeline
    # and also allows us to access the habit associated with a week tracking entry
    weeks = relationship('WeekTrackingDbModel', back_populates='habit_timeline', cascade="all, delete-orphan")

    # define a relationship between Habit and HabitTimeline
    # this relationship allows us to access the habit timeline associated with a habit
    # and also allows us to access the habit associated with a habit timeline entry
    habit = relationship('Habit', back_populates='timeline')

    # No, I don't need to add anything to Habit to make this newly created relationship work. The relationship between HabitTimelineDbModel and Habit is already defined through the habit_id foreign key in HabitTimelineDbModel. This allows us to access the habit associated with a habit timeline entry through the habit_id foreign key.
    
    # The habit_id column in HabitTimelineDbModel is a foreign key that references the id column in Habit.
    # This means that for any given HabitTimelineDbModel entry, we can access the Habit entry associated with it through the habit_id foreign key.
    # For example, if we have a HabitTimelineDbModel entry with habit_id = 1, we can access the Habit entry with id = 1 through the habit_id foreign key.


    # this relationship is not necessary as we can already access the habit associated with a habit timeline entry through the habit_id foreign key

    # # define a relationship between Habit and HabitTimeline
    # # this relationship allows us to access the habit timeline associated with a habit
    # # and also allows us to access the habit associated with a habit timeline entry
    # habit = relationship('Habit', back_populates='weeks')

# class DailyTrackingStep(Base):
#     __tablename__ = 'daily_tracking_step'

#     id = Column(Integer, primary_key=True)
#     daily_tracking_id = Column(Integer, ForeignKey('daily_tracking_of_habit.id'))


class DailyTrackingOfHabit(Base):
    __tablename__ = 'daily_tracking_of_habit'
    id = Column(Integer, primary_key=True)

    # link to habit (required)
    habit_id = Column(Integer, ForeignKey('habit.id'), nullable=False, index=True)

    # the calendar date this tracking row represents
    date_stamp = Column(Date, nullable=False)

    # relationship to per-day step completion rows
    steps = relationship('DailyTrackingStep', back_populates='daily_tracking', cascade='all, delete-orphan')

    # summary counters (denormalized for quick reads)
    steps_completed = Column(Integer, default=0)
    steps_total = Column(Integer, default=0)

    # audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # free-form notes for the day
    notes = Column(String, default=None)

    __table_args__ = (UniqueConstraint('habit_id', 'date_stamp', name='uq_habit_date'),)

    habit = relationship('Habit', back_populates='daily_tracking')


class DailyTrackingStep(Base):
    __tablename__ = 'daily_tracking_step'
    __table_args__ = (UniqueConstraint('daily_tracking_id', 'habit_step_id', name='uq_dailystep_per_day'),)

    id = Column(Integer, primary_key=True)
    daily_tracking_id = Column(Integer, ForeignKey('daily_tracking_of_habit.id'), nullable=False, index=True)
    habit_step_id = Column(Integer, ForeignKey('habit_step.id'), nullable=True, index=True)

    # whether this step was completed on that date
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # optional note specific to this completion
    note = Column(String, nullable=True)

    daily_tracking = relationship('DailyTrackingOfHabit', back_populates='steps')
    habit_step = relationship('HabitStep')
