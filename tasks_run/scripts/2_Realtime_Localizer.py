from nilearn.glm.first_level import FirstLevelModel
import settings
import ScriptManager
import Logger
import FileHandler
import nibabel as nib
import numpy as np
from nilearn import image, masking
import os
import subprocess
import pandas as pd
from datetime import datetime

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
choose_task = ""
while True:
    choose_task = input("Did you run task: MSIT or RIFG (m/r): ")
    if choose_task == "m":
        Logger.print_and_log("OK, Using MSIT Event CSV")
        event_csv = pd.read_csv(settings.MSIT_EVENT_CSV, delimiter=",")
        break

    elif choose_task == "r":
        Logger.print_and_log("OK, Using RIFG Event CSV")
        event_csv = pd.read_csv(settings.RIFG_EVENT_CSV, delimiter=",")
        break

    else:
        Logger.print_and_log("Please choose either 'r' or 'm'.")

roi_mask_path: str = FileHandler.get_most_recent(action="roi_mask")
dicom_dir: str = FileHandler.get_most_recent(action="dicom_dir")

roi_mask = image.load_img(roi_mask_path)
if not is_binary_mask(roi_mask):
    Logger.print_and_log("Mask is not binary. Binarizing now .. ")
    roi_mask = image.binarize_img(roi_mask, threshold=0)
    Logger.print_and_log("Mask is binarized.")

nifti_image_path_4d_taskdata: str = dicom_to_nifti(dicom_dir)
nifti_image_4d_taskdata = image.load_img(nifti_image_path_4d_taskdata)

#skull strip nifti image
Logger.print_and_log("Skull Stripping Data now...")
subj_skull_stripped = masking.compute_brain_mask(nifti_image_4d_taskdata)

#GLM
Logger.print_and_log("Starting GLM...")
fmri_glm = FirstLevelModel(t_r=settings.repetitionTime,
                           standardize=False,
                           signal_scaling=0,
                           smoothing_fwhm=6,
                           hrf_model=None,
                           drift_model='cosine',
                           high_pass=0.01,
                           mask_img=roi_mask)

fmri_glm = fmri_glm.fit(nifti_image_4d_taskdata,event_csv)
design_matrix = fmri_glm.design_matrices_[0]
num_of_conditions = design_matrix.shape[1]

inter_minus_con = []
if choose_task == "m":
    conditions = {"control": np.zeros(num_of_conditions), "interference": np.zeros(num_of_conditions)}
    conditions["interference"][1] = 1
    conditions["control"][0] = 1
    inter_minus_con = conditions["interference"] - conditions["control"]
elif choose_task == "r":
    conditions = {"rest": np.zeros(num_of_conditions), "task": np.zeros(num_of_conditions)}
    conditions["task"][1] = 1
    conditions["rest"][0] = 1
    inter_minus_con = conditions["task"] - conditions["rest"]

z_map = fmri_glm.compute_contrast(inter_minus_con, output_type='z_score')
print("Ran compute_contrast()")

# ask experimenter for threshold
threshold = 50
while True:
    choseThr = input(f"Threshold Binary Mask so that top {threshold}% of voxels are included? (y/n): ")
    if choseThr == "y":
        print(f"Ok, Mask will include voxels that are in the top {threshold}% or higher.")
        break
    elif choseThr == "n":
         while True:
            try:
                 threshold = float(input("Please enter a new percent threshold: "))
                 print(f"Mask will include voxels in the top {threshold}% or higher.")
                 break
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

Logger.print_and_log(f"Using Threshold: {threshold} of Voxels.")

Logger.print_and_log("Starting Binarization .. ")
binarized_z_map = image.binarize_img(z_map, threshold=threshold)

now = datetime.now()
formatted_string_time: str = now.strftime("%Y%m%d_%H%M%S")
output_mask: str = f"{pid}_localized_mask_thr{threshold}_{formatted_string_time}"
output_file_path: str = os.path.join(settings.ROI_MASK_DIR_PATH, output_mask)
nib.save(binarized_z_map, output_file_path)

Logger.print_and_log(f"Find Output Mask: {output_file_path}.")




