import glob
import os
import utility_settings
import sys
from datetime import datetime

def get_most_recent(action: str, log_dir: str = None, dicom_dir: str = None, get_registered_mask: bool = False) -> str:
    if action == "dicom":
        if dicom_dir is None:
            print(f"param 'dicom_dir' must be also used if running get_most_recent(action='dicom')")
            sys.exit(1)

        dicoms: list = glob.glob(os.path.join(dicom_dir, "*.dcm"))
        if dicoms is None or dicoms == []:
            print(f"Could Not Find any dicoms at {dicom_dir}")
            sys.exit(1)

        first_iteration = True
        start_time = datetime.now()
        while True: 
            try: 
                most_recent_dicom: str = max(dicoms, key=os.path.getmtime)
                elapsed_time = datetime.now() - start_time
                print(f"Permissions are set after {elapsed_time}")
                return most_recent_dicom

            except Exception as e:
                if first_iteration:
                    first_iteration = False
                    print(f"Waiting for permissions to be set...")

    elif action == "dicom_dir":

        dirs_in_samba: list = [os.path.join(utility_settings.SAMBASHARE_DIR_PATH, file) for file in os.listdir(utility_settings.SAMBASHARE_DIR_PATH) if os.path.isdir(os.path.join(utility_settings.SAMBASHARE_DIR_PATH, file))]
        print(f"Directories found in {utility_settings.SAMBASHARE_DIR_PATH}: {dirs_in_samba}")
        if dirs_in_samba is None or dirs_in_samba == []:
            print(f"There Are No Dicom Dirs in: {utility_settings.SAMBASHARE_DIR_PATH}")
            sys.exit()

        most_recent_dir: str = max(dirs_in_samba, key=os.path.getmtime)
        return most_recent_dir

    elif action == "roi_mask":
        masks: list = glob.glob(os.path.join(utility_settings.ROI_MASK_DIR_PATH, "*.nii")) + \
                      glob.glob(os.path.join(utility_settings.ROI_MASK_DIR_PATH, "*.nii.gz"))
        if masks is None or masks == []:
            print(f"Could Not Find any masks at {utility_settings.ROI_MASK_DIR_PATH}")
            sys.exit(1)
        
        # get only the masks with the name localized in it 
        if get_registered_mask:
            masks: list = [mask for mask in masks if not "localized" in mask]

        most_recent_mask: str = max(masks, key=os.path.getmtime)

        return most_recent_mask
    
    elif action == "txt_output_log":
        textfiles = []
        if log_dir is None:
            print(f"FileHandler's func get_most_recent() with param 'txt_output_log' requires you input a value for 'log_dir'")
            sys.exit(1)
        if not os.path.exists(log_dir):
            print("Could not find inputted log_dir for FileHandler's func get_most_recent() with param 'txt_output_log'")
            sys.exit(1)
        else:
            textfiles: list = glob.glob(os.path.join(log_dir, "*.txt"))

        if textfiles is None or textfiles == []:
            print(f"Could Not Find any Text Output Logs at the specified directory.")
            print(f"Please Assure you are creating the text output log file before calling Logger.print_and_log() or any function that calls it.")
            sys.exit(1)

        most_recent_txt_file: str = max(textfiles, key=os.path.getmtime)

        return most_recent_txt_file

    elif action == "nifti_in_tmp_dir":
        nii_imgs = [os.path.join(utility_settings.TMP_OUTDIR_PATH, current_img) for current_img in os.listdir(utility_settings.TMP_OUTDIR_PATH) if current_img.endswith(".nii") or current_img.endswith(".nii.gz")]
        most_recent_nifti = max(nii_imgs, key=os.path.getmtime)
        return most_recent_nifti

    elif action == "local_dicom_dir": 
        dirs_in_samba: list = [os.path.join(utility_settings.SAMBASHARE_DIR_PATH, file)
                               for file in os.listdir(utility_settings.SAMBASHARE_DIR_PATH)
                               if os.path.isdir(os.path.join(utility_settings.SAMBASHARE_DIR_PATH, file))]
        if dirs_in_samba is None or dirs_in_samba == []:
            print(f"There Are No DICOM Dirs in: {utility_settings.SAMBASHARE_DIR_PATH}")
            sys.exit()

        most_recent_dir: str = max(dirs_in_samba, key=os.path.getmtime)
        return most_recent_dir

    else:
        print(f" {action} is not a valid choice for get_most_recent() param: 'action'")

