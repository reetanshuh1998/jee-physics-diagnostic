from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import engine, get_db
import xgboost as xgb
import pandas as pd
import os

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JEE Physics Diagnostic API")

# Load Model
model_path = os.path.join(os.path.dirname(__file__), "mastery_model.json")
mastery_model = None
if os.path.exists(model_path):
    mastery_model = xgb.XGBClassifier()
    mastery_model.load_model(model_path)
    print("XGBoost model loaded successfully.")
else:
    print(f"Warning: Model file not found at {model_path}")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the JEE Physics Diagnostic API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Questions Endpoints
@app.get("/questions")
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(models.Question).all()
    return questions

@app.post("/questions")
def create_question(question: dict, db: Session = Depends(get_db)):
    db_question = models.Question(**question)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# Users Endpoints
@app.post("/users")
def create_user(user: dict, db: Session = Depends(get_db)):
    db_user = models.User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Test Attempts Endpoints
@app.post("/test-attempts")
def create_test_attempt(attempt: dict, db: Session = Depends(get_db)):
    db_attempt = models.TestAttempt(**attempt)
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

@app.get("/test-attempts/{user_id}")
def get_test_attempts(user_id: str, db: Session = Depends(get_db)):
    attempts = db.query(models.TestAttempt).filter(models.TestAttempt.user_id == user_id).all()
    return attempts

@app.post("/question-attempts")
def create_question_attempt(attempt: dict, db: Session = Depends(get_db)):
    db_attempt = models.QuestionAttempt(**attempt)
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

@app.post("/predict-mastery")
def predict_mastery(data: dict):
    if not mastery_model:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    try:
        # Convert input data to DataFrame
        df = pd.DataFrame([data])
        # Ensure correct column order
        df = df[['time_spent', 'answer_changes', 'revisits', 'is_correct']]
        
        prediction = mastery_model.predict(df)
        probability = mastery_model.predict_proba(df)
        
        return {
            "prediction": int(prediction[0]),
            "probability": float(probability[0][1]),
            "message": "Mastery predicted"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
