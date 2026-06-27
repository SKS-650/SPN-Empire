# Disease Prediction Tests
import os
import sys

# Ensure Python can find the backend and service layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.backend.services.disease_service import disease_service

def run_diagnostic_tests():
    print("🧪 Starting Machine Learning Model Unit Tests...\n")
    
    # Test Case 1: Flu Symptoms
    flu_symptoms = ["Fever", "Cough", "Headache", "Fatigue", "Body Ache"]
    print(f"📥 Testing Input: {flu_symptoms}")
    result_1 = disease_service.predict(flu_symptoms)
    print(f"🎯 Predicted Condition: {result_1['condition']}")
    print(f"📊 Confidence: {result_1['confidence'] * 100:.2f}%")
    print(f"⚠️ Severity Level: {result_1['severity']}")
    assert "Influenza" in result_1['condition'] or "Viral" in result_1['condition']
    print("🟢 Test Case 1 Passed!\n" + "-"*40)

    # Test Case 2: Stomach Issues
    stomach_symptoms = ["Nausea", "Vomiting", "Diarrhea"]
    print(f"📥 Testing Input: {stomach_symptoms}")
    result_2 = disease_service.predict(stomach_symptoms)
    print(f"🎯 Predicted Condition: {result_2['condition']}")
    print(f"📊 Confidence: {result_2['confidence'] * 100:.2f}%")
    assert "Gastroenteritis" in result_2['condition'] or "Undetermined" in result_2['condition']
    print("🟢 Test Case 2 Passed!\n")
    
    print("✅ All Machine Learning Local Assertion Checks Passed Successfully!")

if __name__ == "__main__":
    run_diagnostic_tests()