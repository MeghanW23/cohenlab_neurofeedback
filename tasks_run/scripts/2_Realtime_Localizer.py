import settings
import ScriptManager
import Logger
import FileHandler
import os
import subprocess
import pandas as pd
from datetime import datetime
import nibabel as nib
import numpy as np
from nilearn import image, masking
from nilearn.glm.first_level import FirstLevelModel
import sys
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

def visualizer(mask_path: str, reg_mask_path: str, func_slice_path: str):
    # see: https://open.win.ox.ac.uk/pages/fsl/fsleyes/fsleyes/userdoc/command_line.html

    input_paths = [mask_path, reg_mask_path, func_slice_path]
    for path in input_paths:
        if not os.path.exists(path):
            Logger.print_and_log(f"Could not find file: {path}")
            return None

    Logger.print_and_log("NOTE: Exit fsleyes to continue the script.")
    try:
        # Run FSLeyes with the specified options
        subprocess.run([
            "fsleyes", 
            "--scene", "3d",
            func_slice_path, "--alpha", "75", 
            reg_mask_path, "--alpha", "85", "--cmap", "brain_colours_bluegray", 
            mask_path, "--cmap", "red-yellow"
            ])    
    except Exception as e:
        Logger.print_and_log(f"Error running fsleyes: {e}")

def setup_threshold(z_map, nifti_4d_img: str, pid: str, reg_roi_mask_path: str, reg_roi_mask):
    Logger.print_and_log("Making 3d slice now...")
    func_slice_path = os.path.join(settings.TMP_OUTDIR_PATH, f"func_slice_{pid}")
    nib.save(image.index_img(nifti_4d_img, 0), func_slice_path)

    ss_func_slice_path = os.path.join(settings.TMP_OUTDIR_PATH, f"ss_func_slice_{pid}.nii.gz")
    subprocess.run(["bet", func_slice_path, ss_func_slice_path])

    # set prelim threshold, initialize variables
    threshold: float = 50.0
    RunningThresholding = True 
    output_mask_filename = ""
    while RunningThresholding:
        GetThresh = True
        while GetThresh:
            choseThr: str = input(f"Threshold Binary Mask so that voxels with intensities in the {threshold}%  or higher percentile are included? (y/n): ")
            if choseThr == "y": 
                Logger.print_and_log(f"Ok, Thresholding mask at percentile: {threshold}%")

                output_mask_path = calculate_threshold(threshold=threshold, reg_roi_mask=reg_roi_mask, z_map=z_map)

                GetThresh = False
                break

            elif choseThr == "n":
                while True:
                    try:
                        threshold = float(input("Please enter desired percentile threshold for voxels in mask (between 0 and 100): "))
                    except Exception as e:
                        Logger.print_and_log("Please enter valid number")
                    if threshold < 0 or threshold > 100:
                        Logger.print_and_log("Please enter a number between 0 and 100")
                    else:
                        Logger.print_and_log(f"Ok, Thresholding mask at percentile: {threshold}%")
                        
                        output_mask_path = calculate_threshold(threshold=threshold,reg_roi_mask=reg_roi_mask, z_map=z_map)

                        GetThresh = False
                        break
            
            else: 
                print("Please type either 'y' or 'n'")

        
        while True:
            choose_visualize = input("Visualize the thresholded mask in fsleyes? (y/n): ")
            if choose_visualize == "y":
                Logger.print_and_log("Ok, booting fsleyes ...")
                print(output_mask_filename)
                visualizer(mask_path=output_mask_path, 
                           func_slice_path=ss_func_slice_path,
                           reg_mask_path=reg_roi_mask_path)
                while True: 
                    accept = input("Accept this mask? (y/n): ")
                    if accept == "y":
                        Logger.print_and_log("Ok, localizer is all set.")
                        RunningThresholding = False
                        break
                    elif accept == "n":
                        break
                    else:
                       Logger.print_and_log("Please enter either 'y' or 'n'")
                break
            elif choose_visualize == "n":
                Logger.print_and_log("Ok, localizer is all set.")
                RunningThresholding = False
                break
            else: 
                Logger.print_and_log("Please enter either 'y' or 'n'")

def calculate_threshold(threshold, reg_roi_mask, z_map):
    output_mask_filename: str = f"{pid}_localized_mask_thr{int(threshold)}_{(datetime.now()).strftime('%Y%m%d_%H%M%S')}.nii.gz"

    thresholded_mask = image.threshold_img(z_map,
                                           threshold=f"{threshold}%",
                                           cluster_threshold=settings.CLUSTER_THRESHOLD, 
                                           mask_img=reg_roi_mask, 
                                           two_sided=False) # cut out background
    nib.save(thresholded_mask, os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename))

    """
    subprocess.run(["cluster", 
                    f"--in={os.path.join(settings.TMP_OUTDIR_PATH, 'non_binarized_zmask')}",
                    f"--thresh=0",
                    f"--othresh={os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)}",
                    "--connectivity=6"])
    """

    image.binarize_img(nib.load(os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)), threshold=0)

    return os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)
    
    # binarized_mask = image.binarize_img(thresholded_mask, threshold=0)
    # Logger.print_and_log(f"Ok, Saving mask to subj_space dir...")
    
    # output_mask_filepath: str = os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)
    # nib.save(binarized_mask, output_mask_filepath)

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

# get the input dicoms from the localizer task, make nifti file using dcm2niix
dicom_dir: str = FileHandler.get_most_recent(action="local_dicom_dir")

nifti_4d_path = dicom_to_nifti(dicom_dir)
nifti_image_4d_task_data = image.load_img(nifti_4d_path)

# get the ROI mask and binarize if necessary 
roi_mask_path: str = FileHandler.get_most_recent(action="roi_mask", get_registered_mask=True)
print(f"path to roi mask: {roi_mask_path}")
roi_mask = image.load_img(roi_mask_path)
if not is_binary_mask(roi_mask):
    Logger.print_and_log("Mask is not binary. Binarizing now .. ")
    roi_mask = image.binarize_img(roi_mask, threshold=0)
    Logger.print_and_log("Mask is binarized.")

# make the first level model 
Logger.print_and_log("Starting GLM...")
fmri_glm = FirstLevelModel(t_r=settings.repetitionTime,
                           standardize=False,
                           signal_scaling=0,
                           smoothing_fwhm=6,
                           hrf_model=None,
                           drift_model='cosine',
                           high_pass=0.01,
                           mask_img=roi_mask)

# fit the GLM
Logger.print_and_log("Fitting the GLM ...")
try:
    fmri_glm = fmri_glm.fit(nifti_image_4d_task_data, event_csv)
except ValueError as e:
    Logger.print_and_log("Error fitting the GLM to the Nii Timage: ")
    Logger.print_and_log(e)
    Logger.print_and_log("This error typically occurs when there is no data in the registered mask you grabbed. Please check for errors in the registration process.")
design_matrix = fmri_glm.design_matrices_[0]
num_of_conditions = design_matrix.shape[1]

# compute the contrast between the conditions and create the resulting ROI zmap
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
nib.save(z_map, os.path.join(settings.TMP_OUTDIR_PATH, "z_map"))

# interactively threshold the mask
setup_threshold(z_map=z_map,
                nifti_4d_img=nifti_image_4d_task_data,
                pid=pid,
                reg_roi_mask=roi_mask, 
                reg_roi_mask_path=roi_mask_path)




