import requests
import time
from utils.config import settings
from utils.logger import app_logger

class ScholarRetriever:
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.headers = {}
        if settings.SEMANTIC_SCHOLAR_API_KEY:
            self.headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY
            app_logger.info("Semantic Scholar API Key loaded.")
        else:
            app_logger.warning("No Semantic Scholar API key found. Requests will be strictly rate-limited.")

    def fetch_papers(self, query: str, limit: int = 10) -> list[dict]:
        """
        Searches Semantic Scholar for a specific query and returns formatted paper metadata.
        """
        app_logger.info(f"Fetching top {limit} papers for query: '{query}'")
        
        # We request exactly the fields needed for the Neo4j schema and the Trending Score math
        params = {
            "query": query,
            "limit": limit,
            "fields": "paperId,title,year,abstract,citationCount,authors"
        }

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            raw_papers = data.get("data", [])
            
            formatted_papers = []
            for p in raw_papers:
                # Skip papers missing critical data needed for our graph
                if not p.get("year") or not p.get("abstract"):
                    continue
                    
                formatted_papers.append({
                    "paper_id": p.get("paperId"),
                    "title": p.get("title"),
                    "year": p.get("year"),
                    "abstract": p.get("abstract"),
                    "citation_count": p.get("citationCount", 0),
                    # Flatten authors into a single string for easier Neo4j storage initially
                    "authors": ", ".join([a.get("name") for a in p.get("authors", [])])
                })
                
            app_logger.info(f"Successfully retrieved {len(formatted_papers)} valid papers.")
            return formatted_papers

        except requests.exceptions.RequestException as e:
            app_logger.error(f"Semantic Scholar API request failed for query: '{query}'")
            app_logger.exception(e)
            return []

    def run_pipeline(self, keywords: list[str], papers_per_keyword: int = 5) -> list[dict]:
        """
        Takes the {k_1, ..., k_n} list and aggregates the unique papers.
        """
        all_papers = {}
        
        for keyword in keywords:
            papers = self.fetch_papers(keyword, limit=papers_per_keyword)
            for paper in papers:
                # Use a dictionary keyed by paper_id to automatically deduplicate
                all_papers[paper["paper_id"]] = paper
                
            # Respect API rate limits (especially if running without a key)
            time.sleep(1.5)
            
        app_logger.info(f"Pipeline complete. Aggregated {len(all_papers)} unique papers.")
        return list(all_papers.values())

if __name__ == "__main__":
    # Test the retriever with the output from your local LLM
    retriever = ScholarRetriever()
    test_keywords = [
        'Knowledge Graph Embedding methods', 
        '(KGE) AND (knowledge representation)'
    ]
    
    results = retriever.run_pipeline(test_keywords, papers_per_keyword=3)
    
    if results:
        print(f"\nSample Paper Retrieved:\nTitle: {results[0]['title']}\nYear: {results[0]['year']}\nCitations: {results[0]['citation_count']}")
    else:
        print("No papers retrieved.")