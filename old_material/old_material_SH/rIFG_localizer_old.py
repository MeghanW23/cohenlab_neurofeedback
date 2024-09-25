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

def dicom_to_nifti(dicom_dir, output_dir):
    """
    Converts DICOM files to NIfTI format using dcm2niix.
    :param dicom_dir: Directory containing the DICOM files.
    :param output_dir: Directory to save the converted NIfTI files.
    :return: Path to the converted NIfTI file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Run dcm2niix for DICOM to NIfTI conversion
        subprocess.run(['dcm2niix', '-z', 'y', '-o', output_dir, dicom_dir], check=True)
        print(f"Conversion completed. NIfTI files saved to {output_dir}")

        # Search for the converted .nii file in the output directory
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
    try:
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist.")
            return None

        # Get a list of all files in the specified directory
        files_list = [os.path.join(directory, f) for f in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, f))]

        if not files_list:
            print(f"No files found in {directory}.")
            return None

        # Sort files by modification time (newest first)
        sorted_files = sorted(files_list, key=lambda x: os.path.getmtime(x), reverse=True)

        # Return the most recent file
        return sorted_files[0]

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_most_recent_dir(ParentDir):
    try:
        directories = []
        for entry in os.scandir(ParentDir):
            if entry.is_dir():
                directories.append(entry.path)

        if not directories:
            print(f"No subdirectories found in {ParentDir}.")
            return None

            # Looks for the most recently created directory
        latest_directory = max(directories, key=os.path.getctime)
        dicom_dir = os.path.join(ParentDir, latest_directory)
        return dicom_dir
    except Exception as e:
        print("Error in get_most_recent_dir()")
        print(e)
        sys.exit(1)

def get_latest_FuncNii(directory):
    # List comprehension to get all files in the directory that end with '.nii'
    nii_files = [os.path.join(directory, file) for file in os.listdir(directory) if
                 os.path.isfile(os.path.join(directory, file)) and file.endswith('.nii')]

    if not nii_files:
        return None
    # Return the latest modified .dcm file
    return max(nii_files, key=os.path.getmtime)

def is_binary_mask(mask_path):
    # Load the mask image
    mask_img = nib.load(mask_path)
    mask_data = mask_img.get_fdata()

    # Get the unique values in the mask
    unique_values = np.unique(mask_data)

    # Check if the unique values are only 0 and 1
    if np.array_equal(unique_values, [0, 1]):
        return True
    else:
        return False


timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
print(f"Timestamp to be used: {timestamp}")

while True:
    pid = input("Enter Subject ID: ")
    if pid.startswith("P") and len(pid) == 4:
        print(f"Using PID: {pid}")
        break

    elif pid == "test":
        print(f"Using PID: test")
        break

    else:
        print("Invalid Subject ID. Please Make Sure input ID starts with 'P' and includes 3 Numbers")
        print("Ex: P002")
        print("Try Again.")

dicom_parent_dir = "/workdir/tasks_run/data/sambashare/"
output_dir = "/workdir/tasks_run/data/subjects/dcm2niix_outputs"

dicom_dir = get_most_recent_dir(dicom_parent_dir)
subj_data_func = dicom_to_nifti(dicom_dir,output_dir)

if os.path.exists(subj_data_func):
    print(f"Converted DICOMs to NIfTI: {subj_data_func}")
else:
    print("Conversion failed. Could not find NIfTI file.")
    sys.exit(1)

# Event CSV
events = pd.read_table('/workdir/tasks_run/msit_materials/msit_events_with_rest.csv', delimiter=',')
if os.path.exists('/workdir/tasks_run/msit_materials/msit_events_with_rest.csv'):
    print(f"Using MSIT Event CSV at: {events}")
else:
    print(f"Could not find MSIT Event CSV at: {events}")
    sys.exit(1)

fnirtORe3 = ""
subj_data_func = ""
while True:
    fnirtORe3 = input("Did you register using E3 or Fnirt? (e/f): ")
    if fnirtORe3 == 'e':
        print("Ok, You Registered using E3 Script.")
        break
    elif fnirtORe3 == 'f':
        print("Ok, You Registered using Fnirt Script.")
        break
    else:
        print("Please chose either 'e' or 'f'. Try again.")

if fnirtORe3 == 'e':
    # Get 4d Nifti Data
    inputFuncDataParentDir = "/workdir/tasks_run/data/subjects/dcm2niix_outputs"
    if os.path.exists(inputFuncDataParentDir):
        print(f"Getting Input Func Data Directory from this Parent Dir: {inputFuncDataParentDir}")
    else:
        print(f"Couldn't Find Input Func Data from Parent Directory: {inputFuncDataParentDir}")
        sys.exit(1)

    inputFuncDataDir = get_most_recent_dir(inputFuncDataParentDir)
    if os.path.exists(inputFuncDataParentDir):
        print(f"Entering Most Recent Input Func Data Directory: {inputFuncDataDir}")
    else:
        print(f"Couldn't Find Most Recent Input Func Data Directory: {inputFuncDataDir}")
        sys.exit(1)

    try:
        subj_data_func = get_latest_FuncNii(inputFuncDataDir)
    except Exception as e:
        print("Error in get_latest_FuncNii()")
        print(e)
        sys.exit(1)

    if os.path.exists(subj_data_func):
        print("------")
        print(f"Grabbed 4d rIFG Data: {subj_data_func}")
        print("------")

    else:
        print(f"Couldn't Find 4d rIFG Data: {subj_data_func}")
        sys.exit(1)

else:
    inputFuncDataParentDir = "/workdir/tasks_run/data/fnirtDir/"
    if os.path.exists(inputFuncDataParentDir):
        print(f"Getting Input Func Data Directory from this Parent Dir: {inputFuncDataParentDir}")
    else:
        print(f"Couldn't Find Input Func Data from Parent Directory: {inputFuncDataParentDir}")
        sys.exit(1)

    inputFuncDataDir = get_most_recent_dir(inputFuncDataParentDir)
    if os.path.exists(inputFuncDataParentDir):
        print(f"Entering Most Recent Input Func Data Directory: {inputFuncDataDir}")
    else:
        print(f"Couldn't Find Most Recent Input Func Data Directory: {inputFuncDataDir}")
        sys.exit(1)

    try:
        subj_data_func = get_latest_FuncNii(inputFuncDataDir)
    except Exception as e:
        print("Error in get_latest_FuncNii()")
        print(e)
        sys.exit(1)

    if os.path.exists(subj_data_func):
        print("------")
        print(f"Grabbed 4d rIFG Data: {subj_data_func}")
        print("------")

    else:
        print(f"Couldn't Find 4d rIFG Data: {subj_data_func}")
        sys.exit(1)

# Get Registered Subj-Space Mask
MaskDir = f"/workdir/tasks_run/localization_materials/mni_rIFG_mask.nii.gz"
if os.path.exists(MaskDir):
    print(f"Mask Dir is: {MaskDir}")
else:
    print(f"Could Not Find Mask Dir: {MaskDir}")
    sys.exit(1)

rIFG_mask = get_most_recent_mask(MaskDir)
if os.path.exists(rIFG_mask) and rIFG_mask.endswith("nii.gz") or rIFG_mask.endswith(".nii"):
    print("------")
    print(f"Found rIFG Mask: {rIFG_mask}")
    print("------")

elif not rIFG_mask.endswith("nii.gz") or rIFG_mask.endswith(".nii"):
    print("Most Recent File (for rIFG Mask) is rIFGessible, but does not either:")
    print("(1) End with 'nii.gz'")
    print("(2) End with 'nii'")
    sys.exit(1)

else:
    print(f"Could not find rIFG Mask: {rIFG_mask}")
    sys.exit(1)

if is_binary_mask(rIFG_mask):
    print("rIFG Mask is Binary")
else:
    print(f"NOTE: rIFG Mask at {rIFG_mask} is NOT binary")
    print("Binarizing Mask Now ...")
    try:
        rIFG_mask = image.binarize_img(rIFG_mask, threshold=0)
    except Exception as e:
        print("Error Binarizing the rIFG_mask")
        sys.exit(1)


# Skull Strip 4d Data
print("Skull Stripping Data ... ")
try:
    subj_skull_stripped = masking.compute_brain_mask(subj_data_func)
    print(f"Data is Skull Stripped")
except Exception as e:
    print("Error running: masking.compute_brain_mask()")
    sys.exit(1)

print("starting GLM ... ")
fmri_glm = FirstLevelModel(t_r=1.06,
                           standardize=False,
                           signal_scaling=0,
                           smoothing_fwhm=6,
                           hrf_model=None,
                           drift_model='cosine',
                           high_pass=0.01,
                           mask_img=rIFG_mask)
print("Fitting FirstLevelModel to Subject Data ...")
fmri_glm = fmri_glm.fit(subj_data_func, events)

design_matrix = fmri_glm.design_matrices_[0]
num_conditions = design_matrix.shape[1]
print('Number of conditions in the design matrix:', num_conditions)

conditions = {"control": np.zeros(num_conditions), "interference": np.zeros(num_conditions)}
conditions["interference"][1] = 1
conditions["control"][0] = 1
inter_minus_con = conditions["interference"] - conditions["control"]

print("Length of inter_minus_con:", len(inter_minus_con))
print(f"Inter Minus Con: {inter_minus_con}")

try:
    z_map = fmri_glm.compute_contrast(inter_minus_con, output_type='z_score')
    print("Ran compute_contrast()")
except Exception as e:
    print("Could not run compute_contrast()")
    print(e)
    sys.exit(1)

zThresh = 1
while True:
    choseThr = input(f"Threshold Binary Mask at Z-score of {zThresh}? (y/n): ")
    if choseThr == "y":
        print(f"Ok, Mask will include voxels with a Z-score of {zThresh} or higher.")
        break
    elif choseThr == "n":
        while True:
            try:
                zThresh = float(input("Please input desired z-score threshold: "))
                if not 0 <= zThresh <= 4:
                    print("Please Choose a number between 0 - 4, with no non-number characters. Try Again.")
                else:
                    print(f"Ok, Mask will include voxels with a Z-score of {zThresh} or higher.")
                    break
            except ValueError:
                print("Please Choose a number between 0 - 4, with no non-number characters. Try Again.")
        break
    else:
        print("Please Choose either 'y' for Yes or 'n' for No. Try Again.")
try:
    z_mapBin = image.binarize_img(z_map, threshold=zThresh)
    print("Ran binarize_img()")
except Exception as e:
    print("Could Not Run binarize_img()")
    print(e)
    sys.exit(1)

z_mapBinPath = os.path.join(MaskDir, f"{pid}_LocalizedrIFGMaskThr{zThresh}_{timestamp}.nii")
try:
    nib.save(z_mapBin, z_mapBinPath)
    print(f"Localized Mask Saved at: {z_mapBinPath}")
except Exception as e:
    print(f"Could Not Save Final Localized Mask to Path: {z_mapBinPath}")
    print(e)
    sys.exit(1)

if os.path.exists(z_mapBinPath):
    print("Localizer Is Done.")
else:
    print(f"Could Not Find Final Localized Mask at Path: {z_mapBinPath}")

visualize = ""
while True:
    visualize = input("Visualize Results? (y/n): ")
    if visualize == 'y':
        print("Ok. Starting Visualization Process Now ... ")
        break
    elif visualize == 'n':
        print("Ok. Ending Now.")
        break
    else:
        print("Invalid Input. Please press either the 'y' key or the 'n' key. Try Again: ")


if visualize == 'y':
    print("Cutting off first 3d slice from func data...")

    Func3dNii = f"/home/rt/rt-cloud/projects/adhd_rt/localizer3dImgOutdir/{pid}_3d.nii.gz"
    try:
        # fslroi ${Func4dNii} ${Func3dNii} 0 -1 0 -1 0 -1 0 1
        subprocess.run(["fslroi", subj_data_func, Func3dNii, "0", "-1", "0", "-1", "0", "-1", "0", "1"])
    except Exception as e:
        print("Could not cut off 3d frame from 4d data:")
        print(e)
        sys.exit(1)
    if os.path.exists(Func3dNii):
        print("------")
        print("3d Functional Nifti Image Created.")
        print(f"Find at: {Func3dNii}:")
        print("------")
    else:
        print(f"Could not find the 3d nii image: {Func3dNii}")
        sys.exit(1)

    img = nib.load(Func3dNii)
    mask = z_mapBin
    data = img.get_fdata()
    mask_data = mask.get_fdata()

    # Function to display slices with mask overlay
    def show_slices_with_mask(slices, masks):
        fig, axes = plt.subplots(1, len(slices))
        for i, (slice, mask_slice) in enumerate(zip(slices, masks)):
            axes[i].imshow(slice.T, cmap="gray", origin="lower")
            axes[i].imshow(mask_slice.T, cmap="Reds", alpha=0.5, origin="lower")
        plt.show()


    # Select slices from the 3D image and mask
    slice_0 = data[50, :, :]  # sagittal
    mask_0 = mask_data[50, :, :]
    slice_1 = data[:, 50, :]  # coronal
    mask_1 = mask_data[:, 50, :]
    slice_2 = data[:, :, 50]  # axial
    mask_2 = mask_data[:, :, 50]

    # Display the slices with mask overlay
    show_slices_with_mask([slice_0, slice_1, slice_2], [mask_0, mask_1, mask_2])
"""
    # Get the image data as a NumPy array

    image_data = nifti_image.get_fdata()

    # Plot a slice of the image
    slice_index = image_data.shape[2] // 2  # Choose the middle slice

    plt.imshow(image_data[:, :, slice_index], cmap='gray')
    plt.axis('off')  # Turn off axis labels
    plt.title('NIfTI Image Slice')  # Optional: add a title
    plt.show()

"""
