from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import func
import os

from .database import engine, get_db, Base
from . import models

Base.metadata.create_all(bind=engine)
app = FastAPI(title="FitTrack Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class WorkoutCreate(BaseModel):
    workout_type: str
    exercise: str
    weight: float = 0.0
    reps: int = 0
    sets: int = 0
    duration: int = 0
    time_of_day: str
    calories_burned: int = 0

class FoodCreate(BaseModel):
    meal_type: str
    food_name: str
    calories: int
    protein: float = 0.0

class BeforeAfterCreate(BaseModel):
    starting_weight: float
    current_weight: float
    goal: str

class ScheduleCreate(BaseModel):
    time_of_day: str
    sport: str

class ProgressAdviceRequest(BaseModel):
    starting_weight: float
    current_weight: float
    goal: str = "Muscle Gain"

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_workouts": db.query(models.Workout).count(),
        "total_volume": db.query(func.sum(models.Workout.weight * models.Workout.reps * models.Workout.sets)).scalar() or 0,
        "total_calories": db.query(func.sum(models.FoodLog.calories)).scalar() or 0,
        "db_size": round(os.path.getsize("fittrack.db") / 1024, 2) if os.path.exists("fittrack.db") else 0
    }

@app.post("/workouts")
def add_workout(w: WorkoutCreate, db: Session = Depends(get_db)):
    row = models.Workout(**w.dict()); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id}

@app.get("/workouts")
def list_workouts(db: Session = Depends(get_db)):
    rows = db.query(models.Workout).order_by(models.Workout.created_at.desc()).all()
    return [{"id": r.id, "workout_type": r.workout_type, "exercise": r.exercise, "weight": r.weight, "reps": r.reps, "sets": r.sets, "duration": r.duration, "time_of_day": r.time_of_day, "calories_burned": r.calories_burned} for r in rows]

@app.delete("/workouts/{wid}")
def delete_workout(wid: int, db: Session = Depends(get_db)):
    row = db.query(models.Workout).get(wid)
    if row: db.delete(row); db.commit()
    return {"ok": True}

@app.post("/food")
def add_food(f: FoodCreate, db: Session = Depends(get_db)):
    row = models.FoodLog(**f.dict()); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id}

@app.get("/food")
def list_food(db: Session = Depends(get_db)):
    rows = db.query(models.FoodLog).order_by(models.FoodLog.created_at.desc()).all()
    return [{"id": r.id, "meal_type": r.meal_type, "food_name": r.food_name, "calories": r.calories, "protein": r.protein} for r in rows]

@app.delete("/food/{fid}")
def delete_food(fid: int, db: Session = Depends(get_db)):
    row = db.query(models.FoodLog).get(fid)
    if row: db.delete(row); db.commit()
    return {"ok": True}

@app.post("/beforeafter")
def add_ba(b: BeforeAfterCreate, db: Session = Depends(get_db)):
    row = models.BeforeAfter(**b.dict()); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id}

@app.get("/beforeafter")
def get_ba(db: Session = Depends(get_db)):
    row = db.query(models.BeforeAfter).order_by(models.BeforeAfter.updated_at.desc()).first()
    if not row: return {"starting_weight": 0, "current_weight": 0, "goal": "Not set"}
    return {"starting_weight": row.starting_weight, "current_weight": row.current_weight, "goal": row.goal}

@app.post("/schedule")
def add_schedule(s: ScheduleCreate, db: Session = Depends(get_db)):
    row = models.Schedule(**s.dict()); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id}

@app.get("/schedule")
def list_schedule(db: Session = Depends(get_db)):
    rows = db.query(models.Schedule).all()
    return [{"id": r.id, "time_of_day": r.time_of_day, "sport": r.sport} for r in rows]

@app.delete("/schedule/{sid}")
def delete_schedule(sid: int, db: Session = Depends(get_db)):
    row = db.query(models.Schedule).get(sid)
    if row: db.delete(row); db.commit()
    return {"ok": True}

@app.post("/progress-advice")
def get_progress_advice(req: ProgressAdviceRequest):
    diff = req.current_weight - req.starting_weight
    abs_diff = abs(diff)
    
    if diff > 0: status, color = "Gained", "green"
    elif diff < 0: status, color = "Lost", "red"
    else: status, color = "Maintained", "blue"
        
    advice = {"difference": abs_diff, "status": status, "color": color, "food_advice": "", "water_advice": ""}

    if diff > 0:
        if req.goal == "Muscle Gain":
            advice["food_advice"] = f"You gained {abs_diff}kg. To ensure this is MUSCLE and not fat, you need: **Protein:** 1.6g - 2.2g per kg (chicken, eggs, fish). **Carbs:** Eat complex carbs (rice, oats) to fuel training. **Timing:** Eat protein within 1 hour after your workout."
            advice["water_advice"] = "As an athlete, drink about **125 oz (15 cups)** of fluid daily. Drink **17-20 oz** 2-3 hours before training, and **8 oz** 20-30 mins before."
        else:
            advice["food_advice"] = f"You gained {abs_diff}kg. If your goal was fat loss, focus on lean proteins (turkey, tofu) and reduce simple sugars. Keep protein high (1.2g-1.6g per kg)."
            advice["water_advice"] = "Drink **125 oz** daily. Water helps with metabolism and appetite control."
    elif diff < 0:
        if req.goal == "Fat Loss":
            advice["food_advice"] = f"Great job! You lost {abs_diff}kg. To keep losing fat without losing muscle: **Protein:** 1.2g - 1.4g per kg (lean meats, lentils). **Carbs:** Keep moderate carbs for energy. **Healthy Fats:** Avocado, nuts."
            advice["water_advice"] = "Drink **91 oz (11 cups)** for women or **125 oz (15 cups)** for men daily. Hydration is critical for fat metabolism."
        else:
            advice["food_advice"] = f"You lost {abs_diff}kg. This is dangerous if your goal was muscle gain. You MUST eat **300-500 extra calories** daily. Increase protein to **2g per kg** and add healthy calorie-dense foods."
            advice["water_advice"] = "Dehydration can make you feel weak. Drink **125 oz** daily. Add electrolytes if you sweat heavily."
    else:
        advice["food_advice"] = "Your weight is stable. Adjust your calories based on your current goal."
        advice["water_advice"] = "Maintain your daily hydration goal of at least 91-125 oz depending on your gender."

    return advice