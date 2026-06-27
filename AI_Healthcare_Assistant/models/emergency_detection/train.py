import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def train_production_model():
    csv_path = "datasets/aleart data/Training.csv"
    model_dir = "models/emergency_detection"
    os.makedirs(model_dir, exist_ok=True)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Kaggle data file missing at: {csv_path}")
        
    print("🔄 Loading Kaggle Dataset...")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()
    
    # Expand target markers to capture more rows from your Kaggle dataset
    critical_indicators = ['chest_pain', 'breathlessness', 'loss_of_balance', 'unsteadiness']
    urgent_indicators = ['high_fever', 'vomiting', 'altered_sensorium', 'headache', 'nausea']
    
    critical_cols = [c for c in critical_indicators if c in df.columns]
    urgent_cols = [c for c in urgent_indicators if c in df.columns]
    
    def determine_row_severity(row):
        if any(row[col] == 1 for col in critical_cols):
            return 3  # CRITICAL
        elif any(row[col] == 1 for col in urgent_cols):
            return 2  # URGENT
        return 1      # ROUTINE

    print("🏷️ Mapping and balancing data severities...")
    y = df.apply(determine_row_severity, axis=1)
    
    # Rebuild input rows matching your application requirements
    X = pd.DataFrame()
    X['chest_pain'] = df['chest_pain'] if 'chest_pain' in df.columns else 0
    X['breathlessness'] = df['breathlessness'] if 'breathlessness' in df.columns else 0
    X['high_fever'] = df['high_fever'] if 'high_fever' in df.columns else 0
    X['loss_of_balance'] = df['loss_of_balance'] if 'loss_of_balance' in df.columns else 0
    X['mild_symptoms'] = y.apply(lambda val: 1 if val == 1 else 0)
    
    # Print out distribution counts to debug potential class skewing issues
    print(f"📊 Class Distribution -> Routine (1): {sum(y==1)}, Urgent (2): {sum(y==2)}, Critical (3): {sum(y==3)}")

    # Split using stratify to ensure emergency classes are equally split
    X_train, X_test, y_train, y_test = train_test_split(
        X.values, y.values, test_size=0.25, stratify=y, random_state=42
    )
    
    print("🤖 Training balanced Random Forest Classifier...")
    # CRITICAL FIX: class_weight="balanced" forces the model to learn rare emergency rows
    model = RandomForestClassifier(n_estimators=150, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)
    
    # Verify performance
    y_pred = model.predict(X_test)
    print(f"\n📈 Fixed Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=['ROUTINE', 'URGENT', 'CRITICAL'], zero_division=0))
    
    # Save the output file
    model_output_path = os.path.join(model_dir, "emergency_model.pkl")
    with open(model_output_path, "wb") as f:
        pickle.dump(model, f)
        
    print(f"🎉 Success! Balanced model compiled and deployed at: {model_output_path}\n")

if __name__ == "__main__":
    train_production_model()