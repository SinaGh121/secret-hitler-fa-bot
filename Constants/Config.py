"""
Central configuration module.
Reads BOT_TOKEN, ADMIN_ID, STATS_PATH from environment variables
or from a .env file at project root.
"""

from pathlib import Path
import json
import os
from dotenv import load_dotenv

# load .env beside README / requirements.txt
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

TOKEN: str = os.getenv("BOT_TOKEN", "")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment or .env")

ADMIN: int = int(os.getenv("ADMIN_ID", "0"))
_stats_path = Path(os.getenv("STATS_PATH", "stats.json"))
if not _stats_path.is_absolute():
    _stats_path = project_root / _stats_path
STATS: str = str(_stats_path)

def _new_stats():
    return {
        "libwin_policies": 0,
        "libwin_kill": 0,
        "fascwin_policies": 0,
        "fascwin_blue": 0,
        "cancelled": 0,
        "groups": [],
    }

def load_stats():
    path = Path(STATS)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(_new_stats(), ensure_ascii=False), encoding="utf-8")
    stats = json.loads(path.read_text(encoding="utf-8"))
    defaults = _new_stats()
    for key, value in defaults.items():
        if key not in stats:
            stats[key] = value if not isinstance(value, list) else []
    return stats

def save_stats(stats):
    path = Path(STATS)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats, ensure_ascii=False), encoding="utf-8")

__all__ = ["TOKEN", "ADMIN", "STATS", "load_stats", "save_stats"]
