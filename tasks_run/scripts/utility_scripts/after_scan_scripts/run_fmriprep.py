import subprocess
import os

# Prompt user if not already set
CHID = os.environ.get("CHID") or input("Enter your CHID: ").strip()
E3_USER = CHID
E3_HOST = "e3-login.tch.harvard.edu"

# Remote path to the batch script on e3
REMOTE_SCRIPT = "/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB/fmriprep_pipeline_adapted/run_fmriprep_batch.sh"

print("Connecting to e3...")

try:
    subprocess.run([
        "ssh", "-t", "-o", "StrictHostKeyChecking=no",
        f"{E3_USER}@{E3_HOST}",
        f"bash {REMOTE_SCRIPT}"
    ], check=True)
    print("fMRIPrep pipeline executed successfully.")

except subprocess.CalledProcessError as e:
    print("Error during fMRIPrep pipeline execution.")
    print(e)
