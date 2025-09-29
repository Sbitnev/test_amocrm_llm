import os
import sys

import logging
from logging.handlers import RotatingFileHandler

# Создаём каталог logs, если его нет
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

rotating_handler = RotatingFileHandler(
    os.path.join(log_dir, "service.log"),
    encoding="utf-8",
    maxBytes=10 * 1024 * 1024,  # Максимум 10MB на файл
    backupCount=10,  # До 10 резервных копий
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)
console_handler.stream = open(
    sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[rotating_handler, console_handler],
)

logger = logging.getLogger(__name__)
