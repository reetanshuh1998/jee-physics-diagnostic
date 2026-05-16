import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
import json

# 1. Generate Synthetic Data
np.random.seed(42)
n_samples = 1000

# Features
time_spent = np.random.randint(10, 300, n_samples) # 10 to 300 seconds
answer_changes = np.random.randint(0, 5, n_samples)
revisits = np.random.randint(0, 4, n_samples)
is_correct = np.random.choice([0, 1], n_samples, p=[0.4, 0.6]) # 60% correct

# Target: Mastery (0 = Needs work, 1 = Good)
# Logic: High time + correct = Good. Low time + correct = Good (or lucky).
# High time + incorrect = Needs work. High changes + incorrect = Needs work.
mastery = []
for i in range(n_samples):
    score = 0
    if is_correct[i] == 1:
        score += 3
    if time_spent[i] > 60 and is_correct[i] == 1:
        score += 2 # Diligent correct
    if answer_changes[i] > 2:
        score -= 1 # Low confidence
    if revisits[i] > 2:
        score -= 1 # Struggling
        
    if score >= 3:
        mastery.append(1)
    else:
        mastery.append(0)

data = pd.DataFrame({
    'time_spent': time_spent,
    'answer_changes': answer_changes,
    'revisits': revisits,
    'is_correct': is_correct,
    'mastery': mastery
})

# 2. Train Model
X = data[['time_spent', 'answer_changes', 'revisits', 'is_correct']]
y = data['mastery']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# 3. Save Model
model.save_model('mastery_model.json')
print("Model saved as mastery_model.json")

# Save some sample data for testing
data.head().to_json('sample_data.json', orient='records')
print("Sample data saved as sample_data.json")
