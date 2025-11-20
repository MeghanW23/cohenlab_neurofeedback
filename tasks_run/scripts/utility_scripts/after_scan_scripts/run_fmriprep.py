#!/usr/bin/env python

import os
import sys
import subprocess
from pathlib import Path
sys.path.append("/workdir/tasks_run/scripts")
import settings

E3_HOST = settings.E3_HOSTNAME

REMOTE_SCRIPT = (
    "/lab-share/Neuro-Cohen-e2/Groups/IRB-P00049401/"
    "nfb_fmriprep/fmriprep_pipeline_adapted/run_fmriprep_sbatch.sh")

def get_chid() -> str:
    chid = os.environ.get("CHID")
    if not chid:
        raise RuntimeError(
            "CHID environment variable is not set inside the container.\n"
            "The wrapper script should pass '-e CHID=\"$CHID\"' to docker run."
        )
    return chid.strip()


def main() -> None:
    chid = get_chid()
    e3_user = chid
    print(f"Connecting to {E3_HOST} as {e3_user}...")

    ssh_cmd = [
        "ssh",
        "-t",
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",  # fail fast if key auth doesn't work (no password prompt)
        f"{e3_user}@{E3_HOST}",
        f"bash {REMOTE_SCRIPT}",
    ]

    try:
        subprocess.run(ssh_cmd, check=True)
        print("fMRIPrep pipeline executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error during fMRIPrep pipeline execution.")
        print(f"Exit code: {e.returncode}")
        print(f"Command: {e.cmd}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
