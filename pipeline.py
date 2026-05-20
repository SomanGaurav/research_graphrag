import time
from utils.logger import app_logger
from retrieval.query_expander import QueryExpander
from retrieval.scholar_api import ScholarRetriever
from embeddings.embedder import SemanticEmbedder
from graph.graph_builder import upsert_paper_node, create_weighted_edge
from graph.layer_assignment import assign_graph_layers

class GraphRAGPipeline:
    def __init__(self):
        self.expander = QueryExpander()
        self.retriever = ScholarRetriever()
        self.embedder = SemanticEmbedder()
        
    def run(self, user_query: str, K: int = 10, T: int = 2024):
        """
        Executes Phase 1 & 2 of the SurveyG Methodology.
        """
        app_logger.info("="*30)

        app_logger.info(f"STARTING PIPELINE FOR: '{user_query}'")
        app_logger.info("="*30)


        keywords = self.expander.expand_query(user_query, num_keywords=3)
        if not keywords:
            app_logger.error("Keyword expansion failed. Halting.")
            return


        papers = self.retriever.run_pipeline(keywords, papers_per_keyword=5)
        if not papers:
            app_logger.error("No papers retrieved. Halting.")
            return

        # ---------------------------------------------------------
        # Step 3: Generate Embeddings (In-Memory)
        # ---------------------------------------------------------
        app_logger.info("Generating dense vector embeddings for all papers...")
        for paper in papers:
            paper['embedding'] = self.embedder.get_embedding(paper['abstract'])

        # ---------------------------------------------------------
        # Step 4: Write Nodes to Graph
        # ---------------------------------------------------------
        app_logger.info("Writing paper nodes to Neo4j...")
        for paper in papers:
            upsert_paper_node({
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "year": paper["year"],
                "summary": paper["abstract"], 
                "citation_count": paper["citation_count"],
                "layer": None # Will be populated by the assignment script
            })

        # ---------------------------------------------------------
        # Step 5: Calculate and Write Semantic Edges
        # ---------------------------------------------------------
        app_logger.info("Calculating semantic similarity network...")
        similarity_threshold = 0.65 # Only create an edge if sim > 0.65
        edge_count = 0
        
        # Compare every paper against every other paper
        for i in range(len(papers)):
            for j in range(i + 1, len(papers)):
                vec_a = papers[i].get('embedding')
                vec_b = papers[j].get('embedding')
                
                # Skip if embedding failed for some reason
                if not vec_a or not vec_b:
                    continue
                    
                sim_score = self.embedder.calculate_similarity(vec_a, vec_b)
                
                if sim_score >= similarity_threshold:
                    create_weighted_edge(
                        source_id=papers[i]['paper_id'],
                        target_id=papers[j]['paper_id'],
                        edge_type="SIMILAR_TO",
                        weight=sim_score
                    )
                    edge_count += 1

        app_logger.info(f"Injected {edge_count} weighted 'SIMILAR_TO' edges into the graph.")

        # ---------------------------------------------------------
        # Step 6: Stratify the Graph (Layer Assignment)
        # ---------------------------------------------------------
        app_logger.info("Executing Layer Assignment Function L(v)...")
        assign_graph_layers(K=K, T=T)
        
        app_logger.info("==================================================")
        app_logger.info("PIPELINE COMPLETE. THE GRAPH IS READY FOR CREWAI.")
        app_logger.info("==================================================")

if __name__ == "__main__":
    pipeline = GraphRAGPipeline()
    # Feel free to test with a smaller K value (e.g., 5) since we are pulling a small batch
    pipeline.run("I want a survey about Diffusion Models in Medical Domain", K=5, T=2024)