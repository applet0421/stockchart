import hashlib
from pathlib import Path


def latest_rows(rows, date=None):
    rows = list(rows)
    if not rows:
        return []
    latest_date = date or max(row["date"] for row in rows)
    return [row for row in rows if row["date"] == latest_date]


def build_run_manifest(metadata, files):
    result = dict(metadata)
    result["files"] = []
    for file_path in files:
        path = Path(file_path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        result["files"].append({"path": path.name, "bytes": path.stat().st_size, "sha256": digest})
    return result
