from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import xgboost as xgb
import pandas as pd
import os
from supabase import create_client, Client

SUPABASE_URL = "https://druruykbefdlbmbvrglb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRydXJ1eWtiZWZkbGJtYnZyZ2xiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NjI3ODAsImV4cCI6MjA5NDUzODc4MH0.GIMvJQ4_w5G3WjEvaOZGLvX122iT78H1HfaWtsQMqWw"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="JEE Physics Diagnostic API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model
model_path = os.path.join(os.path.dirname(__file__), "mastery_model.json")
mastery_model = None
if os.path.exists(model_path):
    mastery_model = xgb.XGBClassifier()
    mastery_model.load_model(model_path)
    print("XGBoost model loaded successfully.")
else:
    print(f"Warning: Model file not found at {model_path}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the JEE Physics Diagnostic API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Questions Endpoints
@app.get("/questions")
def get_questions():
    try:
        response = supabase.table('questions').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/questions")
def create_question(question: dict):
    try:
        response = supabase.table('questions').insert(question).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Users Endpoints
@app.post("/users")
def create_user(user: dict):
    try:
        response = supabase.table('users').insert(user).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test Attempts Endpoints
@app.post("/test-attempts")
def create_test_attempt(attempt: dict):
    try:
        response = supabase.table('test_attempts').insert(attempt).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-attempts/{user_id}")
def get_test_attempts(user_id: str):
    try:
        response = supabase.table('test_attempts').select('*').eq('user_id', user_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/question-attempts")
def create_question_attempt(attempt: dict):
    try:
        response = supabase.table('question_attempts').insert(attempt).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
