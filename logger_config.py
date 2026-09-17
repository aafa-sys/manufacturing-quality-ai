import logging
import json
from logging.handlers import RotatingFileHandler
import os


class JSONFormatter(logging.Formatter):
    """Formatter custom: ubah log jadi JSON."""
    def format(self, record):
        log_data = {
            "waktu": self.formatTime(record),
            "level": record.levelname,
            "pesan": record.getMessage(),
            "modul": record.module,
        }
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger():
    """Setup root logger dengan format JSON + rotasi."""
    root_logger = logging.getLogger()
    
    if root_logger.handlers:  # sudah pernah di-setup, skip
        return root_logger
    
    root_logger.setLevel(logging.INFO)
    
    # Handler: file dengan rotasi
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(JSONFormatter())
    
    # Handler: terminal (juga JSON)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger