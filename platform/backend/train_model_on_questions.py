import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
from database import SessionLocal
import models
import json

def generate_data():
    db = SessionLocal()
    questions = db.query(models.Question).all()
    db.close()
    
    print(f"Found {len(questions)} questions in database.")
    
    if len(questions) == 0:
        print("No questions found. Aborting.")
        return None
        
    np.random.seed(42)
    data_list = []
    
    # Generate 100 samples per question
    samples_per_question = 100
    
    for q in questions:
        # Assign difficulty based on ID or randomly
        # Let's use ID % 3 for deterministic difficulty in this demo
        difficulty = q.id % 3 # 0=Easy, 1=Medium, 2=Hard
        
        for _ in range(samples_per_question):
            if difficulty == 0: # Easy
                time_spent = np.random.randint(10, 90)
                is_correct = np.random.choice([0, 1], p=[0.2, 0.8])
                answer_changes = np.random.randint(0, 2)
                revisits = np.random.randint(0, 2)
            elif difficulty == 1: # Medium
                time_spent = np.random.randint(40, 180)
                is_correct = np.random.choice([0, 1], p=[0.5, 0.5])
                answer_changes = np.random.randint(0, 4)
                revisits = np.random.randint(0, 3)
            else: # Hard
                time_spent = np.random.randint(90, 300)
                is_correct = np.random.choice([0, 1], p=[0.7, 0.3])
                answer_changes = np.random.randint(0, 6)
                revisits = np.random.randint(0, 5)
                
            # Mastery Logic (Target)
            score = 0
            if is_correct == 1:
                score += 3
            if time_spent > 60 and is_correct == 1:
                score += 2 # Diligent correct
            if answer_changes > 2:
                score -= 1 # Low confidence
            if revisits > 2:
                score -= 1 # Struggling
                
            mastery = 1 if score >= 3 else 0
            
            data_list.append({
                'question_id': q.id,
                'difficulty': difficulty,
                'time_spent': float(time_spent),
                'answer_changes': int(answer_changes),
                'revisits': int(revisits),
                'is_correct': int(is_correct),
                'mastery': mastery
            })
            
    return pd.DataFrame(data_list)

def train():
    data = generate_data()
    if data is None:
        return
        
    print(f"Generated {len(data)} samples.")
    
    # Features
    X = data[['time_spent', 'answer_changes', 'revisits', 'is_correct']]
    y = data['mastery']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train XGBoost
    print("Training XGBoost model...")
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    # Save Model
    model.save_model('mastery_model.json')
    print("Model saved as mastery_model.json")
    
    # Save sample data
    data.head(10).to_json('sample_data.json', orient='records')
    print("Sample data saved as sample_data.json")

if __name__ == "__main__":
    train()
