import sys
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
