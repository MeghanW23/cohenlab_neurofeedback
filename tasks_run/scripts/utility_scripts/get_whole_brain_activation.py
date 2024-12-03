import pydicom
import numpy as np
import os
def calculate_mean_activation(dicom_files):
    """
    Calculate the mean brain activation from a list of DICOM files.
    
    Parameters:
        dicom_files (list of str): List of paths to DICOM files.
        
    Returns:
        float: Mean activation value across all DICOM files.
    """
    all_pixel_values = []
    
    for count, file_path in enumerate(dicom_files, start=1):
        # Read the DICOM file
        ds = pydicom.dcmread(file_path)
        
        # Check if pixel data is present
        if hasattr(ds, 'pixel_array'):
            pixel_array = ds.pixel_array
            all_pixel_values.append(pixel_array.flatten())
            mean_activation = np.mean(pixel_array)
            print(f"Mean Activation for Dicom {count}: {mean_activation}")
        else:
            print(f"Warning: No pixel data found in {file_path}")
    
    # Combine all pixel values into a single array
    all_pixel_values = np.concatenate(all_pixel_values)
    
    # Calculate the mean activation value
    mean_activation = np.mean(all_pixel_values)
    return mean_activation

# Example usage
dicom_dir = "/Users/samba_user/sambashare/see_dicoms/"
if not os.path.isdir(dicom_dir):
    print("Inputted dicom_dir not a valid dir")
    exit
dicom_files: list[str] = [os.path.join(dicom_dir, dicom_file) for dicom_file in os.listdir(dicom_dir) if ".dcm" in dicom_file]

mean_activation = calculate_mean_activation(dicom_files)
print(f"Whole Dir Mean Brain Activation: {mean_activation}")
