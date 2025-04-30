import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import csv
import re
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /home/pervaiz/Documents/chatdoctor/backend/chatdoctor/
MODEL_DIR = os.path.join(BASE_DIR, 'trained_model')
DATA_DIR = os.path.join(BASE_DIR, 'chatdata', 'input')

# Initialize globals
clf = None
le = None
cols = None
reduced_data = None
severity_dict = {}
description_dict = {}
precaution_dict = {}
symptoms_dict = {}

def initialize(force=False):
    global clf, le, cols, reduced_data, symptoms_dict
    
    # Only initialize if needed or forced
    if not force and all(v is not None for v in [clf, le, cols, reduced_data]):
        return
        
    try:
        print("\n=== Initializing system ===")
        
        # 1. Load feature columns
        cols_path = os.path.join(MODEL_DIR, 'feature_columns.pkl')
        cols = joblib.load(cols_path)
        print(f"Loaded {len(cols)} feature columns")
        
        # 2. Load model
        model_path = os.path.join(MODEL_DIR, 'model.pkl')
        clf = joblib.load(model_path)
        
        # 3. Load label encoder
        le_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
        le = joblib.load(le_path)
        
        # 4. Load training data
        training_path = os.path.join(DATA_DIR, 'Training.csv')
        training = pd.read_csv(training_path)
        reduced_data = training.groupby(training['prognosis']).max()
        
        # 5. Create symptoms dictionary
        symptoms_dict = {symptom: idx for idx, symptom in enumerate(cols)}
        print(f"Created symptoms dictionary with {len(symptoms_dict)} entries")
        
        print("=== Initialization successful ===")
        
    except Exception as e:
        print(f"\n!!! Initialization failed: {e}")
        raise

def load_severity_dict():
    with open(os.path.join(DATA_DIR, 'Symptom_severity.csv')) as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                severity_dict[row[0]] = int(row[1])
            except:
                pass

def load_description_dict():
    with open(os.path.join(DATA_DIR, 'symptom_Description.csv')) as f:
        reader = csv.reader(f)
        for row in reader:
            description_dict[row[0]] = row[1]

def load_precaution_dict():
    with open(os.path.join(DATA_DIR, 'symptom_precaution.csv')) as f:
        reader = csv.reader(f)
        for row in reader:
            precaution_dict[row[0]] = [row[1], row[2], row[3], row[4]]

def calc_condition(symptoms, days):
    initialize()
    total_severity = sum(severity_dict.get(sym, 0) for sym in symptoms)
    if (total_severity * days) / (len(symptoms) + 1) > 13:
        return "You should consult a doctor."
    return "It might not be serious, but take precautions."

def get_symptom_matches(symptom, chk_dis=None):
    initialize()
    
    try:
        # Use global cols if none provided
        if chk_dis is None:
            chk_dis = cols
            
        # Convert to list if it's a pandas Index
        if hasattr(chk_dis, 'tolist'):
            symptom_list = chk_dis.tolist()
        else:
            symptom_list = list(chk_dis)
            
        # Perform case-insensitive search
        pattern = re.compile(re.escape(symptom), re.IGNORECASE)
        matches = [s for s in symptom_list if pattern.search(str(s))]
        
        return matches if matches else None
        
    except Exception as e:
        print(f"Error in get_symptom_matches: {e}")
        raise


def second_prediction(symptoms):
    initialize()
    input_vector = np.zeros(len(symptoms_dict))
    
    for sym in symptoms:
        if sym in symptoms_dict:
            input_vector[symptoms_dict[sym]] = 1
        else:
            # Handle case where symptom isn't found
            print(f"Symptom '{sym}' not found in dictionary!")
    
    input_df = pd.DataFrame([input_vector], columns=cols)
    
    # Ensure the prediction only happens if there's valid data in input_df
    if input_df.empty:
        raise ValueError("Input data for prediction is empty.")
    
    return le.inverse_transform(clf.predict(input_df))[0]


def get_related_symptoms(disease):
    initialize()
    try:
        # Convert index to list for safe checking
        disease_list = reduced_data.index.tolist()
        if disease in disease_list:
            symptoms_series = reduced_data.loc[disease]
            # Convert to numpy array and find non-zero indices
            symptoms_array = np.atleast_1d(symptoms_series.values)
            nonzero_indices = np.where(symptoms_array == 1)[0]
            return reduced_data.columns[nonzero_indices].tolist()
        return []
    except Exception as e:
        print(f"Error in get_related_symptoms for disease {disease}: {e}")
        return []

def predict_disease(symptom):
    initialize()
    try:
        if symptom not in symptoms_dict:
            print(f"Symptom '{symptom}' not found in symptoms dictionary")
            return None
            
        input_vector = np.zeros(len(cols))
        input_vector[symptoms_dict[symptom]] = 1
        input_df = pd.DataFrame([input_vector], columns=cols)
        return le.inverse_transform(clf.predict(input_df))[0]
    except Exception as e:
        print(f"Error in predict_disease for symptom {symptom}: {e}")
        return None
    


