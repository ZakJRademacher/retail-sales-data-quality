"""Publish complete result versions; readers resolve one pointer per operation."""
import argparse
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def current_output(output):
    output = Path(output).resolve()
    pointer = output / "latest.json"
    if not pointer.exists():
        return output  # Checked-in historical reference files.
    info = json.loads(pointer.read_text(encoding="utf-8"))
    name = info.get("snapshot", "")
    if info.get("contract_version") != 1 or not isinstance(name, str) or not re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{12}", name):
        raise ValueError("Invalid results pointer")
    snapshot = output / "snapshots" / name
    if not snapshot.is_dir():
        raise ValueError("Published results snapshot is missing")
    return snapshot


def publish(output, builder):
    """Keep prior results current until all outputs exist and checks succeed."""
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    lock = output / ".refresh.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError("Another refresh owns .refresh.lock; inspect it before retrying") from exc
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:12]
    stage = output / (".staging_" + run_id)
    pending = output / ("latest_" + uuid.uuid4().hex + ".tmp")
    try:
        os.close(fd)
        stage.mkdir()
        result = builder(stage)
        if not (stage / "analysis.json").is_file() or not all(result["checks"].values()):
            raise ValueError("Incomplete or invalid result version")
        snapshots = output / "snapshots"
        snapshots.mkdir(exist_ok=True)
        stage.rename(snapshots / run_id)
        pending.write_text(json.dumps({"contract_version": 1, "snapshot": run_id}, indent=2) + "\n", encoding="utf-8")
        os.replace(pending, output / "latest.json")
        return result
    finally:
        # Failed runs remain inspectable in .staging_* or as unpublished snapshots.
        # They cannot become current without a successful pointer replacement.
        if pending.exists():
            pending.unlink()
        lock.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "results")
    print(current_output(parser.parse_args().output))
