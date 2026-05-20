import requests
import numpy as np
from utils.config import settings
from utils.logger import app_logger

class SemanticEmbedder:
    def __init__(self):
        # Notice we are using the /api/embeddings endpoint, not /generate
        self.api_url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
        self.model = settings.EMBEDDING_MODEL

    def get_embedding(self, text: str) -> list[float]:
        """
        Converts text (like an abstract or summary) into a dense vector array.
        """
        if not text or not isinstance(text, str):
            app_logger.warning("Empty or invalid text passed to embedder.")
            return []

        payload = {
            "model": self.model,
            "prompt": text
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            embedding = response.json().get("embedding", [])
            return embedding

        except requests.exceptions.RequestException as e:
            app_logger.error("Failed to generate embedding from local Ollama instance.")
            app_logger.exception(e)
            return []

    def calculate_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        Calculates the cosine similarity (w) between two vectors.
        Returns a float between -1.0 and 1.0 (higher means more similar).
        """
        if not vec1 or not vec2:
            return 0.0
            
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Cosine similarity formula: (A . B) / (||A|| * ||B||)
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        similarity = dot_product / (norm_v1 * norm_v2)
        
        # Round to 3 decimal places for cleaner database storage
        return round(float(similarity), 3)

if __name__ == "__main__":
    # Test the embedding and math logic
    embedder = SemanticEmbedder()
    
    text_a = "Knowledge Graph Embedding uses neural networks to map entities to vectors."
    text_b = "Representation learning in KGs involves embedding nodes into a continuous vector space."
    text_c = "Mechanical thrombectomy is a surgical procedure for stroke patients."
    
    app_logger.info("Generating vectors...")
    vec_a = embedder.get_embedding(text_a)
    vec_b = embedder.get_embedding(text_b)
    vec_c = embedder.get_embedding(text_c)
    
    if vec_a and vec_b and vec_c:
        sim_ab = embedder.calculate_similarity(vec_a, vec_b)
        sim_ac = embedder.calculate_similarity(vec_a, vec_c)
        
        print(f"\nSimilarity (Related texts): {sim_ab}") 
        print(f"Similarity (Unrelated texts): {sim_ac}")