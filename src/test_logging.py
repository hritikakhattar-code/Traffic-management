import logging
import os

log_dir = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "test.log")

# ✅ Manually set UTF-8 encoding by using FileHandler instead of basicConfig
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")  # ✅ UTF-8 encoding
file_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

logger.info("Test log entry - Logging works!")

print(f"Check if logs are written to: {log_file}")
