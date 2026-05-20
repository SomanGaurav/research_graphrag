from graph.db_client import db
from utils.logger import app_logger
from datetime import datetime

def assign_graph_layers(K=50, T=2024):
    """
    Executes the L: V -> {Foundation, Development, Frontier} function.
    """
    current_year = datetime.now().year
    app_logger.info(f"Starting layer assignment with K={K}, T={T}, Current Year={current_year}")

    # ---------------------------------------------------------
    # 0. Calculate Trend Score for ALL Papers
    # ---------------------------------------------------------
    score_query = """
    MATCH (p:Paper)
    WHERE p.citation_count IS NOT NULL AND p.year IS NOT NULL
    SET p.trend_score = (p.citation_count * 1.0) / (1 + ($current_year - p.year))
    RETURN count(p) as scored_count
    """
    result_s = db.execute_query(score_query, parameters={"current_year": current_year})
    app_logger.info(f"Calculated trend_score for {result_s[0]['scored_count']} papers.")

    # ---------------------------------------------------------
    # 1. Assign Foundation Layer (V_foundation)
    # ---------------------------------------------------------
    # Now we just order by the score we just saved
    foundation_query = """
    MATCH (p:Paper)
    WHERE p.trend_score IS NOT NULL
    WITH p
    ORDER BY p.trend_score DESC
    LIMIT $K
    SET p.layer = 'Foundation'
    RETURN count(p) as foundation_count
    """
    result_f = db.execute_query(foundation_query, parameters={"K": K})
    app_logger.info(f"Assigned {result_f[0]['foundation_count']} papers to the Foundation layer.")

    # ---------------------------------------------------------
    # 2. Assign Frontier Layer (V_frontier)
    # ---------------------------------------------------------
    frontier_query = """
    MATCH (p:Paper)
    WHERE p.layer IS NULL AND p.year >= $T
    SET p.layer = 'Frontier'
    RETURN count(p) as frontier_count
    """
    result_fr = db.execute_query(frontier_query, parameters={"T": T})
    app_logger.info(f"Assigned {result_fr[0]['frontier_count']} papers to the Frontier layer.")

    # ---------------------------------------------------------
    # 3. Assign Development Layer (V_development)
    # ---------------------------------------------------------
    development_query = """
    MATCH (p:Paper)
    WHERE p.layer IS NULL AND p.year < $T
    SET p.layer = 'Development'
    RETURN count(p) as development_count
    """
    result_d = db.execute_query(development_query, parameters={"T": T})
    app_logger.info(f"Assigned {result_d[0]['development_count']} papers to the Development layer.")
    
    app_logger.info("Layer assignment L(v_i) complete.")

    
if __name__ == "__main__":
    # Test the assignment
    assign_graph_layers(K=50, T=2025)