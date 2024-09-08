import glob
import os
import sys
import settings

def get_most_recent(action: str) -> str:
    if action == "dicom":
        print("got most recent dicom")
    elif action == "dicom_dir":
        print("got most recent dicom dir")
    elif action == "roi_mask":
        print("got most recent roi mask")

    elif action == "txt_output_log":
        parent_dir = settings.LOGGING_DIR_PATH
        # print(f"parent directory: {parent_dir}")

        textfiles: list = glob.glob(os.path.join(parent_dir, "*.txt"))
        # print(f"textfiles: {textfiles}")

        if textfiles is None or textfiles == []:
            print("Could Not Find the most recent Text Output Log")
            sys.exit(1)

        most_recent_txt_file: str = max(textfiles, key=os.path.getmtime)

        return most_recent_txt_file

    else:
        print(f" {action} is not a valid choice for get_most_recent() param: 'action'")

def dicom_to_nifti():
    print("did dicom to nifti")

