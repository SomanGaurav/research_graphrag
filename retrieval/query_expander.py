import json
import requests
from utils.config import settings
from utils.logger import app_logger

class QueryExpander:
    def __init__(self):
        self.api_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.GENERATION_MODEL

    def expand_query(self, query: str, num_keywords: int = 4) -> list[str]:
        """
        Takes a raw user query 'q' and returns a list of semantic keywords {k_1, ..., k_n}.
        """
        app_logger.info(f"Expanding query: '{query}'")

        # UPDATED PROMPT: Explicitly define the expected JSON key.
        prompt = f"""
        You are an expert academic research assistant.
        The user wants to survey the following topic: "{query}"
        
        Generate exactly {num_keywords} distinct academic search queries (such as Boolean strings or core concepts) 
        that would yield a broad set of relevant papers for a literature review.
        
        CRITICAL INSTRUCTION: Do NOT generate specific paper titles. Generate conceptual search terms.
        Good examples: "Knowledge Graph Embedding methods", "(KGE) AND (link prediction)"
        Bad examples: "A Comparative Study of TransE and TransR in Knowledge Graphs"
        
        OUTPUT FORMAT: 
        You must output ONLY valid JSON containing a single key called "keywords" mapped to a list of strings.
        Example: {{"keywords": ["keyword 1", "keyword 2"]}}
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json" 
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            result_text = response.json().get("response", "{}")
            parsed_json = json.loads(result_text)
            
            # UPDATED PARSING: Handle both a dictionary and a raw list just in case
            if isinstance(parsed_json, dict) and "keywords" in parsed_json:
                keywords = parsed_json["keywords"]
            elif isinstance(parsed_json, list):
                keywords = parsed_json
            else:
                raise ValueError(f"Unexpected JSON structure: {parsed_json}")
                
            app_logger.info(f"Successfully generated keywords: {keywords}")
            return keywords

        except requests.exceptions.RequestException as e:
            app_logger.error("Failed to connect to local Ollama instance.")
            app_logger.exception(e)
            return [query] 
            
        except (json.JSONDecodeError, ValueError) as e:
            app_logger.error(f"Failed to parse LLM output. Raw output: {result_text}")
            app_logger.exception(e)
            return [query]
        

if __name__ == "__main__":
    # Test the expander
    expander = QueryExpander()
    test_query = "I want a survey about Knowledge Graph Embedding"
    keywords = expander.expand_query(test_query)
    print(f"Final Output: {keywords}")