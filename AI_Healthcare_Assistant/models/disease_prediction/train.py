import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# 🟢 FIXED: Separate the Directory path from the File path explicitly
DATA_DIR = "datasets/disease_prediction"
CSV_PATH = os.path.join(DATA_DIR, "symptoms_data.csv")

MODEL_DIR = "models/disease_prediction"
MODEL_PATH = os.path.join(MODEL_DIR, "random_forest.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

SYMPTOMS = [
    "Fever", "Cough", "Headache", "Fatigue", "Body Ache", 
    "Nausea", "Vomiting", "Diarrhea", "Shortness of Breath", "Loss of Smell"
]

def generate_mock_dataset():
    """Generates a structured clinical dataset if no CSV is present."""
    # This now safely creates only the directory folder path
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(CSV_PATH):
        print(f"[ℹ️] Dataset already exists at: {CSV_PATH}. Skipping generation.")
        return CSV_PATH

    print("[ℹ️] No symptom dataset found. Generating structured mock medical dataset...")
    np.random.seed(42)
    records = []
    
    conditions = [
        ("Influenza (Flu)", ["Fever", "Cough", "Headache", "Fatigue", "Body Ache"]),
        ("Gastroenteritis", ["Nausea", "Vomiting", "Diarrhea", "Body Ache"]),
        ("Respiratory Infection", ["Cough", "Shortness of Breath", "Fever", "Fatigue"]),
        ("Migraine Profile", ["Headache", "Nausea"])
    ]
    
    for _ in range(100):
        for condition, matching_symptoms in conditions:
            row = {symptom: 0 for symptom in SYMPTOMS}
            for sym in matching_symptoms:
                if np.random.rand() > 0.15: 
                    row[sym] = 1
            for sym in SYMPTOMS:
                if sym not in matching_symptoms and np.random.rand() < 0.10:
                    row[sym] = 1
            row["Disease"] = condition
            records.append(row)
            
    df = pd.DataFrame(records)
    df.to_csv(CSV_PATH, index=False)
    print(f"[🟢] Mock dataset generated at: {CSV_PATH}")
    return CSV_PATH

def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Generate or grab path safely
    csv_path = generate_mock_dataset()
        
    df = pd.read_csv(csv_path)
    
    X = df[SYMPTOMS]
    y = df["Disease"]
    
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print("[🚀] Optimizing Random Forest Ensemble Classifier...")
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"[📊] Model Training Evaluation Complete. Accuracy: {accuracy * 100:.2f}%")
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoder, f)
        
    print(f"[💾] Machine learning binaries successfully serialized to '{MODEL_DIR}/'")

if __name__ == "__main__":
    train_model()