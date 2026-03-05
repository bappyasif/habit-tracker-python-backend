from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

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

class HabitSuccess(Base):
    __tablename__ = 'habit_success'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habit.id'))
    success_definition = Column(String)
    # add any other fields you need for the HabitSuccess

    habit = relationship('Habit', back_populates='success_definition')

class Habit(Base):
    __tablename__ = 'habit'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    duration = Column(Integer)
    steps = relationship('HabitStep', back_populates='habit')
    measurement = relationship('HabitMeasurement', back_populates='habit')
    success_definition = relationship('HabitSuccess', back_populates='habit')
    frequency = Column(Enum('daily', 'weekly', 'monthly', 'yearly'), nullable=False)