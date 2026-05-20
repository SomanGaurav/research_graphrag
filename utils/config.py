import os
from pathlib import Path
from dotenv import load_dotenv
from utils.logger import app_logger

load_dotenv()

class Config : 

    def __init__(self):
        
        self.BASE_DIR = Path(__file__).resolve().parent.parent 
        self.LOG_DIR = self.BASE_DIR / "logs" 
        self.OUTPUT_DIR = self.BASE_DIR / "outputs"

        os.makedirs(self.OUTPUT_DIR , exist_ok=True)

        self.NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.GENERATION_MODEL = os.getenv("GENERATION_MODEL", "llama3")
        
        self.SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        self.T_MAX_LOOPS = int(os.getenv("T_MAX_LOOPS", 3))
        self.COMMUNITY_RESOLUTION = float(os.getenv("COMMUNITY_RESOLUTION", 1.0))
        self.TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", 5))

    def validate(self):
        """Runs basic checks to ensure critical configurations are present."""
        if not self.SEMANTIC_SCHOLAR_API_KEY:
            app_logger.warning("SEMANTIC_SCHOLAR_API_KEY is missing. Academic retrieval may fail or be rate-limited.")
        if self.NEO4J_PASSWORD == "password":
            app_logger.warning("Using default Neo4j password. Ensure this is intentional for local dev.")

# Instantiate a global settings object to be imported across the app
settings = Config()
settings.validate()