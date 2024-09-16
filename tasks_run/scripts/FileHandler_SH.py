import glob
import os
import sys
import settings
import subprocess
import Logger
from typing import Union
import shutil
import time

def get_most_recent(action: str, dicom_dir: str = None) -> str:
    if action == "dicom":
        if dicom_dir is None:
            Logger.print_and_log(f"param 'dicom_dir' must be also used if running get_most_recent(action='dicom')")
            sys.exit(1)

        dicoms: list = glob.glob(os.path.join(dicom_dir, "*.dcm"))
        if not dicoms:
            Logger.print_and_log(f"Could Not Find any dicoms at {dicom_dir}")
            sys.exit(1)

        most_recent_dicom: str = max(dicoms, key=os.path.getmtime)
        return most_recent_dicom

    elif action == "dicom_dir":
        dirs_in_samba: list = [os.path.join(settings.SAMBASHARE_DIR_PATH, file) for file in os.listdir(settings.SAMBASHARE_DIR_PATH) if os.path.isdir(os.path.join(settings.SAMBASHARE_DIR_PATH, file))]

        if not dirs_in_samba:
            Logger.print_and_log(f"There Are No Dicom Dirs in: {settings.SAMBASHARE_DIR_PATH}")
            sys.exit()

        most_recent_dir: str = max(dirs_in_samba, key=os.path.getmtime)
        return most_recent_dir

    else:
        Logger.print_and_log(f"Unknown action: {action}")
        sys.exit(1)

def dicom_to_nifti(dicom_file: str, trial: Union[int, str], WaitAfterRun: bool) -> str:
    result = subprocess.run(['dcm2niix', '-f', f'nii_TR{trial}', '-s', 'y', '-o', settings.NIFTI_TMP_OUTDIR, dicom_file])

    if WaitAfterRun:
        time.sleep(settings.RETRY_WAIT_TIME)

    if result.returncode != 0:
        raise Exception(f"dcm2niix failed with error code {result.returncode}\n"
                        f"stderr: {result.stderr}\n"
                        f"stdout: {result.stdout}")

    nifti_path = os.path.join(settings.NIFTI_TMP_OUTDIR, f'nii_TR{trial}.nii')
    if not os.path.exists(nifti_path):
        raise Exception("Cannot Find Nifti Image After dcm2niix")

    return nifti_path

def clear_nifti_dir():
    if os.path.exists(settings.NIFTI_TMP_OUTDIR):
        for item in os.listdir(settings.NIFTI_TMP_OUTDIR):
            item_path = os.path.join(settings.NIFTI_TMP_OUTDIR, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    if not len(os.listdir(settings.NIFTI_TMP_OUTDIR)) == 0:
        Logger.print_and_log(f"Issue Clearing Nifti Temp Dir: {settings.NIFTI_TMP_OUTDIR}")

    else:
        Logger.print_and_log("Nifti Outdir Cleared")