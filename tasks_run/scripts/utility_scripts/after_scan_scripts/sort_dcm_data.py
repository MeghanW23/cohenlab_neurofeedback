import shutil 
import os 
import pydicom
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import settings

def get_dicom_path() ->  str:

    dicom_directory: str = ""
    Selecting = True 

    while Selecting:
        dicom_directory: str = input("Please enter the path to the DICOM directory you would like to sort: ")
        
        if not os.path.exists(dicom_directory) or not os.path.isdir(dicom_directory):
            print(f"The inputted path does not exist or is not a directory.")
            Selecting: bool = True 

        else: 
            Selecting: bool = False
            Confirming: bool = True 

            while Confirming:
                confirm_dicom_directory: str = input(f"Inputted DICOM Directory:\n{dicom_directory}\nAccept This Path? (y/n): ")

                if confirm_dicom_directory == "y":
                    print(f"Using Inputted DICOM Directory: {confirm_dicom_directory}")
                    Confirming: bool = False 
                    Selecting: bool = False 
                elif confirm_dicom_directory == "n":
                    Selecting: bool = True 
                    Confirming: bool = False 
                else:
                    print(f"Please Enter 'y' or 'n'")
                    Confirming: bool = True
    
    return dicom_directory

def get_output_parentdir_path() -> str:
    output_directory: str = ""
    Selecting: bool = True 

    while Selecting: 
        output_directory: str = ""
        output_directory: str = input("Please Enter the Path to the Parent Directory You Want to Put the Sorted DICOM Directory in: ")

        if not os.path.exists(output_directory) or not os.path.isdir(output_directory):
            print(f"The inputted path does not exist or is not a directory.")
            Selecting: bool = True 
       
        else: 
            Selecting: bool = False
            Confirming: bool = True 

            while Confirming:
                confirm_output_directory: str = input(f"Inputted Output Directory:\n{output_directory}\nAccept This Path? (y/n): ")
                if confirm_output_directory == "y":
                    print(f"Using Output Directory: {output_directory}")
                    Confirming: bool = False 
                    Selecting: bool = False 
                elif confirm_output_directory == "n":
                    Selecting: bool = True 
                    Confirming: bool = False 
                else:
                    print(f"Please Enter 'y' or 'n'")
                    Confirming: bool = True
    return output_directory

def create_output_directory(dicom_directory: str) -> str:
    output_path: str = os.path.join(output_parentdir_path, f"sorted_{os.path.basename(dicom_directory)}")
    
    # make output directory or get a new name if desired directory already exists 
    while True:

        try: 
            os.makedirs(name=output_path)
            break

        except FileExistsError: 
            print(f"Output Directory for Sorted DICOMs: {output_path} Already Exists.")

            Creating: bool = True

            while Creating: 
                new_filename: str = input(f"Please Enter a New Name for the Output Directory: ")
                new_filename: str = f"{new_filename}_{os.path.basename(dicom_directory)}"

                Accepting: bool = True
                while Accepting: 
                    accept_filename: str = input(f"Accept Filename: '{new_filename}'? (y/n): ")

                    if accept_filename == 'y':
                        output_path: str = os.path.join(output_parentdir_path, new_filename)
                        print(f"Sorted DICOMs will be outputted to: {output_path}")

                        Creating: bool = False
                        Accepting: bool = False 
                    elif accept_filename == 'n':
                        Creating: bool = True
                        Accepting: bool = False 
                    else: 
                        print(f"Please Enter 'y' or 'n'")
                        Accepting: bool = True
    return output_path

# get input paths 
dicom_directory_path: str = get_dicom_path()
output_parentdir_path: str = get_output_parentdir_path()

# create output directory 
output_directory: str = create_output_directory(dicom_directory=dicom_directory_path)

# make list of available MRI sequence names
tags: list[str] = [settings.PRE_MSIT_TASK_METADATA_TAG,
                   settings.POST_MSIT_TASK_METADATA_TAG,
                   settings.PRE_RIFG_TASK_METADATA_TAG,
                   settings.POST_RIFG_TASK_METADATA_TAG,
                   settings.NFB1_TASK_METADATA_TAG,
                   settings.NFB2_TASK_METADATA_TAG,
                   settings.NFB3_TASK_METADATA_TAG,
                   settings.REST1_TASK_METADATA_TAG,
                   settings.REST2_TASK_METADATA_TAG,
                   settings.REST3_TASK_METADATA_TAG,
                   settings.REST4_TASK_METADATA_TAG]
    
# iterate through directory and select out data 
tasks_found = []
for index, dicom_filename in enumerate(sorted(os.listdir(dicom_directory_path)), start=1):
    dicom_path: str = os.path.join(dicom_directory_path, dicom_filename)

    # get task tag metadata
    try:
        dicom_data: pydicom.dataset.FileDataset = pydicom.dcmread(dicom_path)
    except Exception as e:
        print(f"\n\n\nATTENTION: Error reading data from dicom: {dicom_filename}. Skipping...\n\n\n")
    tag: str = dicom_data[settings.TASK_METADATA_TAG].value
    sequence: str = f"{dicom_filename.split('_')[0]}_{dicom_filename.split('_')[1]}"
    output_dirname: str =f"{tag}_{sequence}"

    # check if directory for that task tag exists yet
    tag_directory = os.path.join(output_directory, output_dirname)
    if not os.path.exists(tag_directory):
        tasks_found.append(output_dirname)
        print(f"Making Directory for Task: {output_dirname}")
        os.makedirs(tag_directory)
    
    # copy the DICOM file
    print(f"Moving DICOM: {dicom_filename} to Task Directory: {output_dirname}")
    shutil.copy(src=dicom_path, dst=os.path.join(tag_directory, dicom_filename))
    
# get ending statisics
print("Script is Done.")

print("\nDICOMs Found for Task Tags: ")
for output_dirname in tasks_found: print("     ", output_dirname, f"(Dicom Count: {len(os.listdir(os.path.join(output_directory, output_dirname)))})")

print("\nDICOMs NOT Found for Task Tags: ")
for output_dirname in tags: 
    if not output_dirname in tasks_found:
        print("     ", output_dirname)


