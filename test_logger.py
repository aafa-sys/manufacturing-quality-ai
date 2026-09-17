# test_logger.py
from logger_config import setup_logger

setup_logger()
import logging
logger = logging.getLogger(__name__)
logger.info("Ini log INFO")
logger.warning("Ini log WARNING")
logger.error("Ini log ERROR")

print("Selesai. Cek folder logs/")