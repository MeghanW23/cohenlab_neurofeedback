import glob
import os
import sys
import settings
import subprocess
import Logger
from typing import Union, List
import shutil
import time
import ScriptManager
import warnings
import sys
import pydicom
from datetime import datetime

def get_most_recent(action: str, log_dir: str = None, dicom_dir: str = None, get_registered_mask: bool = False) -> str:
    if action == "dicom":
        if dicom_dir is None:
            Logger.print_and_log(f"param 'dicom_dir' must be also used if running get_most_recent(action='dicom')")
            sys.exit(1)

        dicoms: list = glob.glob(os.path.join(dicom_dir, "*.dcm"))
        if dicoms is None or dicoms == []:
            Logger.print_and_log(f"Could Not Find any dicoms at {dicom_dir}")
            sys.exit(1)

        first_iteration = True
        start_time = datetime.now()
        while True: 
            try: 
                most_recent_dicom: str = max(dicoms, key=os.path.getmtime)
                elapsed_time = datetime.now() - start_time
                Logger.print_and_log(f"Permissions are set after {elapsed_time}")
                return most_recent_dicom

            except Exception as e:
                if first_iteration:
                    first_iteration = False
                    Logger.print_and_log(f"Waiting for permissions to be set...")

    elif action == "dicom_dir":

        dirs_in_samba: list = [os.path.join(settings.SAMBASHARE_DIR_PATH, file) for file in os.listdir(settings.SAMBASHARE_DIR_PATH) if os.path.isdir(os.path.join(settings.SAMBASHARE_DIR_PATH, file))]
        Logger.print_and_log(f"Directories found in {settings.SAMBASHARE_DIR_PATH}: {dirs_in_samba}")
        if dirs_in_samba is None or dirs_in_samba == []:
            Logger.print_and_log(f"There Are No Dicom Dirs in: {settings.SAMBASHARE_DIR_PATH}")
            sys.exit()

        most_recent_dir: str = max(dirs_in_samba, key=os.path.getmtime)
        return most_recent_dir

    elif action == "roi_mask":
        masks: list = glob.glob(os.path.join(settings.ROI_MASK_DIR_PATH, "*.nii")) + \
                      glob.glob(os.path.join(settings.ROI_MASK_DIR_PATH, "*.nii.gz"))
        if masks is None or masks == []:
            Logger.print_and_log(f"Could Not Find any masks at {settings.ROI_MASK_DIR_PATH}")
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

    elif action == "csv_output_log":
        if log_dir is None:
            Logger.print_and_log(f"FileHandler's func get_most_recent() with param 'csv_output_log' requires a log_dir value")
            sys.exit(1)
        if not os.path.exists(log_dir):
            Logger.print_and_log(f"Could not find provided log dir: {log_dir}")
            sys.exit(1)

        csv_files: list = glob.glob(os.path.join(log_dir, "*.csv"))
        if csv_files is None or csv_files == []:
            Logger.print_and_log(f"Could not find any CSV log files in: {log_dir}")
            sys.exit(1)

        most_recent_csv_file: str = max(csv_files, key=os.path.getmtime)
        return most_recent_csv_file

    elif action == "nifti_in_tmp_dir":
        nii_imgs = [os.path.join(settings.TMP_OUTDIR_PATH, current_img) for current_img in os.listdir(settings.TMP_OUTDIR_PATH) if current_img.endswith(".nii") or current_img.endswith(".nii.gz")]
        most_recent_nifti = max(nii_imgs, key=os.path.getmtime)
        return most_recent_nifti

    elif action == "local_dicom_dir": 
        dirs_in_samba: list = [os.path.join(settings.SAMBASHARE_DIR_PATH, file) 
                               for file in os.listdir(settings.SAMBASHARE_DIR_PATH) 
                               if os.path.isdir(os.path.join(settings.SAMBASHARE_DIR_PATH, file))]
        if dirs_in_samba is None or dirs_in_samba == []:
            Logger.print_and_log(f"There Are No DICOM Dirs in: {settings.SAMBASHARE_DIR_PATH}")
            sys.exit()

        most_recent_dir: str = max(dirs_in_samba, key=os.path.getmtime)
        return most_recent_dir

    else:
        Logger.print_and_log(f" {action} is not a valid choice for get_most_recent() param: 'action'")

def dicom_to_nifti(dicom_file: str, trial: Union[int, str], preDcm2niixWait: int) -> str:

    time.sleep(preDcm2niixWait)

    result = subprocess.run(['dcm2niix', '-f', f'nii_TR{trial}', '-s', 'y', '-o', settings.TMP_OUTDIR_PATH, dicom_file])

    if result.returncode != 0:
        raise Exception(f"dcm2niix failed with error code {result.returncode}\n"
                        f"stderr: {result.stderr}\n"
                        f"stdout: {result.stdout}")

    nifti_path = os.path.join(settings.TMP_OUTDIR_PATH, f'nii_TR{trial}.nii')
    if not os.path.exists(nifti_path):
        raise Exception("Cannot Find Nifti Image After dcm2niix")

    return nifti_path

def clear_nifti_dir():
    if os.path.exists(settings.TMP_OUTDIR_PATH):
        for item in os.listdir(settings.TMP_OUTDIR_PATH):
            item_path = os.path.join(settings.TMP_OUTDIR_PATH, item)
            if ".gitkeep" in item_path:
                continue  # do not delete gitkeep from tmp_outdir
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    if not len(os.listdir(settings.TMP_OUTDIR_PATH)) == 1:
        warnings.warn(f"Issue Clearing Temp Dir: {settings.TMP_OUTDIR_PATH}")
    else:
        Logger.print_and_log("Nifti Outdir Cleared")

def get_task_DICOMS(dicom_dir_path: str, task: str = None):

    # get metadata from dictionary
    def get_task_metadata_value(tasks_metadata, task_list: List[str]) -> str | List[str]:
        if not isinstance(task_list, list): 
            Logger.print_and_log(f"Arg 'task_list' must be a list.")
            sys.exit(1)
        tag_list: List[str] = []

        for task_name in task_list:
            for key, sub_dict in tasks_metadata.items():
                if task_name in sub_dict:
                    tag_list.append(sub_dict[task_name])
        
        return tag_list
        
       
    # sorted task dict and their metadata 
    tasks_metadata: dict = {
        "msit": {
            "premsit": settings.PRE_MSIT_TASK_METADATA_TAG,
            "postmsit": settings.POST_MSIT_TASK_METADATA_TAG,
        },
        "rifg": {
            "prerifg": settings.PRE_RIFG_TASK_METADATA_TAG,
            "postrifg": settings.POST_RIFG_TASK_METADATA_TAG
        }, 
        "nfb": {
            "nfb1": settings.NFB1_TASK_METADATA_TAG,
            "nfb2": settings.NFB2_TASK_METADATA_TAG,
            "nfb3": settings.NFB3_TASK_METADATA_TAG
        },
        "rest": {
            "rest1": settings.REST1_TASK_METADATA_TAG,
            "rest2": settings.REST2_TASK_METADATA_TAG,
            "rest3": settings.REST3_TASK_METADATA_TAG,
            "rest4": settings.REST4_TASK_METADATA_TAG,
        },
    }

    # verify valid task options
    single_block_data_options = [key for value in tasks_metadata.values() for key in value.keys()]
    multi_block_data_options = [key for key in tasks_metadata.keys()]
    all_task_options =  single_block_data_options + multi_block_data_options
    if not task in all_task_options: 
        Logger.print_and_log(f"Inputted value for argument 'task': '{task}' is not a valid option. Please choose from the following options: \n{all_task_options}")
    
    # verify existing directory 
    if not os.path.isdir(dicom_dir_path):
        Logger.print_and_log(f"The provided path '{dicom_dir_path}' either does not exist or is not a directory.")
        sys.exit(1)
    
    # get metadata tags 
    task_list: List[str] = []
    if task in multi_block_data_options:
        task_list: List[str] = [task_name for task_name in single_block_data_options if task in task_name]
    else: 
        task_list: List[str] = [task]

    tag_list: List[str] = get_task_metadata_value(tasks_metadata=tasks_metadata, task_list=task_list)

    Logger.print_and_log(f"Selecting Data with Tag(s): {tag_list}")
    
    # get task dicoms
    task_dicoms: List[str] = []
    for tag in tag_list: 
        dicom_count = 0
        for dicom in sorted(os.listdir(dicom_dir_path)):

            dicom_path = os.path.join(dicom_dir_path, dicom)
            dicom_data = pydicom.dcmread(dicom_path)

            if dicom_data[settings.TASK_METADATA_TAG].value == tag:
                dicom_count += 1
                Logger.print_and_log(f"Including DICOM: {dicom}, Tag: {tag}")
                task_dicoms.append(dicom_path)
            else:
                Logger.print_and_log(f"Skipping Dicom: {dicom}")
        
        # check if correct DICOM Number\
        Logger.print_and_log(f"{tag} DICOMs found: {dicom_count}")
        if "MSIT" in tag and settings.MSIT_N_DICOMS != dicom_count:
            Logger.print_and_log(f"WARNING: Expected number of DICOMs for task {tag}: {settings.MSIT_N_DICOMS} does not match the number of found DICOMs for this task: {dicom_count}")
        elif "RIFG" in tag and settings.RIFG_N_DICOMS != dicom_count:
            Logger.print_and_log(f"WARNING: Expected number of DICOMs for task: {tag}: {settings.RIFG_N_DICOMS} does not match the number of found DICOMs for this task: {dicom_count}")

    return task_dicoms

class WaitForNoRunningPS:
    def __init__(self, dicom_directory: str):
        self.dicom_directory = dicom_directory

        # get the list pf ps IDs of the dicom directory
        self.starting_ps_ids: List[str] = self.get_ps_ids(path=self.dicom_directory)

        # get the ps id of the most recently created dicom, if it exists, and add to list of starting ps ids
        dicoms_in_dir: List[str] = [os.path.join(self.dicom_directory, dcm) for dcm in os.listdir(self.dicom_directory)]
        if len(dicoms_in_dir) != 0:            
            self.starting_ps_ids.extend(self.get_ps_ids(path=max(dicoms_in_dir, key=os.path.getmtime)))

        print(f"Starting File ps IDs: {self.starting_ps_ids}")


    def get_ps_ids(self, path: str) -> List[str]:
        # do the fuser command and get stout/sterr as a string in 'result' var
        try:
            result:str = subprocess.check_output(f'fuser {path}', 
                                                shell=True, 
                                                text=True,
                                                stderr=subprocess.STDOUT).strip()
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                print(f"No processes using {path}.")
                return []
            # return None if error 
            print(f"ATTENTION: Error checking for PS IDs")
            print(e)

            return [] 
        
        # get the IDs from the printout and convert to list
        ps_ids: str = result.split(':')[1].strip()
        ps_id_list: List[str] = ps_ids.split()
        
        return ps_id_list

    def file_ps_wait(self, dicom_path: str):
        iteration_count = 0 
        
        while True: 
            print(f"Waiting for Full File Transfer...")
            # get the new dicom's ps id list
            dicom_ps_ids: List[str] = self.get_ps_ids(path=dicom_path)

            # if empty list, return
            if dicom_ps_ids == []:
                return 

            # Exit if no new process IDs are found
            if all(ps in self.starting_ps_ids for ps in dicom_ps_ids):
                return

            # count iterations, if theres alot- recheck the dicom directory and the 2nd most recent dicom for new dir-wide or across-dicom processes
            iteration_count += 1
            if iteration_count == 10 or iteration_count == 15: 
                print(f"Re-checking for new across-dicom processes.")
                self.starting_ps_ids: List[str] = self.get_ps_ids(path=self.dicom_directory)

                # check ps ids for most recent dicom before current
                dicoms_in_dir: List[str] = sorted([os.path.join(self.dicom_directory, dcm) for dcm in os.listdir(self.dicom_directory)], key=os.path.getmtime)
                if len(dicoms_in_dir) >= 2:       
                    self.starting_ps_ids.extend(self.get_ps_ids(path=dicoms_in_dir[dicoms_in_dir.index(dicom_path) - 1]))
                print(f"Across-DICOM processes: {self.starting_ps_ids}")
                
            if iteration_count >= 20:
                print(f"Timeout reached. Returning.")
                return 