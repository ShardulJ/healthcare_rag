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

	def search(self, query: str) -> Tuple[List[Dict], float]:

		start_time = time.time()

		query_embedding = self.embedder.encode(query).tolist()

		results = self.qdrant.search(
			collection_name=config.collection_name,
			query_vector=query_embedding,
			limit=config.top_k
		)

		latency = (time.time() - start_time) * 1000

		return results, latency

	def generate_answer(self,query: str, context_results: List) -> Tuple[str, float]:
		start_time = time.time()

		context_parts = []
		for result in context_results:
			patient = result.payload["full_record"]
			context_parts.append(
				f"Patient {patient['patient_id']}: "
				f"{result.payload['text']}"
			)

		context = "\n\n".join(context_parts)

		prompt = f""" You are a healthcare assistant analyzing patient records. Answer the question based ONLY on the provided patient data. Be concise and clinical.
			Patient Records:
			{context}

			Question: {query}

			Answer (be specific and cite patient IDs when relevant):
		"""

		response = self.llm_client.chat.completions.create(
            model=config.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        answer = response.choices[0].message.content

        latency = (time.time() - start_time) * 1000

		return answer, latency

	def query(self,):
		pass