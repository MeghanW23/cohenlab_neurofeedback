import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings
import time
import stat

def get_permissions(dicom_path): 
    while True:
        try:
            # Get the file's mode  using os.stat
            file_mode = os.stat(dicom_path).st_mode
            if stat.S_IMODE(file_mode) == 0o777:
                print("Correct Permissions Set. ")
                return 
            else:
                print("Permissions Not Yet Set. ")
                time.sleep(0.1) # wait until new permissions are added 
        except FileNotFoundError:
            print(f"The DICOM Could not be found.")

print("Waiting for a New DICOM Dir...")
starting_dir_count = len(os.listdir(settings.LOCAL_SAMBASHARE_DIR_PATH))
print(f"Current Number of Directories: {starting_dir_count}")

dcm_dir = ""
while True:
    current_dir_count = len(os.listdir(settings.LOCAL_SAMBASHARE_DIR_PATH))
    if current_dir_count != starting_dir_count:
        print("New DICOM Directory Detected. Getting the DICOM Dir ...")
        time.sleep(1) # wait for the set_permissions script to set correct permissions 

        dir_list = []
        for dicom_dir in os.listdir(settings.LOCAL_SAMBASHARE_DIR_PATH):
            full_path_dir = os.path.join(settings.LOCAL_SAMBASHARE_DIR_PATH, dicom_dir)
            dir_list.append(full_path_dir)
            dcm_dir = max(dir_list, key=os.path.getmtime)
        
        print(f"Selected DICOM Directory: {dcm_dir}")

        break
    else:
        print("Waiting for new Directory ...")
        time.sleep(0.1)


print("Reading DICOMS in the Directory ...")
dicoms_found = 0 
starting_dicom_count = len(os.listdir(dcm_dir))
while True: 
    current_dicom_count = len(os.listdir(dcm_dir))
    if current_dicom_count != starting_dicom_count:
        dicoms_found += 1
        starting_dicom_count = current_dicom_count
        print(f"Detected new DICOM. (DICOMs Found: {dicoms_found})")

        dicom_list = []
        for dicom in os.listdir(dcm_dir):
            full_path_dicom = os.path.join(dcm_dir, dicom)
            dicom_list.append(full_path_dicom)
            most_recent_dicom = max(dicom_list, key=os.path.getmtime)
        print("Checking Permissions ...")
        get_permissions(dicom_path=most_recent_dicom)

    else:
        print("Waiting for new DICOMs...")
        time.sleep(0.1)

