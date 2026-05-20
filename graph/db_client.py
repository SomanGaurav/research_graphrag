from neo4j import GraphDatabase
from utils.config import settings
from utils.logger import app_logger

class Neo4jClient : 
    def __init__(self):
        try : 
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            self.driver.verify_connectivity()
            app_logger.info("Successfully connected to Neo4j database.")

        except Exception as e : 
            app_logger.exception("Failed to connect to Neo4j. Check your .env credentials and ensure the database is running.")
    
    def close(self):
        if self.driver:
            self.driver.close()        

    def execute_query(self , query , parameters=None): 
        parameters = parameters or {}
        with self.driver.session() as session : 
            try : 
                result = session.run(query, parameters)
                return [record.data() for record in result]
            except Exception as e:
                app_logger.error(f"Query execution failed: {query}\nParameters: {parameters}")
                app_logger.exception(e)
                raise e


db = Neo4jClient()

