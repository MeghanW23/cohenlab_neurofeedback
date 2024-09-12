import os
import shutil
import subprocess

error_dicom_dir: str = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/sambashare/error_testing_dcms/"
list_deleted_files_path: str = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/sambashare/error_testing_dcms/deleted_dicoms.txt"

with open(list_deleted_files_path, 'w') as file_log:
    file_log.write("This File Contains the List of Filenames for Files That Will Cause a dcm2niix Error")

deleted_files: list = []
count: int = 0
for file in sorted(os.listdir(error_dicom_dir)):
    file_path: str = os.path.join(error_dicom_dir, file)
    if "80" in file_path:
        count += 1

        print(file_path)

        deleted_files.append(file_path)

        subprocess.run(['rm', '-f', file_path])
        subprocess.run(['touch', file_path])

        with open(list_deleted_files_path, 'a') as file_log:
            file_log.write(file_path)
        
print(f"total files: {count}")