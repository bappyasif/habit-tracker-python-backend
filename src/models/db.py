from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class HabitStep(Base):
    __tablename__ = 'habit_step'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'))
    step = Column(String)
    # add any other fields you need for the HabitStep

    habit = relationship('Habit', back_populates='steps')

class HabitMeasurement(Base):
    __tablename__ = 'habit_measurement'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'))
    measurement = Column(String)
    # add any other fields you need for the HabitMeasurement

    habit = relationship('Habit', back_populates='measurement')

# class HabitSuccess(Base):
#     __tablename__ = 'habit_success'

#     id = Column(Integer, primary_key=True)
#     habit_id = Column(Integer, ForeignKey('habit.id'))
#     success_definition = Column(String)
#     # add any other fields you need for the HabitSuccess

#     habit = relationship('Habit', back_populates='success_definition')

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
    steps = relationship('HabitStep', back_populates='habit')
    measurement = relationship('HabitMeasurement', back_populates='habit')
    # don't expose a `success_definition` relationship on Habit for now
    # success_definition = relationship('HabitSuccess', back_populates='habit')
    # frequency = Column(Enum('daily', 'weekly', 'monthly', 'yearly'), nullable=False)
    # frequency = Column(Enum(HabitFrequency), nullable=False)
    frequency = Column(SQLEnum(HabitFrequency), nullable=False)

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
    # relatationship with HabitTimelinedbModel
    habit_timeline_id = Column(Integer, ForeignKey('habit_timeline.id'))

    # relationship back to HabitTimelineDbModel
    habit_timeline = relationship('HabitTimelineDbModel', back_populates='weeks')

    # I don't need to relate WeekTrackingDbModel with Habit because I've already related HabitTimelineDbModel with Habit and HabitTimelineDbModel with WeekTrackingDbModel. This means that I can already access the habit associated with a week tracking entry through the habit timeline.   

    # habit_id = Column(Integer, ForeignKey('habit.id'))

    # habit = relationship('Habit', back_populates='weeks')

# class HabitTimeline(BaseModel):
#     habitId: int
#     weeks: list[WeekTracking]
class HabitTimelineDbModel(Base):
    __tablename__ = 'habit_timeline'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, unique=True, nullable=False)
    # define a relationship between HabitTimeline and WeekTrackingDbModel
    # this relationship allows us to access the weeks associated with a habit timeline
    # and also allows us to access the habit associated with a week tracking entry
    weeks = relationship('WeekTrackingDbModel', back_populates='habit_timeline')

    # No, I don't need to add anything to Habit to make this newly created relationship work. The relationship between HabitTimelineDbModel and Habit is already defined through the habit_id foreign key in HabitTimelineDbModel. This allows us to access the habit associated with a habit timeline entry through the habit_id foreign key.
    
    # The habit_id column in HabitTimelineDbModel is a foreign key that references the id column in Habit.
    # This means that for any given HabitTimelineDbModel entry, we can access the Habit entry associated with it through the habit_id foreign key.
    # For example, if we have a HabitTimelineDbModel entry with habit_id = 1, we can access the Habit entry with id = 1 through the habit_id foreign key.


    # this relationship is not necessary as we can already access the habit associated with a habit timeline entry through the habit_id foreign key

    # # define a relationship between Habit and HabitTimeline
    # # this relationship allows us to access the habit timeline associated with a habit
    # # and also allows us to access the habit associated with a habit timeline entry
    # habit = relationship('Habit', back_populates='weeks')


