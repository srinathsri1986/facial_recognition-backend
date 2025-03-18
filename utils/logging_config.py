import logging
import os

# ✅ Ensure logs directory exists
LOG_DIR = "backend/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ✅ Define Log File Path
LOG_FILE = os.path.join(LOG_DIR, "api.log")

# ✅ Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # ✅ Save logs to file
        logging.StreamHandler()  # ✅ Print logs to console
    ]
)

logger = logging.getLogger(__name__)
logger.info("✅ Logging configured successfully")
