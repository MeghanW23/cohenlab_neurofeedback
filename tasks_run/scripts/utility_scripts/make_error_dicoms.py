import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import settings
from datetime import datetime
import subprocess
import shutil

dir_count = 0
DICOM_dictionary = {}
for DICOM_dir in os.listdir(settings.SAMBASHARE_DIR_PATH):
    if os.path.isdir(os.path.join(settings.SAMBASHARE_DIR_PATH, DICOM_dir)):
        dir_count += 1
        print(f"{dir_count}: {DICOM_dir}")
        DICOM_dictionary[dir_count] = os.path.join(settings.SAMBASHARE_DIR_PATH, DICOM_dir)

input_DICOM_dir = ""
while True:
    DICOM_dir_choice = input(f"Please enter the DICOM directory you would like to base your error-testing DICOM directory off of: ")
    try:
        DICOM_dir_int = int(DICOM_dir_choice)
        if 1 <= DICOM_dir_int <= dir_count:
            input_DICOM_dir = DICOM_dictionary[DICOM_dir_int]
            print(f"Ok, using DICOM dir: {input_DICOM_dir}")
            break
        else:
            print(f"Your choice must be a number between 1 and {dir_count}")
    except Exception as e:
        print(f"Your choice must be a number between 1 and {dir_count}")

# Create error-testing directory
formatted_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
error_DICOM_filename = f"error_testing_DICOMs_{formatted_time}"
error_DICOM_dir_path = os.path.join(settings.SAMBASHARE_DIR_PATH, error_DICOM_filename)
os.makedirs(error_DICOM_dir_path)
print(f"The error testing DICOM directory created at: {error_DICOM_dir_path}")
print("Creating DICOMs Now ...")

divisibility_num = 4
for index, dicom in enumerate(os.listdir(input_DICOM_dir), start=1):
    input_dicom_path = os.path.join(input_DICOM_dir, dicom)
    output_dicom_path = os.path.join(error_DICOM_dir_path, dicom)
    
    if os.path.isfile(input_dicom_path):  # Ensure it's a valid file
        if index % divisibility_num == 0:
            print(f"DICOM {index}: {dicom} will be an EMPTY DICOM")
            subprocess.run(["touch", output_dicom_path])  # create empty dicom file
        else:
            print(f"DICOM {index}: {dicom} will be a REAL")
            shutil.copyfile(input_dicom_path, output_dicom_path)
    else:
        print(f"Skipping non-file entry: {dicom}")

print("Script is done. ")
print(f"The error testing DICOM directory created at: {error_DICOM_dir_path}")
