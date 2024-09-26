import settings
import ScriptManager
import Logger
import FileHandler
import nibabel as nib
import numpy as np
from nilearn import image, masking
import os
import subprocess
"""
INPUTS:
- Task Dicoms (MSIT or RIFG)
- Subject-Space Mask 
- Event CSV 

OUTPUT:
- Localized Mask

STEPS: 
1. dcm2niix
2. check if binary 
"""
def is_binary_mask(mask: nib.Nifti1Image) -> bool:
    mask_data = mask.get_fdata()
    unique_values = np.unique(mask_data)
    return np.array_equal(unique_values, [0, 1])

def dicom_to_nifti(dicom_dir: str) -> str:
    if not os.path.exists(settings.TMP_OUTDIR_PATH):
        os.makedirs(settings.TMP_OUTDIR_PATH)

    subprocess.run(['dcm2niix', '-o', settings.TMP_OUTDIR_PATH, dicom_dir], check=True)
    Logger.print_and_log(f"Conversion completed. NIfTI files saved to {settings.TMP_OUTDIR_PATH}")

    nii_img_path = FileHandler.get_most_recent(action="nifti_in_tmp_dir")

    return nii_img_path

# get pid
pid = ScriptManager.get_participant_id()

# create output log
Logger.create_log(filetype=".txt", log_name=f"{pid}_localization_log")

# get event file
while True:
    choose_task = input("Did you run task: MSIT or RIFG (m/r): ")
    if choose_task == "m":
        Logger.print_and_log("OK, Using MSIT Event CSV")
        event_csv = settings.MSIT_EVENT_CSV
        break

    elif choose_task == "r":
        Logger.print_and_log("OK, Using RIFG Event CSV")
        event_csv = settings.RIFG_EVENT_CSV
        break

    else:
        Logger.print_and_log("Please choose either 'r' or 'm'.")

roi_mask_path: str = FileHandler.get_most_recent(action="roi_mask")
dicom_dir: str = FileHandler.get_most_recent(action="dicom_dir")

roi_mask = nib.load(roi_mask_path)
if not is_binary_mask(roi_mask):
    Logger.print_and_log("Mask is not binary. Binarizing now .. ")
    roi_mask = image.binarize_img(roi_mask, threshold=0)
    Logger.print_and_log("Mask is binarized")

