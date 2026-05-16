import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import xgboost as xgb
from database import SessionLocal
import models
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

artifact_dir = "/home/reet/.gemini/antigravity/brain/016d093e-3886-4fdb-bfb9-abd7532fab3b/"

def generate_student_data():
    db = SessionLocal()
    questions = db.query(models.Question).all()
    db.close()
    
    if len(questions) < 30:
        print("Not enough questions. Need at least 30.")
        return None
        
    np.random.seed(42)
    data_list = []
    
    n_students = 300
    questions_per_student = 30
    
    for student_id in range(n_students):
        skill = np.random.beta(5, 2)
        selected_questions = np.random.choice(questions, questions_per_student, replace=False)
        
        for idx, q in enumerate(selected_questions):
            difficulty = q.id % 3
            fatigue = idx / questions_per_student
            time_pressure = 1 if idx >= (questions_per_student * 0.9) else 0
            
            p_correct = 0.8 if difficulty == 0 else (0.5 if difficulty == 1 else 0.2)
            p_correct = p_correct * skill * (1 - 0.2 * fatigue)
            p_correct = min(max(p_correct, 0.05), 0.95)
            
            is_correct = np.random.choice([0, 1], p=[1 - p_correct, p_correct])
            
            base_time = 45 if difficulty == 0 else (120 if difficulty == 1 else 200)
            time_spent = base_time * (2 - skill) * (1 + 0.3 * fatigue)
            time_spent = int(np.random.normal(time_spent, time_spent * 0.2))
            time_spent = max(10, time_spent)
            
            base_changes = 0.5 if difficulty == 0 else (1.5 if difficulty == 1 else 2.5)
            answer_changes = int(np.random.poisson(base_changes * (1 + 0.5 * fatigue)))
            
            base_revisits = 0.2 if difficulty == 0 else (1.0 if difficulty == 1 else 1.8)
            revisits = int(np.random.poisson(base_revisits * (1 + 0.5 * fatigue)))
            
            p_review = 0.1 if difficulty == 0 else (0.3 if difficulty == 1 else 0.6)
            p_review = p_review * (2 - skill)
            p_review = min(max(p_review, 0.05), 0.95)
            marked_for_review = np.random.choice([0, 1], p=[1 - p_review, p_review])
            
            score = 0
            if is_correct == 1:
                score += 3
            if time_spent < base_time and is_correct == 1:
                score += 1
            if answer_changes > 2:
                score -= 1
            if revisits > 2:
                score -= 1
            if marked_for_review == 1:
                score -= 0.5
                
            mastery = 1 if score >= 2.5 else 0
            
            data_list.append({
                'student_id': student_id,
                'question_id': q.id,
                'difficulty': difficulty,
                'time_spent': float(time_spent),
                'answer_changes': int(answer_changes),
                'revisits': int(revisits),
                'is_correct': int(is_correct),
                'marked_for_review': int(marked_for_review),
                'time_pressure': int(time_pressure),
                'fatigue': float(fatigue),
                'mastery': mastery
            })
            
    return pd.DataFrame(data_list)

def train_and_plot():
    data = generate_student_data()
    if data is None:
        return
        
    print(f"Generated {len(data)} samples.")
    
    features = ['time_spent', 'answer_changes', 'revisits', 'is_correct', 
                'marked_for_review', 'time_pressure', 'fatigue', 'difficulty']
    
    X = data[features]
    y = data['mastery']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Enable eval_set to track loss
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    
    # Train with evaluation
    model.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=False)
    
    y_pred = model.predict(X_test)
    
    # Metrics
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Accuracy: {acc:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Plots
    # 1. Confusion Matrix
    plt.figure(figsize=(6, 5))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['No Mastery', 'Mastery'], yticklabels=['No Mastery', 'Mastery'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    cm_path = os.path.join(artifact_dir, 'confusion_matrix.png')
    plt.savefig(cm_path)
    plt.close()
    print(f"Saved confusion matrix to {cm_path}")
    
    # 2. Feature Importance
    plt.figure(figsize=(10, 6))
    xgb.plot_importance(model, importance_type='weight', max_num_features=len(features))
    plt.title('Feature Importance')
    feat_path = os.path.join(artifact_dir, 'feature_importance.png')
    plt.savefig(feat_path)
    plt.close()
    print(f"Saved feature importance to {feat_path}")
    
    # 3. Learning Curve (Loss vs Trees)
    results = model.evals_result()
    epochs = len(results['validation_0']['logloss'])
    x_axis = range(0, epochs)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, results['validation_0']['logloss'], label='Train')
    plt.plot(x_axis, results['validation_1']['logloss'], label='Validation')
    plt.legend()
    plt.ylabel('Log Loss')
    plt.xlabel('Number of Trees')
    plt.title('XGBoost Learning Curve')
    lc_path = os.path.join(artifact_dir, 'learning_curve.png')
    plt.savefig(lc_path)
    plt.close()
    print(f"Saved learning curve to {lc_path}")
    
    # Save model
    model.save_model('mastery_model.json')
    print("Model saved as mastery_model.json")
    
    # Save metrics
    metrics = {
        "accuracy": acc,
        "f1_score": f1,
        "classification_report": classification_report(y_test, y_pred, output_dict=True)
    }
    metrics_path = os.path.join(artifact_dir, 'model_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")

if __name__ == "__main__":
    train_and_plot()
