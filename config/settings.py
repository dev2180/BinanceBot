import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file (if present)
load_dotenv()

# ==============================
# Binance API Configuration
# ==============================

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# True for Testnet, False for Mainnet
USE_TESTNET = os.getenv("TESTNET", "True").lower() == "true"

# Spot Testnet Base URL
SPOT_TESTNET_BASE_URL = "https://testnet.binance.vision/api"

# ==============================
# Logging Configuration
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE_PATH = os.path.join(LOG_DIR, "bot.log")

# Ensure logs folder exists
os.makedirs(LOG_DIR, exist_ok=True)

# ------------------------------
# LOG LEVEL (SAFE DEFAULT)
# ------------------------------
LOG_LEVEL = logging.INFO   # Change to DEBUG only for local debugging

# ------------------------------
# FORMATTER (NO PATHS, NO TRACEBACKS)
# ------------------------------
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# ------------------------------
# FILE HANDLER (ROTATING, SAFE)
# ------------------------------
file_handler = RotatingFileHandler(
    LOG_FILE_PATH,
    maxBytes=2 * 1024 * 1024,   # 2 MB
    backupCount=3,
    encoding="utf-8"
)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)

# ------------------------------
# CONSOLE HANDLER (OPTIONAL, SAFE)
# ------------------------------
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)

# ------------------------------
# ROOT LOGGER SETUP (NO LEAKS)
# ------------------------------
root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)

# IMPORTANT: Remove old handlers to avoid duplicate logs & leaks
while root_logger.handlers:
    root_logger.handlers.pop()

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)


def validate_config():
    """
    Ensures that required API keys are present.
    Call this once at startup.
    """
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        raise ValueError(
            "API keys not found. Please set BINANCE_API_KEY and "
            "BINANCE_API_SECRET in your .env file."
        )
