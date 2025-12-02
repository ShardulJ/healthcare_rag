import json
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
random.seed(42)

CONDITIONS = [
    "Type 2 Diabetes Mellitus", "Hypertension", "Asthma", "COPD",
    "Coronary Artery Disease", "Chronic Kidney Disease", "Osteoarthritis",
    "Depression", "Anxiety Disorder", "Hyperlipidemia"
]

MEDICATIONS = {
    "Type 2 Diabetes Mellitus": ["Metformin 500mg", "Insulin Glargine", "Glipizide 5mg"],
    "Hypertension": ["Lisinopril 10mg", "Amlodipine 5mg", "Hydrochlorothiazide 25mg"],
    "Asthma": ["Albuterol Inhaler", "Fluticasone Inhaler", "Montelukast 10mg"],
    "COPD": ["Tiotropium Inhaler", "Albuterol Inhaler", "Prednisone 10mg"],
    "Coronary Artery Disease": ["Aspirin 81mg", "Atorvastatin 40mg", "Metoprolol 50mg"],
    "Hyperlipidemia": ["Atorvastatin 20mg", "Simvastatin 40mg", "Ezetimibe 10mg"]
}

VISIT_NOTES = [
    "Patient reports good adherence to medication regimen. Blood pressure well controlled.",
    "Patient experiencing mild side effects from current medication. Discussed alternatives.",
    "Follow-up visit for chronic condition management. Vitals stable.",
    "Patient reports improvement in symptoms since last visit. Continue current treatment plan.",
    "Discussed lifestyle modifications including diet and exercise.",
    "Ordered lab work to monitor disease progression and medication effectiveness.",
    "Patient educated on warning signs and when to seek immediate care.",
    "Medication dosage adjusted based on recent lab results and symptom control."
]

def generate_patient_record():
    patient_id = fake.uuid4()[:8]
    
    gender = random.choice(["Male", "Female"])
    age = random.randint(25, 85)
    
    num_conditions = random.randint(1, 3)
    conditions = random.sample(CONDITIONS, num_conditions)
    
    medications = []
    for condition in conditions:
        if condition in MEDICATIONS:
            meds = random.sample(MEDICATIONS[condition], random.randint(1, 2))
            medications.extend(meds)
    
    vitals = {
        "blood_pressure": f"{random.randint(110, 160)}/{random.randint(70, 100)}",
        "heart_rate": random.randint(60, 100),
        "temperature": round(random.uniform(97.0, 99.5), 1),
        "weight_kg": random.randint(50, 120),
        "height_cm": random.randint(150, 190)
    }
    
    num_visits = random.randint(2, 5)
    visits = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(num_visits):
        visit_date = base_date + timedelta(days=random.randint(30, 90) * i)
        visits.append({
            "date": visit_date.strftime("%Y-%m-%d"),
            "type": random.choice(["Follow-up", "Annual Physical", "Acute Care"]),
            "provider": fake.name(),
            "notes": random.choice(VISIT_NOTES),
            "vitals": vitals.copy()
        })
    
    patient = {
        "patient_id": patient_id,
        "demographics": {
            "name": fake.name(),
            "date_of_birth": fake.date_of_birth(minimum_age=age, maximum_age=age).strftime("%Y-%m-%d"),
            "gender": gender,
            "age": age,
            "phone": fake.phone_number(),
            "email": fake.email(),
            "address": fake.address().replace('\n', ', ')
        },
        "medical_history": {
            "conditions": conditions,
            "allergies": random.sample(["Penicillin", "Sulfa drugs", "Latex", "None"], 1),
            "family_history": random.sample(["Heart Disease", "Diabetes", "Cancer", "None"], 2)
        },
        "medications": medications,
        "current_vitals": vitals,
        "visit_history": visits,
        "insurance": {
            "provider": random.choice(["Blue Cross", "Aetna", "UnitedHealthcare", "Medicare"]),
            "policy_number": fake.uuid4()[:12].upper()
        }
    }
    
    return patient

def generate_dataset(num_patients=100):
    patients = [generate_patient_record() for _ in range(num_patients)]
    
    with open('data/patients.json', 'w') as f:
        json.dump(patients, f, indent=2)
    
    print(f"Generated {num_patients} patient records")
    print(f"Saved to data/patients.json")
    
    print("\nSample patient record:")
    print(json.dumps(patients[0], indent=2)[:500] + "...")
    
    return patients

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    generate_dataset(100)