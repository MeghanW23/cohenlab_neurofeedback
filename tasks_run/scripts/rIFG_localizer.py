import os
import sys
import pandas as pd
import subprocess
import numpy as np
import nibabel as nib
from datetime import datetime
from nilearn import image, masking
from nilearn.glm.first_level import FirstLevelModel
import matplotlib.pyplot as plt

""" FUNCTIONS """
def dicom_to_nifti(dicom_dir, output_dir):
    """ Converts DICOM files to NIfTI format using dcm2niix. """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        subprocess.run(['dcm2niix', '-z', 'y', '-o', output_dir, dicom_dir], check=True)
        print(f"Conversion completed. NIfTI files saved to {output_dir}")

        nifti_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if
                       f.endswith('.nii') or f.endswith('.nii.gz')]
        if nifti_files:
            return nifti_files[0]  # Return the first NIfTI file found
        else:
            print(f"No NIfTI file found in {output_dir}")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error occurred during DICOM-to-NIfTI conversion: {e}")
        sys.exit(1)

def get_most_recent_mask(directory):
    """ Returns the most recent mask file from a given directory. """
    try:
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist.")
            return None

        files_list = [os.path.join(directory, f) for f in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, f))]

        if not files_list:
            print(f"No files found in {directory}.")
            return None

        sorted_files = sorted(files_list, key=lambda x: os.path.getmtime(x), reverse=True)
        return sorted_files[0]

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_most_recent_dir(ParentDir):
    """ Gets the most recent subdirectory in the given parent directory. """
    try:
        directories = [entry.path for entry in os.scandir(ParentDir) if entry.is_dir()]
        if not directories:
            print(f"No subdirectories found in {ParentDir}.")
            return None
        latest_directory = max(directories, key=os.path.getctime)
        return latest_directory
    except Exception as e:
        print("Error in get_most_recent_dir()")
        print(e)
        sys.exit(1)

def get_latest_FuncNii(directory):
    # Check if the directory exists and is not None
    if directory is None or not os.path.isdir(directory):
        raise ValueError(f"Provided directory does not exist or is None: {directory}")

    # Get all .nii files directly in the directory
    nii_files = [os.path.join(directory, file) for file in os.listdir(directory) if
                 os.path.isfile(os.path.join(directory, file)) and (file.endswith('.nii') or file.endswith('.nii.gz'))]
    if not nii_files:
        raise FileNotFoundError(f"No .nii or .nii.gz files found in the directory: {directory}")

    # Sort files by modification time (most recent last)
    nii_files.sort(key=os.path.getmtime)

    # Return the most recent .nii file
    return nii_files[-1] if nii_files else None

def is_binary_mask(mask_path):
    """ Checks if the mask image is binary (only contains 0s and 1s). """
    mask_img = nib.load(mask_path)
    mask_data = mask_img.get_fdata()
    unique_values = np.unique(mask_data)
    return np.array_equal(unique_values, [0, 1])

"""PATHS"""
dicom_parent_dir = "/workdir/tasks_run/data/sambashare/"
output_dir = "/workdir/tasks_run/data/subjects/dcm2niix_outputs"
mask_dir = "/workdir/tasks_run/localization_materials/"
event_file_path = "/workdir/tasks_run/msit_materials/msit_events_with_rest.csv"

timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
print(f"Timestamp to be used: {timestamp}")

# Get Subject ID from user
while True:
    pid = input("Enter Subject ID: ")
    if pid.startswith("P") and len(pid) == 4:
        print(f"Using PID: {pid}")
        break
    elif pid == "test":
        print(f"Using PID: test")
        break
    else:
        print("Invalid Subject ID. Please make sure input ID starts with 'P' and includes 3 numbers (e.g., P002). Try again.")

# Get most recent DICOM directory
dicom_dir = get_most_recent_dir(dicom_parent_dir)
subj_data_func = dicom_to_nifti(dicom_dir, output_dir)

if not os.path.exists(subj_data_func):
    print("Conversion failed. Could not find NIfTI file.")
    sys.exit(1)

# Load Event CSV
if os.path.exists(event_file_path):
    events = pd.read_csv(event_file_path)
    print(f"Using MSIT Event CSV at: {event_file_path}")
else:
    print(f"Could not find MSIT Event CSV at: {event_file_path}")
    sys.exit(1)

# Registering
while True:
    registration_method = input("Did you register using E3 or Fnirt? (e/f): ")
    if registration_method in ['e', 'f']:
        print(f"Using {'E3' if registration_method == 'e' else 'Fnirt'} registration.")
        break
    else:
        print("Please choose either 'e' or 'f'. Try again.")

# Get functional NIfTI data based on the registration method
if registration_method == 'e':
    inputFuncDataParentDir = output_dir
else:
    inputFuncDataParentDir = "/data/fnirtDir/"

inputFuncDataDir = "/workdir/tasks_run/data/subjects/dcm2niix_outputs"
subj_data_func = get_latest_FuncNii(inputFuncDataDir)

if not os.path.exists(subj_data_func):
    print(f"Couldn't find 4D functional data: {subj_data_func}")
    sys.exit(1)

# Get the registered rIFG mask
rIFG_mask_path = os.path.join(mask_dir, "mni_rIFG_mask.nii.gz")
if not os.path.exists(rIFG_mask_path):
    print(f"Could not find mask directory: {rIFG_mask_path}")
    sys.exit(1)

rIFG_mask = get_most_recent_mask(mask_dir)
if not rIFG_mask or not (rIFG_mask.endswith("nii.gz") or rIFG_mask.endswith(".nii")):
    print(f"Could not find a valid rIFG mask: {rIFG_mask}")
    sys.exit(1)

if is_binary_mask(rIFG_mask):
    print("rIFG Mask is Binary")
else:
    print("rIFG Mask is NOT binary, binarizing now...")
    try:
        rIFG_mask = image.binarize_img(rIFG_mask, threshold=0)
    except Exception as e:
        print("Error binarizing the rIFG mask")
        sys.exit(1)

# Skull Strip Data
print("Skull Stripping Data...")
try:
    subj_skull_stripped = masking.compute_brain_mask(subj_data_func)
    print("Data is skull stripped.")
except Exception as e:
    print("Error running: masking.compute_brain_mask()")
    sys.exit(1)

# Run GLM
print("Starting GLM...")
fmri_glm = FirstLevelModel(t_r=1.06,
                           standardize=False,
                           signal_scaling=0,
                           smoothing_fwhm=6,
                           hrf_model=None,
                           drift_model='cosine',
                           high_pass=0.01,
                           mask_img=rIFG_mask)

nii_file_path = get_latest_FuncNii(inputFuncDataDir)

# Check if a valid NIfTI file path is returned
if nii_file_path is None or not isinstance(nii_file_path, str):
    raise ValueError(f"Expected a valid file path but got {nii_file_path}")

# Load the NIfTI file
subj_data_func = nib.load(nii_file_path)

# Now `subj_data_func` is a NIfTI image object, and you can check the shape
print("Shape of subj_data_func:", subj_data_func.shape)

# Fitting FirstLevelModel to Subject Data
print("Fitting FirstLevelModel to Subject Data...")
fmri_glm = fmri_glm.fit(subj_data_func, events)

# Define conditions and contrasts
design_matrix = fmri_glm.design_matrices_[0]
num_conditions = design_matrix.shape[1]
print('Number of conditions in the design matrix:', num_conditions)

conditions = {"control": np.zeros(num_conditions), "interference": np.zeros(num_conditions)}
conditions["interference"][1] = 1  # Adjust based on your actual condition indices
conditions["control"][0] = 1  # Adjust based on your actual condition indices
inter_minus_con = conditions["interference"] - conditions["control"]

# Compute contrast
try:
    z_map = fmri_glm.compute_contrast(inter_minus_con, output_type='z_score')
    print("Ran compute_contrast()")
except Exception as e:
    print("Could not run compute_contrast()")
    print(e)
    sys.exit(1)

# User-defined threshold for binarization
zThresh = 1
while True:
    choseThr = input(f"Threshold Binary Mask at Z-score of {zThresh}? (y/n): ")
    if choseThr == "y":
        print(f"Ok, Mask will include voxels with a Z-score of {zThresh} or higher.")
        break
    elif choseThr == "n":
        while True:
            try:
                zThresh = float(input("Please enter a new Z-score threshold: "))
                print(f"Mask will include voxels with a Z-score of {zThresh} or higher.")
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

# Binarizing Z-map
z_map_binarized = z_map.get_fdata() > zThresh
plt.imshow(z_map_binarized[0, :, :], cmap='gray')
plt.title('Binarized Z-map')
plt.show()

# Save results
output_z_map_path = f"/data/results/{pid}_z_map.nii.gz"
nib.save(nib.Nifti1Image(z_map_binarized.astype(np.float32), z_map.affine), output_z_map_path)
print(f"Binarized Z-map saved to: {output_z_map_path}")
