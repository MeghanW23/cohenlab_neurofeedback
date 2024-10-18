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

def visualizer(mask_path: str, func_slice_path: str):
    # see: https://open.win.ox.ac.uk/pages/fsl/fsleyes/fsleyes/userdoc/command_line.html
    try:
        subprocess.run(["fsleyes", func_slice_path, "--alpha", "85", mask_path, "--cmap", "red-yellow"])
    except Exception as e:
        Logger.print_and_log(f"Error running fsleyes: {e}")

def get_threshold(zmap, pid: str):
    # ask experimenter for threshold
    threshold: float = 50

    choseThr: str = input(f"Threshold Binary Mask so that top {threshold}% of voxels are included? (y/n): ")
    while True:
        if choseThr == "y": 
            Logger.print_and_log(f"Ok, Thresholding mask at {threshold}")
            binarized_z_map = image.binarize_img(z_map, threshold=threshold)

            Logger.print_and_log(f"Ok, Saving mask to subj_space dir...")
            output_mask_filename: str = f"{pid}_localized_mask_thr{threshold}_{(datetime.now()).strftime("%Y%m%d_%H%M%S")}"
            output_mask_filepath: str = os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)
            nib.save(binarized_z_map, output_mask_filepath)

        elif choseThr == "n":
            while True:
                try:
                    threshold = float(input("Please enter desired % of voxels in mask (between 0 and 100): "))
                    if threshold < 0 or threshold > 100:
                        Logger.print_and_log("Please enter a number between 0 and 100%")
                    else:
                        Logger.print_and_log(f"Ok, Thresholding mask at {threshold}")
                        binarized_z_map = image.binarize_img(z_map, threshold=threshold)

                        Logger.print_and_log(f"Ok, Saving mask to subj_space dir...")
                        output_mask_filename: str = f"{pid}_localized_mask_thr{threshold}_{(datetime.now()).strftime("%Y%m%d_%H%M%S")}"
                        output_mask_filepath: str = os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)
                        nib.save(binarized_z_map, output_mask_filepath)
                        break

                except Exception as e:
                    Logger.print_and_log("Please enter valid number")
        else:
            Logger.print_and_log("Please enter either 'y' or 'n'")
        
        

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

nifti_image_path_4d_task_data: str = dicom_to_nifti(dicom_dir)
nifti_image_4d_task_data = image.load_img(nifti_image_path_4d_task_data)

# skull strip nifti image
Logger.print_and_log("Skull Stripping Data now...")
subj_skull_stripped = masking.compute_brain_mask(nifti_image_4d_task_data)

# GLM
Logger.print_and_log("Starting GLM...")
fmri_glm = FirstLevelModel(t_r=settings.repetitionTime,
                           standardize=False,
                           signal_scaling=0,
                           smoothing_fwhm=6,
                           hrf_model=None,
                           drift_model='cosine',
                           high_pass=0.01,
                           mask_img=roi_mask)

fmri_glm = fmri_glm.fit(nifti_image_4d_task_data, event_csv)
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
Logger.print_and_log("Ran compute_contrast()")

# ask experimenter for threshold
threshold = 50
while True:
    choseThr = input(f"Threshold Binary Mask so that top {threshold}% of voxels are included? (y/n): ")
    if choseThr == "y":
        Logger.print_and_log(f"Ok, Mask will include voxels that are in the top {threshold}% or higher.")

        Logger.print_and_log("Starting Binarization .. ")
        binarized_z_map = image.binarize_img(z_map, threshold=threshold)

        Logger.print_and_log("Saving mask to subj_space mask directory ...")
        now = datetime.now()
        formatted_string_time: str = now.strftime("%Y%m%d_%H%M%S")
        output_mask: str = f"{pid}_localized_mask_thr{threshold}_{formatted_string_time}"
        output_file_path: str = os.path.join(settings.ROI_MASK_DIR_PATH, output_mask)
        nib.save(binarized_z_map, output_file_path)

        visualize = input(f"See the results in fsleyes? (y/n)")
        if visualize == "y":
            Visualizing = True
            print("Saving a 3d slice ...")
            func_slice_path = os.path.join(settings.TMP_OUTDIR_PATH, f"func_slice_path_{pid}")
            nib.save(image.index_img(nifti_image_4d_task_data, 0), func_slice_path)

            while Visualizing:
                visualize = input(f"See the results in fsleyes? (y/n)")
                if visualize == "y":
                    visualizer(mask_path=output_file_path, func_slice_path=func_slice_path)
                    break
                elif visualize == "n":
                    Logger.print_and_log("Ok, not visualizing ...")
                    break
                else:
                    Logger.print_and_log("Please enter either 'y' or 'n'.")
        break
    elif choseThr == "n":
         while True:
            try:
                 threshold = float(input("Please enter a new percent threshold: "))
                 break

            except ValueError:
                Logger.print_and_log("Invalid input. Please enter a numeric value.")
    else:
        Logger.print_and_log("Please choose either 'y' or 'n'.")





Logger.print_and_log(f"Find Output Mask: {output_file_path}.")




