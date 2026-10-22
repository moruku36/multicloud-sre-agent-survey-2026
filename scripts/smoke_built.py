"""Run the built package outside the source checkout with no credentials or network."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


root = Path(__file__).resolve().parents[1]
built = root / "build" / "lib"
if not (built / "sre_agent" / "fixtures" / "three_clouds.json").is_file():
    raise SystemExit("built package lacks synthetic fixtures")

with TemporaryDirectory() as isolated:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(built)
    completed = subprocess.run([sys.executable, "-m", "sre_agent.cli", "demo"],
                               cwd=isolated, env=environment, capture_output=True,
                               text=True, check=True)
    report = json.loads(completed.stdout)
    assert {item["cloud"] for item in report} == {"aws", "azure", "gcp"}
    assert all(item["execution"] == "NOT_RUN" for item in report)
print("built package synthetic demo: OK")
