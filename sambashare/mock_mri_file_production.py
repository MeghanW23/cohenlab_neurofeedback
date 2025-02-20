import os
import sys
import shutil
from datetime import datetime, timedelta
import time
import random

print("This Script Transfers Files from a DICOM Directory to another directory in order to Imitate the MRI's Production of DICOMS")
print("This Script Runs Locally, Not on Docker. What Filesystem is this script being run on? ")

path_to_samba: str = os.path.join(os.getcwd())  # initialize
print(f"Path to Dicom Dir Parent Dir: {path_to_samba}")
if not os.path.exists(path_to_samba): print("Path to samba does not exist"); sys.exit(1)

print("\n Which DICOM Dir Would You Like To Use? ")
dir_list: list = []
tuple_list: list = []

for element in os.listdir(path_to_samba):
    if os.path.isdir(os.path.join(path_to_samba, element)):
        dir_list.append(os.path.join(path_to_samba, element))

for index, dcm_dir in enumerate(dir_list, start=1):
    print(f"{index}: {os.path.basename(dcm_dir)}")
    tuple_list.append((str(index), dcm_dir))


while True:
    choose_dcm_dir: str = input("Please Enter the Number Corresponding to the Dir You Would Like To Use: ")
    key_options: list = [tup[0] for tup in tuple_list]
    if choose_dcm_dir not in key_options:
        print("Invalid Choice.")
        print(f"Chose from: {[tup[0] for tup in tuple_list]}")

    else:
        input_dicom_dir: str = tuple_list[int(choose_dcm_dir) - 1][1]
        break

output_dicom_dir: str = os.path.join(os.path.dirname(input_dicom_dir), "test_dir")
if not os.path.exists(output_dicom_dir):
    os.makedirs(output_dicom_dir, exist_ok=True)

print(f"\nOk, Copying DICOMs: \nfrom {input_dicom_dir} \nto {output_dicom_dir}\n")

for file in sorted(os.listdir(input_dicom_dir)):
    start_time: datetime = datetime.now()

    file_path: str = os.path.join(input_dicom_dir, file)
    output_file_path: str = os.path.join(output_dicom_dir, f"{random.randint(1, 100000000000000000000)}.dcm")
    shutil.copy(file_path, output_file_path)

    file_copied_time: datetime = datetime.now()
    total_copied_time: timedelta = file_copied_time - start_time
    total_seconds = total_copied_time.total_seconds()
    print(f"File: {file_path} Copied to {output_file_path}\n in {total_seconds} seconds")

    repetition_time: timedelta = timedelta(seconds=1.06)
    if total_copied_time >= repetition_time:
        print("UNUSUALLY LONG COPY TIME. CHECK NETWORK ISSUES OR CPU ISSUES.")
    else:
        wait_time = repetition_time - total_copied_time
        print(f"Waiting {wait_time} seconds")
        time.sleep(wait_time.total_seconds())
