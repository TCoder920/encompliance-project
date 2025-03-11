import uvicorn
import os
import logging
from app.db.init_db_script import init

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Initialize database if needed
    try:
        init()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 