from app.core.logger import setup_logger

logger = setup_logger(__name__)

logger.info("Logger initialized")
logger.warning("Warning test")
logger.error("Error test")