import shutil 
import os 
import pydicom
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import FileHandler
import Logger 

Logger.create_log(filetype=".txt", log_name=f"dicom_sorting_log")

dicom_directory: str = ""
while True:
    dicom_directory = input("Please enter the path to the DICOM directory you would like to sort: ")
    
    if not os.path.exists(dicom_directory) or not os.path.isdir(dicom_directory):
        print(f"The inputted path does not exist or is not a directory.")
    else: 
        break 
dicom_directory_filename: str = os.path.basename(dicom_directory)
tasks: list[str] = ["preMSIT",
                    "postMSIT",
                    "preRIFG",
                    "postRIFG", 
                    "NFB1",
                    "NFB2",
                    "NFB3", 
                    "rest1",
                    "rest2",
                    "rest3",
                    "rest4"]
for task in tasks: 
    task_dcm_list: list[str] = FileHandler.get_task_DICOMS(dicom_dir_path=dicom_directory,
                                                           task=task)
    new_directory_filename: str = f"{task}_{dicom_directory_filename}"
    print(new_directory_filename)