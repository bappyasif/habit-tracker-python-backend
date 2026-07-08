from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum, DateTime, Date, UniqueConstraint, JSON
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class HabitStep(Base):
    __tablename__ = 'habit_step'

    id = Column(String, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'))
    title = Column(String)
    # add any other fields you need for the HabitStep
    time = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    notes = Column(String, default=None)

    # add datestamp to determine which steps for which date its been tracked for
    datestamp = Column(Date, default=datetime.utcnow)

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
    
    # cascade so that deleting a Habit will also remove related child rows
    # at the ORM level (and avoids FK constraint errors). For DB-level
    # cascade also consider adding `ondelete='CASCADE'` to the ForeignKey
    # definitions and running a migration.
    steps = relationship('HabitStep', back_populates='habit', cascade='all, delete-orphan')
    measurement = relationship('HabitMeasurement', back_populates='habit', cascade='all, delete-orphan')
    # relationship to a single success definition object
    success_definition = relationship(
        'HabitSuccess', back_populates='habit', uselist=False, cascade='all, delete-orphan'
    )
    frequency = Column(SQLEnum(HabitFrequency), nullable=False)
    # i want this table to have relationshiop with HabitTimelineDbModel so that i dont have keep track of habit_it from there

    # relationship back to HabitTimelineDbModel so that i can access the weeks associated with a habit through the timeline
    timeline = relationship('HabitWeeklyTimelineDbModel', back_populates='habit', uselist=False, cascade="all, delete-orphan")

    # daily tracking - keep as a collection (one entry per date for a habit)
    daily_tracking = relationship('DailyTrackingOfHabit', back_populates='habit', cascade="all, delete-orphan")

    # relationship to User
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    # user_id = Column(Integer, ForeignKey('authorized_user.id'), nullable=False)

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

class HabitWeeklyTimelineDbModel(Base):
    __tablename__ = 'habit_timeline_by_weeks'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'), unique=True, nullable=False)
    # define a relationship between HabitTimeline and WeekTrackingDbModel
    # this relationship allows us to access the weeks associated with a habit timeline
    # and also allows us to access the habit associated with a week tracking entry
    weeks = relationship('WeekTrackingDbModel', back_populates='habit_timeline', cascade="all, delete-orphan")

    # define a relationship between Habit and HabitTimeline
    # this relationship allows us to access the habit timeline associated with a habit
    # and also allows us to access the habit associated with a habit timeline entry
    habit = relationship('Habit', back_populates='timeline')

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

    # store completed ids and notes specefic to each of those ids
    steps_completed_with_notes = Column(JSON, default=dict)

    # audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('habit_id', 'date_stamp', name='uq_habit_date'),)

    habit = relationship('Habit', back_populates='daily_tracking')


class DailyTrackingStep(Base):
    __tablename__ = 'daily_tracking_step'
    __table_args__ = (UniqueConstraint('daily_tracking_id', 'habit_step_id', name='uq_dailystep_per_day'),)

    id = Column(Integer, primary_key=True)
    daily_tracking_id = Column(Integer, ForeignKey('daily_tracking_of_habit.id'), nullable=False, index=True)
    habit_step_id = Column(String, ForeignKey('habit_step.id'), nullable=True, index=True)

    # whether this step was completed on that date
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # optional note specific to this completion
    notes = Column(String, nullable=True)

    daily_tracking = relationship('DailyTrackingOfHabit', back_populates='steps')
    habit_step = relationship('HabitStep')

# i want to keep track of authenticated users and their habits, so i will create a new table for that
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    image = Column(String, nullable=False)
    # password_hash = Column(String, nullable=False)

    # relationship to habits
    habits = relationship('Habit', backref='user', cascade='all, delete-orphan')