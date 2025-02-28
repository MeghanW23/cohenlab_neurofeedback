import shutil 
import os 
import pydicom

dicom_directory: str = ""
while True:
    dicom_directory = input("Please enter the path to the DICOM directory you would like to sort: ")
    if not os.path.exists(dicom_directory) or not os.path.isdir(dicom_directory):
        print(f"The inputted path does not exist or is not a directory.")

