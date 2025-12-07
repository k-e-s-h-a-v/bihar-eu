import re, os, json
from typing import Dict

def sanitize_filename(s: str) -> str:
    s = s.strip()
    # replace spaces with underscore and remove problematic characters
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^A-Za-z0-9_\-\.]+", "", s)
    return s or "unknown"

def save_json(output_dir: str, redg_no: int, name: str, payload: Dict) -> str:
    safe_name = sanitize_filename(name)
    filename = f"{redg_no}_{safe_name}.json"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload.get("data", {}), fh, ensure_ascii=False, indent=2)
    return path