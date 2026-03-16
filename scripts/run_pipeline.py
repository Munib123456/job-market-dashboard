import subprocess
import sys
import os
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def run_step(name, script):
    print(f"\n{'='*40}")
    print(f"STEP: {name}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*40}")
    result = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, script)], capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: {name} failed with return code {result.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    print(f"Pipeline started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    run_step("Collect Jobs", "collect_jobs.py")
    run_step("Extract Skills", "extract_skills.py")
    print(f"\n{'='*40}")
    print("PIPELINE COMPLETE")
    print(f"Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*40}")