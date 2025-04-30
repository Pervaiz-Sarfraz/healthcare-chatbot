import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
import csv
import re
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load and preprocess data
training = pd.read_csv('/home/pervaiz/Documents/Datacleaning/Chatbot/chatdata/input/Training.csv')
testing = pd.read_csv('/home/pervaiz/Documents/Datacleaning/Chatbot/chatdata/input/Testing.csv')
cols = training.columns[:-1]
X = training[cols]
y = training['prognosis']

# Encode labels
le = LabelEncoder()
y = le.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

# Train model
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)

# Evaluate model
scores = cross_val_score(clf, X_test, y_test, cv=3)
print(f"Cross-validation scores: {scores}")
print(f"Mean CV score: {scores.mean():.2f}")

# Save model and dependencies
os.makedirs('trained_model', exist_ok=True)
joblib.dump(clf, 'trained_model/model.pkl')
joblib.dump(le, 'trained_model/label_encoder.pkl')
joblib.dump(cols, 'trained_model/feature_columns.pkl')
print("Model saved to 'trained_model/' directory")

# Initialize dictionaries
severity_dict = {}
description_dict = {}
precaution_dict = {}
symptoms_dict = {symptom: idx for idx, symptom in enumerate(cols)}

# Compute reduced data for symptom lookup
reduced_data = training.groupby(training['prognosis']).max()

def load_severity_dict():
    """Load symptom severity from CSV."""
    with open('/home/pervaiz/Documents/Datacleaning/Chatbot/chatdata/input/Symptom_severity.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                severity_dict[row[0]] = int(row[1])
            except:
                pass

def load_description_dict():
    """Load disease descriptions from CSV."""
    with open('/home/pervaiz/Documents/Datacleaning/Chatbot/chatdata/input/symptom_Description.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            description_dict[row[0]] = row[1]

def load_precaution_dict():
    """Load disease precautions from CSV."""
    with open('/home/pervaiz/Documents/Datacleaning/Chatbot/chatdata/input/symptom_precaution.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            precaution_dict[row[0]] = [row[1], row[2], row[3], row[4]]

def validate_data():
    """Validate dataset consistency."""
    missing_desc = set(training['prognosis']) - set(description_dict.keys())
    missing_prec = set(training['prognosis']) - set(precaution_dict.keys())
    if missing_desc:
        print(f"Warning: Missing descriptions for diseases: {missing_desc}")
    if missing_prec:
        print(f"Warning: Missing precautions for diseases: {missing_prec}")

def calc_condition(symptoms, days):
    """Calculate condition severity based on symptoms and duration."""
    total_severity = sum(severity_dict.get(sym, 0) for sym in symptoms)
    if (total_severity * days) / (len(symptoms) + 1) > 13:
        print("You should consult a doctor.")
    else:
        print("It might not be serious, but take precautions.")

def get_valid_symptom(chk_dis):
    """Prompt user for a valid symptom."""
    max_retries = 3
    retries = 0
    while retries < max_retries:
        print("Enter the symptom you are experiencing:")
        symptom = input("-> ").strip()
        matches = [s for s in chk_dis if re.search(re.escape(symptom), s, re.IGNORECASE)]
        if matches:
            print("Related symptoms found:")
            for i, match in enumerate(matches):
                print(f"{i}) {match}")
            idx = int(input(f"Select the one you meant (0-{len(matches)-1}): ")) if len(matches) > 1 else 0
            return matches[idx]
        print("Please enter a valid symptom.")
        retries += 1
    print("Maximum retries reached. Exiting.")
    exit(1)

def get_days():
    """Prompt user for number of days."""
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            return int(input("For how many days have you had this symptom?: "))
        except ValueError:
            print("Please enter a valid number of days.")
            retries += 1
    print("Maximum retries reached. Exiting.")
    exit(1)

def get_yes_no_input(prompt):
    """Prompt user for yes/no input with normalization."""
    max_retries = 3
    retries = 0
    while retries < max_retries:
        inp = input(f"{prompt} (yes/no): ").lower().strip()
        if inp in ['y', 'yes', 'yess']:
            return 'yes'
        if inp in ['n', 'no']:
            return 'no'
        print("Please answer yes/no.")
        retries += 1
    print("Maximum retries reached. Exiting.")
    exit(1)

def second_prediction(symptoms):
    """Predict disease based on symptoms using the trained model."""
    input_vector = np.zeros(len(symptoms_dict))
    for sym in symptoms:
        if sym in symptoms_dict:
            input_vector[symptoms_dict[sym]] = 1
    input_df = pd.DataFrame([input_vector], columns=cols)
    return le.inverse_transform(clf.predict(input_df))[0]

def diagnose():
    """Run the chatbot diagnosis process."""
    print("Please enter your name:")
    name = input("-> ")
    print(f"Hello, {name}")

    # Get initial symptom
    disease_input = get_valid_symptom(cols)
    num_days = get_days()

    # Predict initial disease
    input_vector = np.zeros(len(symptoms_dict))
    input_vector[symptoms_dict[disease_input]] = 1
    input_df = pd.DataFrame([input_vector], columns=cols)
    present_disease = le.inverse_transform(clf.predict(input_df))[0]

    # Get related symptoms
    symptoms_given = []
    if present_disease in reduced_data.index:
        red_cols = reduced_data.columns
        symptoms_series = reduced_data.loc[present_disease]
        symptoms_given = red_cols[np.atleast_1d(symptoms_series.values).nonzero()[0]]
    else:
        print(f"Warning: No symptom data available for {present_disease}. Proceeding with initial symptom.")

    # Ask for additional symptoms
    symptoms_exp = [disease_input]  # Include initial symptom
    if len(symptoms_given) > 0:
        print("Are you experiencing any of these symptoms?")
        for sym in symptoms_given:
            if sym == disease_input:  # Skip the initial symptom
                continue
            inp = get_yes_no_input(sym)
            if inp == 'yes':
                symptoms_exp.append(sym)
    else:
        print("No additional symptoms to check.")

    # Summarize symptoms
    print(f"Symptoms reported: {', '.join(symptoms_exp)}")

    # Second prediction
    second_pred = second_prediction(symptoms_exp)

    # Output results
    calc_condition(symptoms_exp, num_days)
    if present_disease == second_pred:
        print(f"You may have {present_disease}")
        print(description_dict.get(present_disease, "No description available."))
    else:
        print(f"You may have {present_disease} or {second_pred}")
        print(description_dict.get(present_disease, "No description available."))
        print(description_dict.get(second_pred, "No description available."))

    # Precautions
    precautions = precaution_dict.get(present_disease, [])
    print("Take the following measures:")
    for i, prec in enumerate(precautions, 1):
        print(f"{i}) {prec}")

# Load dictionaries and validate data
load_severity_dict()
load_description_dict()
load_precaution_dict()
validate_data()

# Run diagnosis
diagnose()