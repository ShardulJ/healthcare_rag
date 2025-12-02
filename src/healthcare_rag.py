import json
import time
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from groq import Groq
from src.config import config


class HealthcareRag:

	def __init__(self,):

		self.embedder = SentenceTransformer(config.embedding_model)

		self.qdrant = QdrantClient(":memory:")

		self.llm_client = Groq(api_key=config.groq_api_key)

		self.qdrant.create_collection(
			collection_name=config.collection_name,
			vectors_config=VectorParams(
				size=config.vector_size,
				distance=Distance.COSINE
			)
		)

		self.patients_loaded = False

	def _patient_to_text(self, patient: Dict) -> str:
		demo = patient["demographics"]
        med = patient["medical_history"]

        text_parts = [
        	f"Patient ID: {patient['patient_id']}",
            f"Name: {demo['name']}",
            f"Age: {demo['age']}, Gender: {demo['gender']}",
            f"Medical Conditions: {', '.join(med['conditions'])}",
            f"Medications: {', '.join(patient['medications'])}",
            f"Allergies: {', '.join(med['allergies'])}",
            f"Current BP: {patient['current_vitals']['blood_pressure']}",
            f"Heart Rate: {patient['current_vitals']['heart_rate']} bpm"
        ]

        if patient['visit_history']:
            recent_visit = patient['visit_history'][-1]
            text_parts.append(f"Recent Visit Note: {recent_visit['notes']}")

        return " | ".join(text_parts)

	def load_patient(self, filepath:str):
		with open(filepath, 'r') as f:
            patients = json.load(f)
		
		points = []
        for idx, patient in enumerate(patients):
            text = self._patient_to_text(patient)
            
            embedding = self.embedder.encode(text).tolist()

            points.append(
            	PointStruct(
            		id=idx,
            		vector=embedding,
            		payload={
            			"patient_id": patient["patient_id"],
            			"text": text,
            			"full_record": patient
            		}
            	)
            )

        self.qdrant.upsert(
            collection_name=config.collection_name,
            points=points
        )

        self.patients_loaded = True
        print(f"Loaded {len(patients)} patient records")

	def search(self,):
		pass

	def generate_answer(self,):
		pass

	def query(self,):
		pass