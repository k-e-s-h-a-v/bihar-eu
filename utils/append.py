import os, csv
from typing import Dict
import threading

def append_csv_row(csv_path: str, row: Dict, lock: threading.Lock, fieldnames: list):
    write_header = not os.path.exists(csv_path)
    with lock:
        with open(csv_path, "a", newline="", encoding="utf-8") as fh:
            # use the hardcoded CSV_FIELDNAMES so column order is stable
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            # ensure all fields are present (missing -> empty string)
            full_row = {k: (row.get(k) if k in row else "") for k in fieldnames}
            writer.writerow(full_row)


def append_not_found(output_dir: str, redg_no: int, lock: threading.Lock):
    """Append a registration number to not_found.txt in a thread-safe way."""
    path = os.path.join(output_dir, "not_found.txt")
    with lock:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{redg_no}\n")