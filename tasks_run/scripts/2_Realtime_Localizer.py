import settings
import ScriptManager
import Logger
import FileHandler
import os
import subprocess
import pandas as pd
from datetime import datetime
import numpy as np
from nilearn import image
from nilearn.glm.first_level import FirstLevelModel
import sys
import shutil
import nibabel as nib
from scipy.ndimage import maximum_filter
from skimage.segmentation import watershed
from skimage import measure
import Logger
import glob


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
        expected_dcms = settings.MSIT_N_DICOMS
    elif task == 'r':
        expected_dcms = settings.RIFG_N_DICOMS
    else:
        expected_dcms = None

# Check if the number of frames matches the expected trials
    if expected_dcms is not None and nii_img_dims[3] != expected_dcms:
        Logger.print_and_log(f"-------------------- WARNING --------------------")
        Logger.print_and_log(f"The 4D NIfTI image task data's number of 3D frames ({nii_img_dims[3]})")
        Logger.print_and_log(f"does not equal the expected number of dicoms for the {task} task ({expected_dcms})")
        Logger.print_and_log(f"-------------------- WARNING --------------------")
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

def setup_threshold(z_map, nifti_4d_img: str, pid: str, reg_roi_mask_path: str, reg_roi_mask: str):
    Logger.print_and_log("Making 3d slice now...")
    func_slice_path = os.path.join(settings.TMP_OUTDIR_PATH, f"func_slice_{pid}.nii")
    nib.save(image.index_img(nifti_4d_img, 0), func_slice_path)



    # set prelim threshold, initialize variables
    output_mask_path = ""
    RunningThresholding = True 
    while RunningThresholding:
        GetThresh = True
        while GetThresh:
            choseThr: str = input(f"Threshold mask with Z-score: {settings.INITAL_Z_THRESH}? (y/n): ")
            choseThr = choseThr.replace("s", "") # scanner impulse presses 's' on computer 
            if choseThr == "y": 
                Logger.print_and_log(f"Ok, Thresholding mask at Z-score: {settings.INITAL_Z_THRESH}")

                output_mask_path = calculate_threshold(threshold=settings.INITAL_Z_THRESH, 
                                                       pid=pid, 
                                                       reg_roi_mask_path=reg_roi_mask_path, 
                                                       z_map=z_map)

                GetThresh = False
                break

            elif choseThr == "n":
                while True:
                    threshold_input = input(f"Please enter desired z-threshold for voxels in mask (between {settings.USER_Z_MIN} and {settings.USER_Z_MAX}): ")
                    threshold_input = threshold_input.replace("s", "")
                    try: 
                        threshold = float(threshold_input)
                        if settings.USER_Z_MIN <= threshold <= settings.USER_Z_MAX:
                            Logger.print_and_log(f"Ok, Thresholding mask at z-score: {threshold}")
                            output_mask_path = calculate_threshold(threshold=threshold, 
                                                                   pid=pid, 
                                                                   reg_roi_mask_path=reg_roi_mask_path, 
                                                                   z_map=z_map)
                            GetThresh = False
                            break
                        else:
                            Logger.print_and_log(f"Please enter a number between {settings.USER_Z_MIN} and {settings.USER_Z_MAX}")
                    except ValueError:
                        Logger.print_and_log("Please enter a valid number")

        
        while True:
            choose_visualize = input("Visualize the thresholded mask in fsleyes? (y/n): ")
            choose_visualize = choose_visualize.replace("s", "")

            if choose_visualize == "y":
                Logger.print_and_log("Ok, booting fsleyes ...")
                visualizer(mask_path=output_mask_path, 
                           func_slice_path=func_slice_path,
                           reg_mask_path=reg_roi_mask_path)
                while True: 
                    accept = input("Accept this mask? (y/n): ")
                    accept = accept.replace("s", "")

                    if accept == "y":
                        Logger.print_and_log("Ok, localizer is all set.")
                        Logger.print_and_log(f"Find localized mask at: {output_mask_path}")
                        RunningThresholding = False
                        break
                    elif accept == "n":
                        break
                    else:
                       Logger.print_and_log("Please enter either 'y' or 'n'")
                break
            elif choose_visualize == "n":
                Logger.print_and_log("Ok, localizer is all set.")
                Logger.print_and_log(f"Find localized mask at: {output_mask_path}")
                RunningThresholding = False
                break
            else: 
                Logger.print_and_log("Please enter either 'y' or 'n'")

def calculate_threshold_old(threshold: float, pid: str, z_map: nib.Nifti1Image) -> str:
    
    """
    Calculate the thresholded and localized mask for a given z-map.

    Parameters:
    - threshold (float): The z-score threshold.
    - pid (str): The participant ID.
    - z_map (nib.Nifti1Image): The z-map image (NIfTI format).

    Returns:
    - str: The path to the saved mask image.
    """
    # extract z-score data and put into an array
    zmap_data: np.ndarray = z_map.get_fdata()

    # threshold the array based on the z-threshold given via user input 
    thresholded_zmap: np.ndarray = np.where(zmap_data > threshold, zmap_data, 0)

    # find local maxima in the thresholded_zmap by comparing each voxel to neighbors in a 3x3x3 cube and makes a new array (local_max) where each voxel is the maximum of its neighborhood
    local_max: np.ndarray = maximum_filter(thresholded_zmap, size=settings.LOCAL_MAXIMA_VOXEL_CUBE_DIM)

    # identify voxels that are local maxima and also non-zero
    local_maxima: np.ndarray = (thresholded_zmap == local_max)
    
    # label assigns a unique integer to each connected region of True values in local_maxima
    markers: np.ndarray = measure.label(local_maxima)

    # watershed algorithm grows regions from the markers based on the original z-scores, capturing areas of significant activation around the local maxima.
    mask: np.ndarray = watershed(-thresholded_zmap, markers, mask=thresholded_zmap > 0)

    # save using original z-map’s affine transformation matrix (zmap_img.affine) to preserve the spatial orientation.
    watershed_mask: nib.Nifti1Image = nib.Nifti1Image(mask.astype(np.int32), z_map.affine)

    # remove clusters less than a certain number of voxels in size
    cluster_thresh_mask_img: nib.Nifti1Image = image.threshold_img(img=watershed_mask, 
                                                                   threshold=0, 
                                                                   cluster_threshold=settings.CLUSTER_THRESHOLD)
    
    # binarize mask 
    output_mask: nib.Nifti1Image = image.binarize_img(cluster_thresh_mask_img, threshold=0)
    
    # save mask to subj_space mask dir 
    threshold_string_for_filename: str = str(threshold).replace(".", "_")
    output_mask_filename: str = f"{pid}_localized_mask_thr_{threshold_string_for_filename}_{(datetime.now()).strftime('%Y%m%d_%H%M%S')}.nii.gz"
    mask_path: str = os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)
    nib.save(output_mask, mask_path)

    return mask_path

def calculate_threshold(threshold: float, pid: str, reg_roi_mask_path: str, z_map: nib.Nifti1Image) -> str:
    # smooth img
    smooth_img = image.smooth_img(z_map, fwhm=3)
    
    # extract z-score data and put into an array
    smooth_img_data: np.ndarray = smooth_img.get_fdata()
    largest_z_threshold = np.max(smooth_img_data)
    Logger.print_and_log(f"Max Z Score: {largest_z_threshold} ")

    # get the coordinates for this point
    seed_coordinates = np.unravel_index(np.argmax(smooth_img_data), smooth_img_data.shape)
    Logger.print_and_log(f"Max Z Score Coordinates: {seed_coordinates} ")

    # mark the seed on an array (all zero array except for seed)
    markers = np.zeros_like(smooth_img_data, dtype=np.uint16)  # Use uint16 for watershed_ift
    markers[seed_coordinates] = 1  # Mark the seed point

    # Perform the watershed
    watershed_mask = watershed(-smooth_img_data, markers, mask=smooth_img_data > threshold)
    watershed_roi_mask = watershed_mask == markers[seed_coordinates]

    # Count the number of True elements in the watershed_roi_mask
    Logger.print_and_log(f"Voxels post-watershed: {np.sum(watershed_roi_mask)}")


    watershed_roi_img = nib.Nifti1Image(watershed_roi_mask.astype(np.int16), smooth_img.affine)

    return make_filename(pid=pid, 
                         reg_roi_mask_path=reg_roi_mask_path, 
                         threshold=str(threshold), 
                         img_to_save=watershed_roi_img)

def make_filename(pid: str, reg_roi_mask_path: str, threshold: str, img_to_save: nib.Nifti1Image) -> str:

    threshold_string_for_filename = ""
    if "." in threshold:
        threshold_string_for_filename: str = str(threshold).replace(".", "_")
    else:
        threshold_string_for_filename: str = str(threshold)
    
    if "acc" in reg_roi_mask_path:
        roi_type = "acc"
    elif "rifg" in reg_roi_mask_path:
        roi_type = "rifg"
    elif "motor" in reg_roi_mask_path:
        roi_type = "motor"
    else:
        roi_type=""

    Logger.print_and_log(f"Input mask is an {roi_type} mask")
    output_mask_filename: str = f"{pid}_localized_{roi_type}_mask_thr_{threshold_string_for_filename}_{(datetime.now()).strftime('%Y%m%d_%H%M%S')}.nii.gz"
    mask_path: str = os.path.join(settings.ROI_MASK_DIR_PATH, output_mask_filename)
    nib.save(img_to_save, mask_path)

    return mask_path

def get_latest_event_file(directory, prefix):
    search_pattern = os.path.join(directory, f"{prefix}RIFG_events.csv")
    files = glob.glob(search_pattern)
    return max(files, key=os.path.getmtime) if files else None


# get pid
pid = ScriptManager.get_participant_id()

# create output log
Logger.create_log(filetype=".txt", log_name=f"{pid}_localization_log")
POST_RIFG_EVENT_CSV = get_latest_event_file(settings.RIFG_EVENT_CSV_DIR , "postRIFG_events.csv")
PRE_RIFG_EVENT_CSV = get_latest_event_file(settings.RIFG_EVENT_CSV_DIR, "preRIFG_events.csv")
Logger.print_and_log(f"Pre RIFG Event CSV {POST_RIFG_EVENT_CSV}")

start_time = datetime.now()
Logger.print_and_log(f"Script starting at: {start_time.strftime('%Y%m%d_%H%M%S')}")


# get event file
choose_task = ""
while True:
    choose_task = input("Did you run task: MSIT or RIFG (m/r): ")
    choose_task = choose_task.replace("s", "") 
    if choose_task == "m":
        Logger.print_and_log("OK, Using MSIT Event CSV")
        event_csv = pd.read_csv(settings.MSIT_EVENT_CSV, delimiter=",")
        break

    elif choose_task == "r":
        while True:
            Logger.print_and_log("OK, Using RIFG Event CSV")
            use_file = input("Would you like to use the pre or post RIFG event file? (pre/post): ").lower()
            if use_file == "post":
                event_csv_path = POST_RIFG_EVENT_CSV
                break
            elif use_file == "pre":
                event_csv_path = PRE_RIFG_EVENT_CSV
                break
            else:
                Logger.print_and_log("Invalid choice. Please type 'pre' or 'post'.")

        if event_csv_path:
            event_csv = pd.read_csv(event_csv_path, delimiter=",")
        else:
            Logger.print_and_log("Error: No valid RIFG event file found.")
            raise FileNotFoundError("No valid RIFG event file found.")
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
Logger.print_and_log(f"Path to Input Registered ROI Mask: {roi_mask_path}")
roi_mask = image.load_img(roi_mask_path)
if not is_binary_mask(roi_mask):
    Logger.print_and_log("Mask is not binary. Binarizing now .. ")
    roi_mask = image.binarize_img(roi_mask, threshold=0)
    Logger.print_and_log(f"Saving binarized mask to the register mask path.")
    nib.save(roi_mask, roi_mask_path)
    Logger.print_and_log("Mask is binarized.")

# make the first level model 
Logger.print_and_log("Starting GLM...")
fmri_glm = FirstLevelModel(t_r=settings.REPETITION_TIME,
                           standardize=False,
                           signal_scaling=0,
                           smoothing_fwhm=6,
                           hrf_model="spm + derivative",
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
    conditions = {"correct rejection": np.zeros(num_of_conditions), "false alarm": np.zeros(num_of_conditions)}
    conditions["correct rejection"][1] = 1
    conditions["false alarm"][0] = 1
    inter_minus_con = conditions["correct rejection"] - conditions["false alarm"]
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

