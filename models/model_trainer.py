import os
import random
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# Ensure models directory exists
os.makedirs("models", exist_ok=True)
os.makedirs("dataset", exist_ok=True)

# 1. Define states, occupations, education levels, and categories for synthetic data
STATES = ["Maharashtra", "Delhi", "Punjab", "Gujarat", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Bihar", "Rajasthan", "West Bengal"]
GENDERS = ["Male", "Female", "Other"]
OCCUPATIONS = ["Farmer", "Student", "Business Owner", "Unemployed", "Private Job", "Government Job", "Retired"]
EDUCATIONS = ["Below 10th", "10th Pass", "12th Pass", "Graduate", "Postgraduate"]
CATEGORIES = ["General", "OBC", "SC", "ST"]
DISABILITY_STATUS = ["Yes", "No"]
BPL_STATUS = ["Yes", "No"]
EMPLOYMENT_STATUS = ["Student", "Farmer", "Business Owner", "Employed", "Unemployed", "Retired"]

# Load original schemes from CSV to execute rules
def load_schemes():
    if os.path.exists("dataset/schemes_sample.csv"):
        return pd.read_csv("dataset/schemes_sample.csv")
    else:
        # Fallback inline scheme data if CSV not present
        return pd.DataFrame([
            {"id": 1, "name": "PM-KISAN", "min_age": 18, "max_age": 120, "gender_target": "All", "min_income": 0, "max_income": 300000, "occupation_target": "Farmer", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 2, "name": "Sukanya Samriddhi Yojana", "min_age": 0, "max_age": 10, "gender_target": "Female", "min_income": 0, "max_income": 10000000, "occupation_target": "No", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 3, "name": "Pradhan Mantri Awas Yojana", "min_age": 18, "max_age": 120, "gender_target": "All", "min_income": 0, "max_income": 1800000, "occupation_target": "All", "disability_required": "No", "bpl_required": "Yes", "state": "All"},
            {"id": 4, "name": "Post Matric Scholarship Scheme", "min_age": 15, "max_age": 30, "gender_target": "All", "min_income": 0, "max_income": 250000, "occupation_target": "Student", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 5, "name": "Pradhan Mantri Suraksha Bima Yojana", "min_age": 18, "max_age": 70, "gender_target": "All", "min_income": 0, "max_income": 10000000, "occupation_target": "All", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 6, "name": "Atal Pension Yojana", "min_age": 18, "max_age": 40, "gender_target": "All", "min_income": 0, "max_income": 10000000, "occupation_target": "All", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 7, "name": "Pradhan Mantri Mudra Yojana", "min_age": 18, "max_age": 65, "gender_target": "All", "min_income": 0, "max_income": 10000000, "occupation_target": "Business Owner", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 8, "name": "Stand-Up India Scheme", "min_age": 18, "max_age": 70, "gender_target": "Female", "min_income": 0, "max_income": 10000000, "occupation_target": "Business Owner", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 9, "name": "Indira Gandhi National Old Age Pension", "min_age": 60, "max_age": 120, "gender_target": "All", "min_income": 0, "max_income": 100000, "occupation_target": "All", "disability_required": "No", "bpl_required": "Yes", "state": "All"},
            {"id": 10, "name": "MGNREGA", "min_age": 18, "max_age": 120, "gender_target": "All", "min_income": 0, "max_income": 200000, "occupation_target": "All", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 11, "name": "Pradhan Mantri Jan Dhan Yojana", "min_age": 10, "max_age": 120, "gender_target": "All", "min_income": 0, "max_income": 10000000, "occupation_target": "All", "disability_required": "No", "bpl_required": "No", "state": "All"},
            {"id": 12, "name": "Sanjay Gandhi Niradhar Grant Scheme", "min_age": 18, "max_age": 65, "gender_target": "All", "min_income": 0, "max_income": 21000, "occupation_target": "All", "disability_required": "Yes", "bpl_required": "Yes", "state": "Maharashtra"}
        ])

# Rule matching function to assign eligibility targets for training data
def evaluate_eligibility(profile, scheme):
    # Age check
    if not (scheme['min_age'] <= profile['age'] <= scheme['max_age']):
        return 0
    # Gender check
    if scheme['gender_target'] != 'All' and profile['gender'] != scheme['gender_target']:
        return 0
    # Income check
    if not (scheme['min_income'] <= profile['income'] <= scheme['max_income']):
        return 0
    # State check
    if scheme['state'] != 'All' and profile['state'] != scheme['state']:
        return 0
    # Disability check
    if scheme['disability_required'] == 'Yes' and profile['disability_status'] != 'Yes':
        return 0
    # BPL check
    if scheme['bpl_required'] == 'Yes' and profile['bpl_status'] != 'Yes':
        return 0
    # Occupation check
    if scheme['occupation_target'] != 'All' and scheme['occupation_target'] != 'No':
        if profile['occupation'] != scheme['occupation_target']:
            return 0
            
    # If all basic filters pass, the user is eligible (label = 1)
    return 1

# Generate synthetic dataset
def generate_synthetic_data(num_samples=1500):
    schemes_df = load_schemes()
    records = []
    
    for i in range(num_samples):
        age = random.randint(5, 85)
        gender = random.choice(GENDERS)
        state = random.choice(STATES)
        occupation = random.choice(OCCUPATIONS)
        
        # Guide income based on occupation to make it realistic
        if occupation == "Student":
            income = random.randint(0, 150000)
            age = random.randint(5, 25)
        elif occupation == "Farmer":
            income = random.randint(20000, 350000)
            age = random.randint(20, 70)
        elif occupation == "Unemployed":
            income = random.randint(0, 100000)
        elif occupation == "Retired":
            income = random.randint(20000, 400000)
            age = random.randint(60, 85)
        else:
            income = random.randint(100000, 1500000)
            
        education = random.choice(EDUCATIONS)
        category = random.choice(CATEGORIES)
        disability_status = random.choice(DISABILITY_STATUS)
        bpl_status = "Yes" if income < 100000 and random.random() > 0.3 else "No"
        employment_status = "Student" if occupation == "Student" else ("Farmer" if occupation == "Farmer" else ("Retired" if occupation == "Retired" else ("Unemployed" if occupation == "Unemployed" else "Employed")))
        family_size = random.randint(1, 8)
        
        profile = {
            "age": age,
            "gender": gender,
            "state": state,
            "occupation": occupation,
            "income": float(income),
            "education": education,
            "category": category,
            "disability_status": disability_status,
            "bpl_status": bpl_status,
            "employment_status": employment_status,
            "family_size": family_size
        }
        
        # Calculate targets
        for idx, scheme in schemes_df.iterrows():
            profile[f"scheme_{scheme['id']}"] = evaluate_eligibility(profile, scheme)
            
        records.append(profile)
        
    df = pd.DataFrame(records)
    # Save the synthetic dataset
    df.to_csv("dataset/synthetic_users.csv", index=False)
    print(f"Generated {num_samples} synthetic user profiles saved to dataset/synthetic_users.csv")
    return df

def train_model():
    df = generate_synthetic_data(1500)
    
    # Identify target columns
    target_cols = [col for col in df.columns if col.startswith("scheme_")]
    feature_cols = [
        "age", "gender", "state", "occupation", "income", "education",
        "category", "disability_status", "bpl_status", "employment_status", "family_size"
    ]
    
    X = df[feature_cols]
    y = df[target_cols]
    
    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Preprocessing pipelines for numerical and categorical features
    numerical_features = ["age", "income", "family_size"]
    categorical_features = ["gender", "state", "occupation", "education", "category", "disability_status", "bpl_status", "employment_status"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    
    # Multi-Output Random Forest Classifier
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf = MultiOutputClassifier(rf)
    
    # Build complete ML pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', clf)
    ])
    
    # Train the pipeline
    print("Training Random Forest pipeline...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate performance
    y_pred = pipeline.predict(X_test)
    
    # Calculate accuracy per scheme
    print("\nModel Evaluation (Accuracy per Scheme):")
    accuracies = []
    for i, scheme_col in enumerate(target_cols):
        acc = accuracy_score(y_test.iloc[:, i], y_pred[:, i])
        accuracies.append(acc)
        print(f"Scheme ID {scheme_col.split('_')[1]}: Accuracy = {acc:.4f}")
        
    print(f"\nAverage Accuracy across all schemes: {np.mean(accuracies):.4f}")
    
    # Save the pipeline using joblib
    model_path = "models/recommendation_model.joblib"
    joblib.dump(pipeline, model_path)
    print(f"Model pipeline successfully saved to {model_path}")

if __name__ == "__main__":
    train_model()
