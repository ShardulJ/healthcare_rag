from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "mixtral-8x7b-32768"
    
    collection_name: str = "patient_records"
    vector_size: int = 384  
    
    top_k: int = 5
    temperature: float = 0.1
    max_tokens: int = 500
    
    patient_data_path: str = "data/patients.json"

config = Config()