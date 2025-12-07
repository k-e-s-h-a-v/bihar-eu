#!/usr/bin/env python3
"""
Fetch multiple student results in parallel from the BEU endpoint and save payloads as JSON
and a summary CSV.

Usage examples:
  python3 fetch_results.py --start 23105108001 --end 23105108060 --concurrency 10

By default JSON files are saved to ./results_json and CSV to ./results_json/results.csv
"""
import argparse
import csv
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

import requests

from constants.url import BASE_URL, HEADERS
from constants.third_sem_cse_subjects import CSV_FIELDNAMES, THEORY_SUBJECTS, PRACTICAL_SUBJECTS

from utils.save_json import save_json
from utils.append import append_csv_row, append_not_found

DEFAULT_OUTPUT_DIR = "results_json"

# Extend CSV_FIELDNAMES with subject-specific columns (ESE and IA for theory and practical)
for subj in THEORY_SUBJECTS:
    CSV_FIELDNAMES.append(f"{subj} THEORY ESE")
    CSV_FIELDNAMES.append(f"{subj} THEORY IA")

for subj in PRACTICAL_SUBJECTS:
    CSV_FIELDNAMES.append(f"{subj} PRACTICAL ESE")
    CSV_FIELDNAMES.append(f"{subj} PRACTICAL IA")


def fetch_result(session: requests.Session, redg_no: int, year: int = 2024, semester: str = "III", exam_held: str = "July/2025", timeout: int = 10) -> Optional[Dict]:
    """Fetch a single result. Returns parsed JSON (dict) on success, otherwise None."""
    params = {
        "year": year,
        "redg_no": str(redg_no),
        "semester": semester,
        "exam_held": exam_held,
    }

    tries = 3
    for attempt in range(1, tries + 1):
        try:
            resp = session.get(BASE_URL, params=params, headers=HEADERS, timeout=timeout)
            # Some error responses may still be JSON
            try:
                payload = resp.json()
            except ValueError:
                payload = None

            if resp.status_code == 200 and isinstance(payload, dict):
                return payload
            # If rate-limited or server error, retry
            if resp.status_code >= 500 or resp.status_code == 429:
                continue
            # For 4xx, no point retrying except transient 408/429
            return payload
        except requests.RequestException:
            if attempt == tries:
                return None
    return None


def process_redg(session: requests.Session, redg_no: int, output_dir: str, csv_path: str, lock: threading.Lock) -> Optional[int]:
    payload = fetch_result(session, redg_no)
    if not payload:
        # network/error or unparsable response -> record as not found for later inspection
        append_not_found(output_dir, redg_no, lock)
        print(f"{redg_no}: no response or failed to parse JSON (recorded in not_found.txt)")
        return None

    status = payload.get("status")
    data = payload.get("data")
    if status != 200 or not data:
        # result not found or server returned a non-200 status -> don't save JSON; record the reg no
        append_not_found(output_dir, redg_no, lock)
        print(f"{redg_no}: result not found or non-200 status (recorded in not_found.txt)")
        return None

    name = data.get("name") or "unknown"
    saved_path = save_json(output_dir, redg_no, name, payload)

    # Build CSV row with a set of useful fields
    row = {
        "redg_no": redg_no,
        "name": name,
        "father_name": data.get("father_name"),
        "mother_name": data.get("mother_name"),
        "examYear": data.get("examYear"),
        "semester": data.get("semester"),
        "exam_held": data.get("exam_held"),
        "cgpa": data.get("cgpa"),
        "sgpa": ",".join([s for s in (data.get("sgpa") or []) if s]) if data.get("sgpa") else None,
        "fail_any": data.get("fail_any"),
    }

    # Fill theory subject columns (ESE and IA) based on the hardcoded THEORY_SUBJECTS list
    data_theory = data.get("theorySubjects") or []
    theory_lookup = {t.get("name"): t for t in data_theory if t.get("name")}
    for subj in THEORY_SUBJECTS:
        entry = theory_lookup.get(subj)
        row[f"{subj} THEORY ESE"] = entry.get("ese") if entry else ""
        row[f"{subj} THEORY IA"] = entry.get("ia") if entry else ""

    # Fill practical subject columns (ESE and IA)
    data_practical = data.get("practicalSubjects") or []
    practical_lookup = {p.get("name"): p for p in data_practical if p.get("name")}
    for subj in PRACTICAL_SUBJECTS:
        entry = practical_lookup.get(subj)
        row[f"{subj} PRACTICAL ESE"] = entry.get("ese") if entry else ""
        row[f"{subj} PRACTICAL IA"] = entry.get("ia") if entry else ""

    append_csv_row(csv_path, row, lock, CSV_FIELDNAMES)
    print(f"{redg_no}: saved JSON -> {saved_path}")
    return redg_no


def main():
    parser = argparse.ArgumentParser(description="Fetch BEU results in parallel and save JSON + CSV summary")
    parser.add_argument("--start", type=int, required=True, help="starting redg_no (inclusive)")
    parser.add_argument("--end", type=int, required=True, help="ending redg_no (inclusive)")
    parser.add_argument("--concurrency", type=int, default=10, help="number of worker threads")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR, help="directory to save JSON and CSV")
    parser.add_argument("--csv", type=str, default="results.csv", help="CSV filename inside output-dir")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    csv_path = os.path.join(args.output_dir, args.csv)

    lock = threading.Lock()

    # Use a single Session for connection pooling
    session = requests.Session()

    # Iterate through redg numbers and fetch in parallel
    redg_numbers = list(range(args.start, args.end + 1))

    with ThreadPoolExecutor(max_workers=args.concurrency) as exc:
        futures = {exc.submit(process_redg, session, r, args.output_dir, csv_path, lock): r for r in redg_numbers}
        completed = 0
        for fut in as_completed(futures):
            r = futures[fut]
            try:
                result = fut.result()
                if result:
                    completed += 1
            except Exception as e:
                print(f"{r}: exception: {e}")

    print(f"Done. {completed}/{len(redg_numbers)} results saved (payloads saved to {args.output_dir}, CSV {csv_path})")


if __name__ == "__main__":
    main()
