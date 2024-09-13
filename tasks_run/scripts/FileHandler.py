import glob
import os
import sys
import settings
import subprocess
import Logger
from typing import Union
import shutil
import time
import ScriptManager

def get_most_recent(action: str, dicom_dir: str = None) -> str:
    if action == "dicom":
        if dicom_dir is None:
            Logger.print_and_log(f"param 'dicom_dir' must be also used if running get_most_recent(action='dicom')")
            sys.exit(1)

        dicoms: list = glob.glob(os.path.join(dicom_dir, "*.dcm"))
        if dicoms is None or dicoms == []:
            Logger.print_and_log(f"Could Not Find any dicoms at {dicom_dir}")
            sys.exit(1)

        most_recent_dicom: str = max(dicoms, key=os.path.getmtime)

        return most_recent_dicom

    elif action == "dicom_dir":

        dirs_in_samba: list = [os.path.join(settings.SAMBASHARE_DIR_PATH, file) for file in os.listdir(settings.SAMBASHARE_DIR_PATH) if os.path.isdir(os.path.join(settings.SAMBASHARE_DIR_PATH, file))]

        if dirs_in_samba is None or dirs_in_samba == []:
            Logger.print_and_log(f"There Are No Dicom Dirs in: {settings.SAMBASHARE_DIR_PATH}")
            sys.exit()

        most_recent_dir: str = max(dirs_in_samba, key=os.path.getmtime)
        return most_recent_dir

    elif action == "roi_mask":
        masks: list = glob.glob(os.path.join(settings.ROI_MASK_DIR_PATH, "*.nii"))
        if masks is None or masks == []:
            Logger.print_and_log(f"Could Not Find any masks at {settings.ROI_MASK_DIR_PATH}")
            sys.exit(1)

        most_recent_mask: str = max(masks, key=os.path.getmtime)

        return most_recent_mask

    elif action == "txt_output_log":
        if ScriptManager.script_name_in_stack(settings.NFB_SCRIPT_NAME):
            textfiles: list = glob.glob(os.path.join(settings.NFB_LOG_DIR, "*.txt"))
        elif ScriptManager.script_name_in_stack(settings.RIFG_SCRIPT_NAME):
            textfiles: list = glob.glob(os.path.join(settings.RIFG_LOG_DIR, "*.txt"))
        elif ScriptManager.script_name_in_stack(settings.MSIT_SCRIPT_NAME):
            textfiles: list = glob.glob(os.path.join(settings.MSIT_LOG_DIR, "*.txt"))
        else:
            print("Could Not Find the Script Calling this func, please edit FileHandler's get_most_recent() func")
            sys.exit(1)

        if textfiles is None or textfiles == []:
            Logger.print_and_log(f"Could Not Find any Text Output Logs at {settings.NFB_LOG_DIR}")
            sys.exit(1)

        most_recent_txt_file: str = max(textfiles, key=os.path.getmtime)

        return most_recent_txt_file

    else:
        Logger.print_and_log(f" {action} is not a valid choice for get_most_recent() param: 'action'")

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