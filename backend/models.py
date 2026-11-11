from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class Workout(Base):
    __tablename__ = "workouts"
    id           = Column(Integer, primary_key=True, index=True)
    workout_type = Column(String, nullable=False)  
    exercise     = Column(String, nullable=False)  
    weight       = Column(Float, nullable=True)    
    reps         = Column(Integer, nullable=True)  
    sets         = Column(Integer, nullable=True)  
    duration     = Column(Integer, nullable=True)  
    time_of_day  = Column(String, nullable=False)  
    calories_burned = Column(Integer, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

class FoodLog(Base):
    __tablename__ = "food_logs"
    id         = Column(Integer, primary_key=True, index=True)
    meal_type  = Column(String, nullable=False)    
    food_name  = Column(String, nullable=False)    
    calories   = Column(Integer, nullable=False)   
    protein    = Column(Float, nullable=True)      
    created_at = Column(DateTime, default=datetime.utcnow)

class BeforeAfter(Base):
    __tablename__ = "before_after"
    id             = Column(Integer, primary_key=True, index=True)
    starting_weight = Column(Float, nullable=False)
    current_weight  = Column(Float, nullable=False)
    goal           = Column(String, nullable=False) 
    updated_at     = Column(DateTime, default=datetime.utcnow)

class Schedule(Base):
    __tablename__ = "schedules"
    id          = Column(Integer, primary_key=True, index=True)
    time_of_day = Column(String, nullable=False)  
    sport       = Column(String, nullable=False)  
    created_at  = Column(DateTime, default=datetime.utcnow)