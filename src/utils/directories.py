from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.absolute()
LOGS_DIR = Path(BASE_DIR, "..", "..", "logs")

LOGS_DIR.mkdir(exist_ok=True)
