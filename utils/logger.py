import logging
from logging.handlers import RotatingFileHandler
import sys

# Create logger
logger = logging.getLogger("todo_app")
logger.setLevel(logging.INFO)

# File handler (rotates when file reaches 5MB, keeps 3 backups)
file_handler = RotatingFileHandler("app.log", maxBytes=5*1024*1024, backupCount=3)
file_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
)
console_handler.setFormatter(console_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
