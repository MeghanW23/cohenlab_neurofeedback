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
    "nfb_fmriprep/fmriprep_pipeline_adapted/run_fmriprep_sbatch.sh"
)

def get_chid() -> str:
    chid = os.environ.get("CHID")
    if not chid:
        raise RuntimeError(
            "CHID environment variable is not set inside the container.\n"
            'The wrapper script should pass "-e CHID=\\"$CHID\\"" to docker run.'
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
        # Run without check=True so we can interpret return codes
        result = subprocess.run(ssh_cmd)
    except KeyboardInterrupt:
        # In case Python itself gets Ctrl-C (usually ssh gets it first)
        print("\nSSH session interrupted by user (Ctrl-C).")
        print("If the job was submitted, it will continue running on e3.")
        sys.exit(0)

    rc = result.returncode

    if rc == 0:
        print("fMRIPrep pipeline executed successfully.")
        sys.exit(0)

    # Treat common Ctrl-C/SSH abort codes as non-error exits
    if rc in (130, 255):
        print("\nSSH session ended (likely via Ctrl-C or remote disconnect).")
        print("If the fMRIPrep job was submitted, it should still be running on e3.")
        sys.exit(0)

    # Anything else is a real error
    print("Error during fMRIPrep pipeline execution.")
    print(f"Exit code: {rc}")
    print(f"Command: {ssh_cmd}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
