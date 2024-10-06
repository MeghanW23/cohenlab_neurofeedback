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
        Logger.print_and_log(f"Directories found in {settings.SAMBASHARE_DIR_PATH}: {dirs_in_samba}")
        if dirs_in_samba is None or dirs_in_samba == []:
            Logger.print_and_log(f"There Are No Dicom Dirs in: {settings.SAMBASHARE_DIR_PATH}")
            sys.exit()

        most_recent_dir: str = max(dirs_in_samba, key=os.path.getmtime)
        return most_recent_dir

    elif action == "roi_mask":
        masks: list = glob.glob(os.path.join(settings.ROI_MASK_DIR_PATH, "*.nii")) + \
                      glob.glob(os.path.join(settings.ROI_MASK_DIR_PATH, "*.nii.gz"))
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
        elif ScriptManager.script_name_in_stack(settings.MSIT_SCRIPT_NAME_PRE):
            textfiles: list = glob.glob(os.path.join(settings.MSIT_LOG_DIR, "*.txt"))
        elif ScriptManager.script_name_in_stack(settings.MSIT_SCRIPT_NAME_POST):
            textfiles: list = glob.glob(os.path.join(settings.MSIT_LOG_DIR, "*.txt"))
        elif ScriptManager.script_name_in_stack(settings.LOCALIZER_FILE_NAME):
            textfiles: list = glob.glob(os.path.join(settings.LOCALIZER_LOG_DIR, "*.txt"))

        else:
            print("Could Not Find the Script Calling this func, please edit FileHandler's get_most_recent() func")
            sys.exit(1)

        if textfiles is None or textfiles == []:
            print(f"Could Not Find any Text Output Logs at the specified directory.")
            sys.exit(1)

        most_recent_txt_file: str = max(textfiles, key=os.path.getmtime)

        return most_recent_txt_file
    elif action == "nifti_in_tmp_dir":
        nii_imgs = [os.path.join(str(os.getenv("TMP_OUTDIR_PATH")), current_img) for current_img in str(os.getenv("TMP_OUTDIR_PATH")) if current_img.endswith(".nii") or current_img.endswith(".nii.gz")]
        most_recent_nifti = max(nii_imgs, key=os.path.getmtime)
        return most_recent_nifti

    else:
        Logger.print_and_log(f" {action} is not a valid choice for get_most_recent() param: 'action'")

def dicom_to_nifti(dicom_file: str, trial: Union[int, str], WaitAfterRun: bool) -> str:
    result = subprocess.run(['dcm2niix', '-f', f'nii_TR{trial}', '-s', 'y', '-o', str(os.getenv("TMP_OUTDIR_PATH")), dicom_file])

    if WaitAfterRun:
        time.sleep(float(os.getenv("WAIT_BEFORE_RETRY")))

    if result.returncode != 0:
        raise Exception(f"dcm2niix failed with error code {result.returncode}\n"
                        f"stderr: {result.stderr}\n"
                        f"stdout: {result.stdout}")

    nifti_path = os.path.join(str(os.getenv("TMP_OUTDIR_PATH")), f'nii_TR{trial}.nii')
    if not os.path.exists(nifti_path):
        raise Exception("Cannot Find Nifti Image After dcm2niix")

    return nifti_path

def clear_nifti_dir():
    tmp_outdir_path = str(os.getenv("TMP_OUTDIR_PATH"))
    if os.path.exists(tmp_outdir_path):
        for item in os.listdir(tmp_outdir_path):
            item_path = os.path.join(tmp_outdir_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    if not len(os.listdir(tmp_outdir_path)) == 0:
        Logger.print_and_log(f"Issue Clearing Temp Dir: {tmp_outdir_path}")

    else:
        Logger.print_and_log("Nifti Outdir Cleared")