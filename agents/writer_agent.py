from utils.logger import app_logger

def generate_outline(graph_data):
    app_logger.info("Writing Agent started generating outline.")
    
    # Use DEBUG for heavy payloads that you only want in the file, not the console
    app_logger.debug(f"Input graph data payload: {graph_data}")
    
    try:
        # Agent logic here
        pass
    except Exception as e:
        # Use ERROR or EXCEPTION to automatically capture stack traces
        app_logger.exception("Failed to generate outline.")