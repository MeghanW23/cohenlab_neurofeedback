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
import shutil
import warnings
import nibabel as nib

def is_binary_mask(mask: nib.Nifti1Image) -> bool:
    mask_data = mask.get_fdata()
    unique_values = np.unique(mask_data)
    return np.array_equal(unique_values, [0, 1])

def dicom_to_nifti(task: str, dicom_dir: str = None, list_of_dicoms: list = None) -> str:
    Logger.print_and_log("Running dcm2niix on dicoms...") 

    if not os.path.exists(settings.TMP_OUTDIR_PATH):
        os.makedirs(settings.TMP_OUTDIR_PATH)
    else:
        for element in os.listdir(settings.TMP_OUTDIR_PATH):
            try:
                element_path = os.path.join(settings.TMP_OUTDIR_PATH, element)
                if element == ".gitkeep":
                    continue
                elif os.path.isdir(element_path):
                    shutil.rmtree(element_path)
                else:
                    os.remove(element_path)
            except Exception as e:
                Logger.print_and_log(f"Error clearing the temporary output dir: {settings.TMP_OUTDIR_PATH}")
                Logger.print_and_log(e)
                Logger.print_and_log(f"If you are in a time crunch, clear the temporary output dir manually and re-run.")
                sys.exit(1)
            

    if dicom_dir is None and list_of_dicoms is None:
        Logger.print_and_log(f"either argument: 'dicom_dir' OR argument: 'list_of dicoms' must be assigned a non-None value.")
        sys.exit(1)

    elif dicom_dir is not None and list_of_dicoms is not None:
        Logger.print_and_log(f"either argument: 'dicom_dir' OR argument: 'list_of dicoms' must be assigned a non-None value.")
        sys.exit(1)

    elif list_of_dicoms is not None: 
        for dicom_path in list_of_dicoms:
            shutil.copy(dicom_path, settings.TMP_OUTDIR_PATH)
        subprocess.run(['dcm2niix', settings.TMP_OUTDIR_PATH], check=True)
        Logger.print_and_log(f"Conversion completed. NIfTI files saved to {settings.TMP_OUTDIR_PATH}")

    else:
        subprocess.run(['dcm2niix', '-o', settings.TMP_OUTDIR_PATH, dicom_dir], check=True)
        Logger.print_and_log(f"Conversion completed. NIfTI files saved to {settings.TMP_OUTDIR_PATH}")
    

    nii_img_path = FileHandler.get_most_recent(action="nifti_in_tmp_dir")

    if not os.path.exists(nii_img_path):
        Logger.print_and_log(f"the resulting 4d nifti task data could not be found post-dcm2niix. It is likely that dcm2niix failed. Please look possible issues in the inputted data.")
        sys.exit(1)
    
    else:
        nii_img_dims = nib.load(nii_img_path).get_fdata().shape
        if len(nii_img_dims) != 4: 
            Logger.print_and_log(f"The resulting nifti task data is not four dimensional:\n {nii_img_dims}")
            Logger.print_and_log("It is likely that dcm2niix failed. Please look possible issues in the inputted data.")

    # Get the expected number of trials based on the task
    if task == 'm':
        expected_trials = settings.MSIT_N_TRIALS
    elif task == 'r':
        expected_trials = settings.RIFG_N_TRIALS
    else:
        expected_trials = None

# Check if the number of frames matches the expected trials
    if expected_trials is not None and nii_img_dims[3] != expected_trials:
        warnings.warn(
            f"The 4D NIfTI image task data's number of 3D frames ({nii_img_dims[3]}) "
            f"does not equal the expected number of trials for the {task} task ({expected_trials})"
        )
    else:
        Logger.print_and_log(f"The 4D NIfTI task data has {nii_img_dims[3]} 3D frames.")

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
            func_slice_path, "--alpha", "70", 
            reg_mask_path, "--alpha", "77.5", "--cmap", "brain_colours_bluegray", 
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
            choseThr: str = input(f"Threshold Binary Mask so that voxels with intensities in the {threshold}% or higher percentile (pre-clusering) are included? (y/n): ")
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

start_time = datetime.now()
Logger.print_and_log(f"Script starting at: {start_time.strftime('%Y%m%d_%H%M%S')}")

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
task_dicoms = FileHandler.get_task_DICOMS(dicom_dir_path=dicom_dir, task=choose_task)

nifti_4d_path = dicom_to_nifti(task=choose_task, list_of_dicoms=task_dicoms)
nifti_image_4d_task_data = image.load_img(nifti_4d_path)

# get the ROI mask and binarize if necessary 
roi_mask_path: str = FileHandler.get_most_recent(action="roi_mask", get_registered_mask=True)
print(f"Path to Input Registered ROI Mask: {roi_mask_path}")
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


total_time = datetime.now() - start_time
total_seconds = int(total_time.total_seconds())

Logger.print_and_log(f"Total Time: {total_seconds}s")

