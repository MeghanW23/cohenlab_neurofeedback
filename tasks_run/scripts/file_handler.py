import glob
import os
import sys
import settings

def get_most_recent(action: str, dicom_dir: str = None) -> str:
    if action == "dicom":
        if dicom_dir is None:
            print(f"param 'dicom_dir' must be also used if running get_most_recent(action='dicom')")
            sys.exit(1)

        dicoms: list = glob.glob(os.path.join(dicom_dir, "*.dcm"))
        if dicoms is None or dicoms == []:
            print(f"Could Not Find any dicoms at {dicom_dir}")
            sys.exit(1)

        most_recent_dicom: str = max(dicoms, key=os.path.getmtime)

        return most_recent_dicom

    elif action == "dicom_dir":
        most_recent_dir = None

        for file in os.listdir(settings.SAMBASHARE_DIR_PATH):
            file_path = os.path.join(settings.SAMBASHARE_DIR_PATH, file)

            # Check if this is the most recent modified file
            if os.path.getmtime(file_path) > os.path.getmtime(most_recent_dir):
                most_recent_dir = file_path

        if not most_recent_dir:
            print(f"Could not find any dirs at {settings.SAMBASHARE_DIR_PATH}")
            sys.exit(1)

        return most_recent_dir

    elif action == "roi_mask":
        masks: list = glob.glob(os.path.join(settings.ROI_MASK_DIR_PATH, "*.nii"))
        if masks is None or masks == []:
            print(f"Could Not Find any masks at {settings.ROI_MASK_DIR_PATH}")
            sys.exit(1)

        most_recent_mask: str = max(masks, key=os.path.getmtime)

        return most_recent_mask

    elif action == "txt_output_log":
        textfiles: list = glob.glob(os.path.join(settings.LOGGING_DIR_PATH, "*.txt"))
        if textfiles is None or textfiles == []:
            print(f"Could Not Find any Text Output Logs at {settings.LOGGING_DIR_PATH}")
            sys.exit(1)

        most_recent_txt_file: str = max(textfiles, key=os.path.getmtime)

        return most_recent_txt_file

    else:
        print(f" {action} is not a valid choice for get_most_recent() param: 'action'")

def dicom_to_nifti():
    print("did dicom to nifti")

