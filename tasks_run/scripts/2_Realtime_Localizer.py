from datetime import datetime
import sys
from typing import Optional
import ScriptManager
import settings
import os
import glob
import FileHandler
import shutil
import subprocess
from nilearn import image, plotting
import nibabel as nib
import numpy as np
from nilearn.glm.first_level import FirstLevelModel
import pandas as pd
from nilearn import image
from skimage.segmentation import watershed
import Logger

def select_task() -> str:

    task = get_response(question="Did you run the MSIT task or the RIFG task? (m/r): ", acceptable_answers=['m', 'r'])
    

    if task == "m": return "msit"


    elif task == "r": return "rifg"
        

def get_event_file(task_name: str) -> str: 

    if task_name == "msit": 
        
        return settings.MSIT_EVENT_CSV
    
    else:
        
        files: list[str] = []
        for index, file in enumerate(os.listdir(settings.RIFG_EVENT_CSV_DIR)): 
            path = os.path.join(settings.RIFG_EVENT_CSV_DIR, file)
            if "preRIFG" in file and ".csv" in file and "practice" not in file:
                files.append(path)

        if files: 
            return max(files, key=os.path.getmtime)

        else: 
            
            raise FileNotFoundError(f"Could not find any files in the RIFG_EVENT_CSV_DIR: \n{settings.RIFG_EVENT_CSV_DIR}")


def get_task_dicoms(from_metadata: bool, dicom_dir: str, task_name: str) -> list[str]:

    if from_metadata: 

        return FileHandler.get_task_DICOMS(dicom_dir_path=dicom_dir, task=task_name)

    else: 

        return [os.path.join(dicom_dir, dicom) for dicom in os.listdir(dicom_dir)]


def clear_tmp_outdir():

    if not os.path.exists(settings.TMP_OUTDIR_PATH): os.makedirs(settings.TMP_OUTDIR_PATH)

    else: 
        
        try:

            for element in os.listdir(settings.TMP_OUTDIR_PATH):

                element_path = os.path.join(settings.TMP_OUTDIR_PATH, element)

                if element == ".gitkeep": continue

                elif os.path.isdir(element_path): shutil.rmtree(element_path)

                else: os.remove(element_path)

        except Exception as e: 
            
            print(f"Error clearing the temporary output dir: {e}")


def dicom_to_nifti(dicom_list: list[str]):
    

    clear_tmp_outdir()
    

    # copy to temp outdir to process 
    for dicom_path in dicom_list: 
        
        shutil.copy(dicom_path, settings.TMP_OUTDIR_PATH)
        

    subprocess.run(['dcm2niix', settings.TMP_OUTDIR_PATH], check=True)

    return FileHandler.get_most_recent(action="nifti_in_tmp_dir")


def binarize_roi_mask(roi_mask: str | nib.Nifti1Image) -> tuple[nib.Nifti1Image, bool]:
    

    def is_binary_mask(mask: nib.Nifti1Image) -> bool:

        mask_data = mask.get_fdata()

        unique_values = np.unique(mask_data)

        return np.array_equal(unique_values, [0, 1])
    

    if isinstance(roi_mask, str): roi_mask = nib.load(roi_mask)
    
    roi_mask: nib.Nifti1Image = image.load_img(roi_mask)
    
    binarized: bool = False

    if not is_binary_mask(mask=roi_mask):
        
        binarized = True 

        print("Mask is not binary. Binarizing now .. ")

        roi_mask = image.binarize_img(roi_mask, threshold=0)
    

    return roi_mask, binarized


def get_contrast_list_at_each_condition(number_of_conditions: int, conditions_and_their_order: list[tuple[str, int]]) -> dict[list[float]]:

    contrast_list_at_each_condition = { }


    for condition_tuple in conditions_and_their_order:

        contrast_list_at_each_condition[condition_tuple[0]] = np.zeros(number_of_conditions)

        contrast_list_at_each_condition[condition_tuple[0]][condition_tuple[1]] = 1


    # print out to show the whole thing together 
    for key, row in contrast_list_at_each_condition.items():
        
        print(f"{row} -> {key}\n")

    return contrast_list_at_each_condition


def get_contrast_vector(task_name: str, contrast_dict: dict[list[float]], design_matrix: pd.DataFrame, contrast_matrix_output_path: str, expected_trial_types: list[str]) -> np.ndarray:

    # make the contrast vector
    contrast_vector: list[float] = []

     # get missing trial types 
    missing_trial_types: list[str] = [condition for condition in expected_trial_types if condition not in contrast_dict]
    
    if missing_trial_types: print(f"WARNING: Missing Trial Types: {', '.join(missing_trial_types)}")


    if task_name == "rifg":

        # initialize the arrays to use 
        go_trials: np.ndarray[float] = []

        contrast_vector: np.ndarray[float] = []

        # build the contrast matrix, accounting for if each type of trial is missing
        if 'hit' in missing_trial_types: 
            
            print(f"The RIFG Task Localizer Cannot Run When Missing 'run' Trial Types.")
            
            sys.exit(1)

        if 'miss' in missing_trial_types: 
            
            go_trials: np.ndarray[float] = contrast_dict['hit']
        
        else: 
            
            go_trials: np.ndarray[float] = contrast_dict['hit'] + contrast_dict['miss']


        if 'correct_rejection' in missing_trial_types and 'false_alarm' in missing_trial_types: 

            contrast_vector: np.ndarray[float] = go_trials

        elif 'correct_rejection' in missing_trial_types: 

            contrast_vector: np.ndarray[float] = go_trials - contrast_dict['false_alarm']

        elif 'false_alarm' in missing_trial_types:

            contrast_vector: np.ndarray[float] = go_trials - contrast_dict['correct_rejection']
        else:

            contrast_vector: np.ndarray[float] = (go_trials - contrast_dict['correct_rejection']) - (go_trials - contrast_dict['false_alarm'])

    else:

        if missing_trial_types: print(f"The MSIT Task Localizer Cannot Run When Missing Any Trial Types.") ; sys.exit(1)

        contrast_vector: np.ndarray[float] = contrast_dict['interference'] - contrast_dict['control']

    # make and save plot 
    plotting.plot_contrast_matrix(contrast_def=contrast_vector, 
                                  
                                  design_matrix=design_matrix, 

                                  output_file=contrast_matrix_output_path)
    
    return contrast_vector


def threshold_mask(unthresholded_mask_path: str, z_threshold: float) -> Optional[nib.Nifti1Image]:
    
    print(f"\n---- Mask Statistics ----")
    # smooth image and get an array of functional data from the data each voxel

    smooth_img = image.smooth_img(unthresholded_mask_path, fwhm=3)

    smooth_img_data: np.ndarray = smooth_img.get_fdata()

    # get the voxel with the max intensity to use as the seed 

    seed_coordinates = np.unravel_index(np.argmax(smooth_img_data), smooth_img_data.shape)

    unthresholded_num_of_voxels: int = np.sum(smooth_img_data != 0)

    # mark the seed on an array (all zero array except for seed) and use as starting point of watershed algorithm

    if not z_threshold is None:

        markers = np.zeros_like(smooth_img_data, dtype=np.uint16) 

        markers[seed_coordinates] = 1 

        # mark the seed on an array (all zero array except for seed)
        watershed_mask = watershed(-smooth_img_data, markers, mask=smooth_img_data > z_threshold)

        watershed_roi_mask = watershed_mask == markers[seed_coordinates]

        print(f"Number of Voxels in the Thresholded (Z > {z_threshold}) Mask: {np.sum(watershed_roi_mask)}")

        print(f"Percentage of Voxels Remaining Post-Thresholding: {np.round((np.sum(watershed_roi_mask) / unthresholded_num_of_voxels) * 100, decimals=2)}%")

        watershed_roi_img = nib.Nifti1Image(watershed_roi_mask.astype(np.int16), smooth_img.affine)

        print(f" ---- ")

        return watershed_roi_img
    
    else: 
        
        print(f"MNI Coordinates of the Voxel with the Highest Z-Score: {seed_coordinates}")

        print(f"Number of Voxels in the Unthresholded Mask: {unthresholded_num_of_voxels}")

        print(f"Average Z-Score of a Non-Zero Voxel in the Unthresholded Mask: {np.average(smooth_img_data != 0)}")
    
        print(f" ---- ")


def save_mask_to_file(mask_to_save: nib.Nifti1Image, filepath: str = None, participant_pid: str = None, timestamp: str = None, roi_type: str = None, threshold: str = 'None') -> str: 
    
    if filepath is None:
        
        if "." in threshold: threshold: str = threshold.replace('.', '_')

        filename: str = f"{participant_pid}_localized_{roi_type}_mask_thr_{threshold}_{timestamp}.nii.gz"

        filepath: str = os.path.join(settings.ROI_MASK_DIR_PATH, filename)
        

    nib.save(mask_to_save, filepath)

    return filepath


def visualize_thresholded_mask(thresholded_mask_path: str, registered_mask_path: str, func_slice_path: str):
    # see: https://open.win.ox.ac.uk/pages/fsl/fsleyes/fsleyes/userdoc/command_line.html

    input_paths = [thresholded_mask_path, registered_mask_path, func_slice_path]


    for path in input_paths:
        
        if not os.path.exists(path):

            print(f"Could not find file: {path}")
            
            return None


    print("NOTE: Exit fsleyes to continue the script.")

    try:

        # Run FSLeyes with the specified options

        subprocess.run([

            "fsleyes", 

            "--scene", "3d",
            
            func_slice_path, "--alpha", "70", 
            
            registered_mask_path, "--alpha", "77.5", "--cmap", "brain_colours_bluegray", 
            
            thresholded_mask_path, "--cmap", "red-yellow"
            
            ])    
        

    except Exception as e: 
        
        print(f"Error running fsleyes: {e}")


def get_response(question: str, acceptable_answers: list[str] | range, convert_to_float: bool = False ) -> any: 

    while True: 

        response = input(question).strip().lower()

        if convert_to_float: 
            
            try: 
                
                response = float(response)
                
            except ValueError: 
                
                print(f"Your response must include only numbers and decimal points")
                
                continue 
            
        if isinstance(acceptable_answers, range):
            
            if response < min(acceptable_answers) or response > max(acceptable_answers): 
                
                print(f"Your response must be between values: {min(acceptable_answers)} and {max(acceptable_answers)}")

                continue 
            
        elif not response in acceptable_answers:
                
                print(f"Your response must be one of the following options: ")
                
                for acceptable_answer in acceptable_answers: print(f"  {acceptable_answer}")

                continue
        
        return response

def ask_for_dicom_collection_method() -> bool:
    while True: 
        dicom_collection_method = input(f"Get DICOMs based on the task they are associated with (in metadata)? (y/n): ")
        if dicom_collection_method == "y":
            return True 
        
        elif dicom_collection_method == "n":
            print(f"Ok, getting ALL dicoms from the directory")

            return False 
        
        else: 
            print(f"Please enter either 'y' or 'n'")

print(f"Starting Realtime Localizer...")

print(" ** Please assure you have already created a registered-to-subject-space roi mask to run this script on. **")

print("--------------------------------------------------------------------------------")
print("STEP ONE: Getting Input Data ...")
print("--------------------------------------------------------------------------------")

# add setup info
task_data: dict = {
    "start_time": datetime.now(),

    "pid": ScriptManager.get_participant_id(),

    "task": select_task(),

    "msit_conditions": ["control", "interference"],

    "rifg_conditions": ["correct_rejection", "false_alarm", "hit", "miss"],
}

# add more setup info using the starting setup info
task_data.update({
    "textlog_path": Logger.create_log(filetype=".txt", timestamp=task_data['start_time'].strftime('%Y%m%d_%H%M%S'), log_name=f"{task_data['pid']}_localizer_log"),

    "dicom_dir": FileHandler.get_most_recent(action="local_dicom_dir"),

    "roi_mask": FileHandler.get_most_recent(action="roi_mask", get_registered_mask=True),

    "event_csv_path": get_event_file(task_data['task'])
})

task_data.update({
    "task_dicoms": get_task_dicoms(from_metadata=ask_for_dicom_collection_method(), dicom_dir=task_data['dicom_dir'], task_name=task_data['task']),

    "roi_type": "acc" if "acc" in task_data['roi_mask'] else "rifg" if "rifg" in task_data['roi_mask'] else "no_roi_found",

    "design_matrix_path": os.path.join(settings.LOCALIZER_SECONDARY_MATERIAL_DIR_PATH, f"{task_data['pid']}_{task_data['start_time'].strftime('%Y%m%d_%H%M%S')}_design_matrix.png"),

    "contrast_matrix_path": os.path.join(settings.LOCALIZER_SECONDARY_MATERIAL_DIR_PATH, f"{task_data['pid']}_{task_data['start_time'].strftime('%Y%m%d_%H%M%S')}_contrast_matrix.png"),

    "z_map_path": os.path.join(settings.LOCALIZER_SECONDARY_MATERIAL_DIR_PATH, f"{task_data['pid']}_{task_data['start_time'].strftime('%Y%m%d_%H%M%S')}_z_map.nii.gz")
})
# print the task data dictionary 
print(f"\n --- Localization Material ---")

for key, value in task_data.items(): print(f"{key}: {value}") if key != "task_dicoms" else print(f"{key} num of dicoms: {len(value)}")

print(f"--- Localization Material ---\n ")

print("--------------------------------------------------------------------------------")
print(f"STEP TWO: Converting Task Dicoms to Nifti and Loading the Image into Memory...")
print("--------------------------------------------------------------------------------")

nifti_image = image.load_img(dicom_to_nifti(dicom_list=task_data['task_dicoms']))

print("--------------------------------------------------------------------------------")
print(f"STEP THREE: Loading ROI Mask into Memory ..")
print("--------------------------------------------------------------------------------")

roi_mask, was_binarized = binarize_roi_mask(roi_mask=task_data['roi_mask'])

# save roi _mask to the input file path post-binarization if it needed to be binarized
if was_binarized: save_mask_to_file(mask_to_save=roi_mask, filepath=task_data['roi_mask'])

print("--------------------------------------------------------------------------------")
print(f"STEP FOUR: Loading Event CSV into Memory ..")
print("--------------------------------------------------------------------------------")

event_csv: pd.DataFrame = pd.read_csv(task_data['event_csv_path'], delimiter=",")
event_csv.columns = ['onset', 'duration', 'trial_type']
print("--------------------------------------------------------------------------------")
print("STEP FIVE: Fitting a General Linear Model ...")
print("--------------------------------------------------------------------------------")

# make and fit glm from event csv and roi mask
fmri_glm = FirstLevelModel(

    t_r=settings.REPETITION_TIME,
                           
    standardize=False,

    signal_scaling=0,

    smoothing_fwhm=6,

    hrf_model="spm + derivative",

    drift_model='cosine',

    high_pass=0.01,

    mask_img=roi_mask)

fmri_glm = fmri_glm.fit(nifti_image, event_csv)

print("--------------------------------------------------------------------------------")
print("STEP SIX: Getting Design Matrices and Saving to a PNG FILE ...")
print("--------------------------------------------------------------------------------")

# extract design matrix, save a plot and print it to the terminal
design_matrix = fmri_glm.design_matrices_[0]

plotting.plot_design_matrix(design_matrix, output_file=task_data['design_matrix_path'])

print(f"Design Matrix: \n   {design_matrix}\n")

print("--------------------------------------------------------------------------------")
print("STEP Seven: Making Task Contrasts...")
print("--------------------------------------------------------------------------------")

# get the list of conditions based on task name 
if task_data['task'] == "msit":
    
    task_condition_list: list[str] = task_data['msit_conditions'] 

else: 
    
    task_condition_list: list[str] = task_data['rifg_conditions']


# extract the contrast vector at each condition using the design matrix 
conditions_and_their_order: list[tuple[str, int]] = []

for design_matrix_column_index, design_matrix_column in enumerate(design_matrix.columns, start=0):  # for each column of the design matrix, check if it is the same name as a condition in the task_condition_list

    if design_matrix_column in task_condition_list: conditions_and_their_order.append((design_matrix_column, design_matrix_column_index))  # if it is, add the condition and its index in the design matrix as a tuple in the conditions_and_their_order list

contrast_dict: dict[list[float]] = get_contrast_list_at_each_condition(number_of_conditions=design_matrix.shape[1], conditions_and_their_order=conditions_and_their_order)  # give the list of tuples to the get_contrast_list_at_each_condition() function so that it can make the contrast lists 


# get the contrast vector for the whole task 
contrast_vector: np.ndarray = get_contrast_vector(task_name=task_data['task'], 
                                                   contrast_dict=contrast_dict, 
                                                   design_matrix=design_matrix, 
                                                   contrast_matrix_output_path=task_data['contrast_matrix_path'], 
                                                   expected_trial_types=task_data["rifg_conditions"] if task_data['task'] == "rifg" else task_data["msit_conditions"])


print("--------------------------------------------------------------------------------")
print("STEP Eight: Making the Preliminary Unbinarized, Unthresholded Z-Map...")
print("--------------------------------------------------------------------------------")

# get the zmap using the contrasts and save an image
z_map: nib.Nifti1Image = fmri_glm.compute_contrast(contrast_def=contrast_vector, output_type='z_score')

nib.save(img=z_map, filename=task_data['z_map_path'])

print("--------------------------------------------------------------------------------")
print("STEP Nine: Thresholding, Visualizing, and Binarizing Mask...")
print("--------------------------------------------------------------------------------")

# make a 3d func slice to visualize mask on top of 
func_slice_path = os.path.join(settings.TMP_OUTDIR_PATH, f"func_slice_{task_data['pid']}.nii")

nib.save(image.index_img(nifti_image, 0), func_slice_path)

# get prelim, unthresholded mask stats 
thresholded_img = threshold_mask(unthresholded_mask_path=z_map, z_threshold=None)

# threshold / visualize until satisfactory
while True: 
    
    # --- Get Threshold ---
    threshold: float = get_response(question="Please Input the Z-Score You Would Like to Threshold At: ", acceptable_answers=range(-5, 6), convert_to_float=True)
    
    print(f"Thresholding Mask At Z-Score: {threshold} ...")
    
    thresholded_img = threshold_mask(unthresholded_mask_path=z_map, z_threshold=threshold)


    # --- Binarize Mask ---

    binarized_mask, _ = binarize_roi_mask(roi_mask=thresholded_img)


    # --- Save Mask to File ---

    final_mask_path: str = save_mask_to_file(
        mask_to_save=binarized_mask,

        participant_pid=task_data['pid'], 

        timestamp=task_data['start_time'].strftime('%Y%m%d_%H%M%S'), 

        roi_type=task_data['roi_type'], 

        threshold=str(threshold))
    
    print(f"Created Thresholded Mask at: {final_mask_path}")
    

    # --- Visualize Results ---
    visualize_response: str = get_response(question="Visualize the Thresholded Mask? (y/n): ", acceptable_answers=['y', 'n'])

    if visualize_response == 'y':
        
        visualize_thresholded_mask(
            
            thresholded_mask_path=final_mask_path, 

            registered_mask_path=task_data['roi_mask'], 

            func_slice_path=func_slice_path)


    # --- Check if Done ---
    finish_loop: str = get_response(question="Accept the Mask and End the Localization Process? (y/n): ", acceptable_answers=['y', 'n'])

    if finish_loop == 'y': 

        print("Ok, Exiting Now.")

        sys.exit(0)

    print("Ok, Let's Re-Threshold...")