from graph.db_client import db
from utils.logger import app_logger

def upsert_paper_node(paper_data):
    cypher_query = """
    MERGE (p:Paper {paper_id: $paper_id})
    ON CREATE SET 
        p.title = $title, 
        p.year = $year, 
        p.summary = $summary,
        p.citation_count = $citation_count, // Added this line
        p.layer = $layer  
    ON MATCH SET
        p.layer = $layer, 
        p.summary = $summary,
        p.citation_count = $citation_count // Added this line
    RETURN p
    """
    db.execute_query(cypher_query, parameters=paper_data)
    app_logger.debug(f"Upserted node: {paper_data.get('title')}")

def create_weighted_edge(source_id, target_id, edge_type, weight):
    """
    Constructs E ⊆ V × V. 
    Allows for both structural (CITES) and semantic (SIMILAR_TO) edges,
    applying the weight w to the relationship.
    """
    # Cypher doesn't allow dynamic relationship types directly in parameterized queries,
    # so we validate the type to prevent injection, then format it.
    valid_edges = ["CITES", "SIMILAR_TO"]
    if edge_type not in valid_edges:
        raise ValueError(f"Invalid edge type. Must be one of {valid_edges}")

    cypher_query = f"""
    MATCH (source:Paper {{paper_id: $source_id}})
    MATCH (target:Paper {{paper_id: $target_id}})
    MERGE (source)-[r:{edge_type}]->(target)
    SET r.weight = $weight
    RETURN r
    """
    db.execute_query(cypher_query, parameters={
        "source_id": source_id, 
        "target_id": target_id, 
        "weight": weight
    })
    app_logger.debug(f"Created edge {source_id} -[{edge_type}, w={weight}]-> {target_id}")