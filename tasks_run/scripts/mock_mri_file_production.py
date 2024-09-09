import os
import sys

import settings
import shutil
from datetime import datetime, timedelta
import time

print("This Script Transfers Files from a DICOM Directory to another directory in order to Imitate the MRI's Production of DICOMS")
print("This Script Runs Locally, Not on Docker. What Filesystem is this script being run on? ")
path_to_samba: str = ""  # initialize
while True:
    print("(1) Meghan's Computer")
    print("(2) Sofia's Computer")
    which_comp: str = input("Which Computer Is Being Used? (1/2): ")
    if not which_comp == "1" and not which_comp == "2":
        print("Please Enter Either 1 or 2")

    else:
        if which_comp == "1":
            path_to_samba: str = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/sambashare"

        elif which_comp == "2":
            # Sofia: Add your path below (assign to path_to_samba)
            print("Hi Sofia! To Use this Script:\n (1) add your path to your sambashare dir (see notes in script) to variable 'path_to_samba' \n (2) re-run script")
            path_to_samba: str = "path/to/sofias/samba/dir"
            # once you put the path above, delete sys.exit(1)
            sys.exit(1)
    break

print("\n Which DICOM Dir Would You Like To Use? ")
dir_list: list = []
tuple_list: list = []
for element in os.listdir(path_to_samba):
    element_path: str = os.path.join(path_to_samba, element)
    if os.path.isdir(element_path):
        dir_list.append(element_path)

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

for file in os.listdir(input_dicom_dir):
    start_time: datetime = datetime.now()

    file_path: str = os.path.join(input_dicom_dir, file)
    shutil.copy(file_path, output_dicom_dir)

    file_copied_time: datetime = datetime.now()
    total_copied_time: timedelta = file_copied_time - start_time
    total_seconds = total_copied_time.total_seconds()
    print(f"File: {file_path} Copied in {total_seconds} seconds")

    repetition_time: timedelta = timedelta(seconds=1.06)
    if total_copied_time >= repetition_time:
        print("UNUSUALLY LONG COPY TIME. CHECK NETWORK ISSUES OR CPU ISSUES.")
    else:
        wait_time = repetition_time - total_copied_time
        print(f"Waiting {wait_time} seconds")
        time.sleep(wait_time.total_seconds())