import csv
import os
import json
from datetime import datetime
from typing import List, Dict, Any


DEFAULT_PATH = os.path.join("data", "attempts.csv")


def ensure_data_dir(path: str) -> None:
    """Creates the parent folder for the CSV if it doesn't exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def append_attempt(
    path: str,
    name: str,
    score: int,
    total: int,
    percentage: int,
    missed: List[Dict[str, Any]],
    answers: List[Dict[str, Any]]
) -> None:
    """
    Appends a quiz attempt to CSV.

    Missed questions + full answers are stored as JSON strings in the CSV columns.
    This keeps CSV storage while still saving detailed structured information.
    """
    ensure_data_dir(path)
    file_exists = os.path.exists(path)

    row = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "name": name,
        "score": score,
        "total": total,
        "percentage": percentage,
        "missed_questions": json.dumps(missed, ensure_ascii=False),
        "answers": json.dumps(answers, ensure_ascii=False),
    }

    try:
        with open(path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except OSError as e:
        raise OSError(f"Failed to write attempts CSV: {e}") from e


def read_attempts(path: str) -> List[Dict[str, str]]:
    """Reads quiz attempts from CSV; returns empty list if file not found."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, mode="r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except OSError as e:
        raise OSError(f"Failed to read attempts CSV: {e}") from e